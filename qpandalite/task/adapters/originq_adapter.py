"""OriginQ Cloud backend adapter.

Submits OriginIR circuits to the OriginQ Cloud service and retrieves
results via the Python-native API (``pyqpanda3`` when available, or the
HTTP REST API as a fallback).  All HTTP communication is encapsulated
in this adapter — no raw ``requests`` calls leak outside.
"""

from __future__ import annotations

__all__ = ["OriginQAdapter"]

import json
import time
import warnings
from typing import Any

import requests

from qpandalite.task.adapters.base import (
    TASK_STATUS_FAILED,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCESS,
    QuantumAdapter,
)
from qpandalite.task.config import load_originq_config

# ---------------------------------------------------------------------------
# HTTP client (encapsulated here, not in platform task modules)
# ---------------------------------------------------------------------------


class _OriginQHttpClient:
    """Lightweight HTTP client for OriginQ Cloud API.

    All REST communication with OriginQ Cloud is routed through this class.
    It is instantiated once per adapter and reused.
    """

    def __init__(
        self,
        api_key: str,
        submit_url: str,
        query_url: str,
        task_group_size: int = 200,
    ) -> None:
        self._api_key = api_key
        self._submit_url = submit_url
        self._query_url = query_url
        self._task_group_size = task_group_size

    def submit(
        self,
        circuits: list[str],
        *,
        task_name: str | None = None,
        chip_id: int = 72,
        shots: int = 1000,
        circuit_optimize: bool = True,
        measurement_amend: bool = False,
        auto_mapping: bool = False,
        compile_only: bool = False,
        # NOTE: ``compile_only`` is accepted for API compatibility but is not
        # forwarded to the OriginQ Cloud API request body.  The server
        # always performs compilation; returning a compiled-but-unexecuted
        # result is not supported by this backend.
        specified_block: Any = None,
        timeout: float = 30.0,
        retry: int = 5,
    ) -> str:
        """Submit circuits to OriginQ Cloud and return a task ID."""
        headers = {
            "origin-language": "en",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "oqcs_auth=" + self._api_key,
        }

        request_body: dict[str, Any] = {
            "apiKey": self._api_key,
            "qmachineType": 5,
            "qprogArr": circuits,
            "taskFrom": 4,  # means it comes from QPanda
            "chipId": chip_id,
            "shot": shots,
            "isAmend": 1 if measurement_amend else 0,
            "mappingFlag": 1 if auto_mapping else 0,
            "circuitOptimization": 1 if circuit_optimize else 0,
            "compileLevel": 3,
        }

        last_error: Exception | None = None
        for attempt in range(retry):
            try:
                response = requests.post(
                    url=self._submit_url,
                    headers=headers,
                    json=request_body,
                    # OriginQ Cloud uses a self-signed certificate — disabling
                    # verification is required for the HTTPS connection to work.
                    verify=False,  # noqa: S501
                    timeout=timeout,
                )
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Error in submit_task. The returned status code is not 200. "
                        f"Response: {response.text}"
                    )
                break
            except Exception as e:  # noqa: BLE001
                last_error = e
                if attempt < retry - 1:
                    warnings.warn(
                        f"submit_task failed (possibly network). "
                        f"Retry remains {retry - attempt - 1} times."
                    )
                    time.sleep(1)
                else:
                    raise RuntimeError(
                        f"submit_task failed after {retry} attempts. "
                        f"Original exception: {e}"
                    ) from e

        response_body = response.json()
        task_id = response_body["obj"]["taskId"]
        return task_id

    def query_single(self, taskid: str, timeout: float = 10.0) -> dict[str, Any]:
        """Query a single task's status and return parsed result."""
        headers = {
            "origin-language": "en",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": "oqcs_auth=" + self._api_key,
        }

        request_body = {"apiKey": self._api_key, "taskId": taskid}

        response = requests.post(
            url=self._query_url,
            headers=headers,
            json=request_body,
            # OriginQ Cloud uses a self-signed certificate — see note above.
            verify=False,  # noqa: S501
            timeout=timeout,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Error in query_by_taskid. The status code is not 200. "
                f"Response: {response.text}"
            )

        import bz2

        if response.content[:2] == b"BZ":
            text = bz2.decompress(response.content).decode("utf-8")
        else:
            text = response.text

        response_body = json.loads(text)

        # API-level error (different from task-level failure)
        if not response_body["success"]:
            message = response_body["message"]
            code = response_body["code"]
            raise Exception(f"query task error: {message} (errcode: {code})")

        result_list = response_body["obj"]
        ret: dict[str, Any] = {"taskid": result_list["taskId"]}

        task_status = result_list["taskStatus"]
        if task_status == "3":
            ret["status"] = TASK_STATUS_SUCCESS
            try:
                task_result = [
                    json.loads(s) for s in result_list["taskResult"]
                ]
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Error parsing task_result: {result_list['taskResult']}"
                ) from e
            ret["result"] = task_result
        elif task_status == "4":
            ret["status"] = TASK_STATUS_FAILED
            ret["result"] = {
                "errcode": result_list["errorDetail"],
                "errinfo": result_list["errorMessage"],
            }
        else:
            ret["status"] = TASK_STATUS_RUNNING

        return ret


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class OriginQAdapter(QuantumAdapter):
    """Adapter for OriginQ Cloud (本源量子云).

    Communication is routed through ``_OriginQHttpClient`` — no raw
    ``requests`` calls in the platform task modules.
    """

    name = "origin_qcloud"

    def __init__(self) -> None:
        config = load_originq_config()
        self._api_key = config["api_key"]
        self._submit_url = config["submit_url"]
        self._query_url = config["query_url"]
        self._task_group_size = config["task_group_size"]
        self._available_qubits = config.get("available_qubits", [])

        self._client = _OriginQHttpClient(
            api_key=self._api_key,
            submit_url=self._submit_url,
            query_url=self._query_url,
            task_group_size=self._task_group_size,
        )

    def is_available(self) -> bool:
        return bool(self._api_key and self._submit_url and self._query_url)

    # -------------------------------------------------------------------------
    # Circuit translation (OriginIR passes through unchanged for origin_qcloud)
    # -------------------------------------------------------------------------

    def translate_circuit(self, originir: str) -> str:
        """OriginQ Cloud accepts OriginIR strings directly."""
        return originir

    # -------------------------------------------------------------------------
    # Task submission
    # -------------------------------------------------------------------------

    def submit(
        self, circuit: str, *, shots: int = 1000, **kwargs: Any
    ) -> str:
        """Submit a single circuit to OriginQ Cloud."""
        return self._client.submit(
            circuits=[circuit],
            shots=shots,
            **kwargs,
        )

    def submit_batch(
        self, circuits: list[str], *, shots: int = 1000, **kwargs: Any
    ) -> str | list[str]:
        """Submit circuits as a group, splitting if needed."""
        if len(circuits) <= self._task_group_size:
            task_name: str | None = kwargs.get("task_name")
            return self._client.submit(
                circuits=circuits,
                task_name=task_name,
                shots=shots,
                **kwargs,
            )

        # Split into subgroups
        groups: list[list[str]] = []
        group: list[str] = []
        for circuit in circuits:
            if len(group) >= self._task_group_size:
                groups.append(group)
                group = []
            group.append(circuit)
        if group:
            groups.append(group)

        task_name_base: str | None = kwargs.get("task_name")
        taskids: list[str] = []
        for i, grp in enumerate(groups):
            taskid = self._client.submit(
                circuits=grp,
                task_name=f"{task_name_base}_{i}" if task_name_base else None,
                shots=shots,
                **kwargs,
            )
            taskids.append(taskid)
        return taskids

    # -------------------------------------------------------------------------
    # Task query
    # -------------------------------------------------------------------------

    def query(self, taskid: str) -> dict[str, Any]:
        """Query a single task's status."""
        return self._client.query_single(taskid)

    def query_batch(self, taskids: list[str]) -> dict[str, Any]:
        """Query multiple tasks and merge results."""
        taskinfo: dict[str, Any] = {"status": TASK_STATUS_SUCCESS, "result": []}
        for taskid in taskids:
            result_i = self._client.query_single(taskid)
            if result_i["status"] == TASK_STATUS_FAILED:
                taskinfo["status"] = TASK_STATUS_FAILED
                break
            elif result_i["status"] == TASK_STATUS_RUNNING:
                taskinfo["status"] = TASK_STATUS_RUNNING
            if taskinfo["status"] == TASK_STATUS_SUCCESS:
                taskinfo["result"].extend(result_i.get("result", []))
        return taskinfo

    # -------------------------------------------------------------------------
    # Synchronous wait
    # -------------------------------------------------------------------------

    def query_sync(
        self,
        taskid: str | list[str],
        interval: float = 2.0,
        timeout: float = 60.0,
        retry: int = 5,
    ) -> list[dict[str, Any]]:
        """Poll task status until completion or timeout."""
        taskids = [taskid] if isinstance(taskid, str) else taskid
        starttime = time.time()

        while True:
            elapsed = time.time() - starttime
            if elapsed > timeout:
                raise TimeoutError("Reach the maximum timeout.")

            time.sleep(interval)

            taskinfo = self.query_batch(taskids)

            if taskinfo["status"] == TASK_STATUS_RUNNING:
                continue
            if taskinfo["status"] == TASK_STATUS_SUCCESS:
                return taskinfo.get("result", [])
            if taskinfo["status"] == TASK_STATUS_FAILED:
                raise RuntimeError(
                    f"Failed to execute, errorinfo = {taskinfo.get('result')}"
                )

            if retry > 0:
                retry -= 1
                warnings.warn(f"Query failed. Retry remains {retry} times.")
            else:
                raise RuntimeError("Retry count exhausted.")
