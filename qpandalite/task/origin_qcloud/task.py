"""Origin Quantum Cloud (本源量子云) backend for task submission and querying.

This is the **primary production backend** for QPanda-lite.

All HTTP communication is routed through ``OriginQAdapter`` in the
``adapters`` layer — there are no raw ``requests`` calls in this module.

Configuration is loaded from environment variables (preferred) or from
``originq_cloud_config.json`` (deprecated fallback):

    QPANDA_API_KEY       : API token
    QPANDA_SUBMIT_URL    : Submission endpoint URL
    QPANDA_QUERY_URL     : Query endpoint URL
    QPANDA_TASK_GROUP_SIZE: Max circuits per group (default: 200)

Public API:
    - submit_task     — Submit circuit(s) for execution on OriginQ Cloud.
    - query_by_taskid — Asynchronously query task status by task ID.
    - query_by_taskid_sync — Synchronously query task status (blocking).
    - query_all_tasks — Query all locally recorded tasks.
"""

from __future__ import annotations

__all__ = [
    "submit_task",
    "query_by_taskid",
    "query_by_taskid_sync",
    "query_all_tasks",
    "query_all_task",
]

import time
import warnings
from pathlib import Path
from typing import List, Union

from qpandalite.task.adapters import OriginQAdapter
from qpandalite.task.task_utils import (
    load_all_online_info,
    make_savepath,
    write_taskinfo,
)

# Module-level singleton adapter — initialized on first use.
_adapter: OriginQAdapter | None = None


def _get_adapter() -> OriginQAdapter:
    """Lazily create and cache the OriginQAdapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = OriginQAdapter()
    return _adapter


TASK_STATUS_FAILED = "failed"
TASK_STATUS_SUCCESS = "success"
TASK_STATUS_RUNNING = "running"


def query_by_taskid_single(taskid: str, savepath=None, **kwargs) -> dict:
    """Query a single task's status by task ID (non-blocking).

    Checks local cache first; falls back to adapter query.
    """
    if not taskid:
        raise ValueError("Task id ??")

    savepath = Path(savepath) if savepath else Path.cwd() / "online_info"

    # Check local cache
    if savepath and (savepath / f"{taskid}.txt").exists():
        import json

        with open(savepath / f"{taskid}.txt") as fp:
            return json.load(fp)

    adapter = _get_adapter()
    taskinfo = adapter.query(taskid)

    if savepath and taskinfo["status"] in (TASK_STATUS_SUCCESS, TASK_STATUS_FAILED):
        write_taskinfo(taskid, taskinfo, savepath)

    return taskinfo


def query_by_taskid(
    taskid: Union[List[str], str],
    savepath=None,
    **kwargs,
) -> dict:
    """Query task status by task ID (non-blocking).

    Supports a single task ID or a list. Results are merged; overall
    status reflects the worst case (``failed`` > ``running`` > ``success``).
    """
    if not taskid:
        raise ValueError("Task id ??")

    if isinstance(taskid, list):
        taskinfo: dict = {"status": TASK_STATUS_SUCCESS, "result": []}
        for taskid_i in taskid:
            taskinfo_i = query_by_taskid_single(taskid_i, savepath)
            if taskinfo_i["status"] == TASK_STATUS_FAILED:
                taskinfo["status"] = TASK_STATUS_FAILED
                break
            elif taskinfo_i["status"] == TASK_STATUS_RUNNING:
                taskinfo["status"] = TASK_STATUS_RUNNING
            if taskinfo_i["status"] == TASK_STATUS_SUCCESS:
                if taskinfo["status"] == TASK_STATUS_SUCCESS:
                    taskinfo["result"].extend(taskinfo_i.get("result", []))
        return taskinfo

    elif isinstance(taskid, str):
        return query_by_taskid_single(taskid, savepath)
    else:
        raise ValueError("Invalid Taskid")


def query_by_taskid_sync(
    taskid: Union[List[str], str],
    interval: float = 2.0,
    timeout: float = 60.0,
    retry: int = 5,
    savepath=None,
    **kwargs,
) -> list:
    """Query task status by task ID (blocking) until completion or timeout."""
    adapter = _get_adapter()
    starttime = time.time()

    while True:
        elapsed = time.time() - starttime
        if elapsed > timeout:
            raise TimeoutError("Reach the maximum timeout.")

        time.sleep(interval)

        taskinfo = query_by_taskid(taskid, savepath)

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


def submit_task(
    circuit: Union[str, List[str]],
    task_name: str | None = None,
    tasktype=None,
    chip_id: int = 72,
    shots: int = 1000,
    circuit_optimize: bool = True,
    measurement_amend: bool = False,
    auto_mapping: bool = False,
    specified_block=None,
    savepath=None,
    **kwargs,
) -> str | list[str]:
    """Submit one or more quantum circuits for execution on OriginQ Cloud.

    Args:
        circuit: OriginIR circuit string or list of strings.
        task_name: Human-readable task name.
        tasktype: Reserved (unused).
        chip_id: Target chip ID (default 72).
        shots: Number of measurement shots.
        circuit_optimize: Enable circuit optimization.
        measurement_amend: Enable measurement error mitigation.
        auto_mapping: Enable automatic qubit mapping.
        specified_block: Reserved (unused).
        savepath: Directory for local task records.

    Returns:
        str or list[str]: Task ID(s) assigned by the backend.
    """
    adapter = _get_adapter()
    savepath = Path(savepath) if savepath else Path.cwd() / "online_info"

    if isinstance(circuit, list):
        for c in circuit:
            if not isinstance(c, str):
                raise ValueError(
                    "Input is not a valid circuit list (a.k.a List[str])."
                )
        taskid = adapter.submit_batch(
            circuits=circuit,
            task_name=task_name,
            chip_id=chip_id,
            shots=shots,
            circuit_optimize=circuit_optimize,
            measurement_amend=measurement_amend,
            auto_mapping=auto_mapping,
            **kwargs,
        )
    elif isinstance(circuit, str):
        taskid = adapter.submit(
            circuit=circuit,
            task_name=task_name,
            chip_id=chip_id,
            shots=shots,
            circuit_optimize=circuit_optimize,
            measurement_amend=measurement_amend,
            auto_mapping=auto_mapping,
            **kwargs,
        )
    else:
        raise ValueError(
            "Input must be a str or List[str], "
            "where each str is a valid originir string."
        )

    import json

    ret = {"taskid": taskid, "taskname": task_name}
    if savepath:
        make_savepath(savepath)
        with open(savepath / "online_info.txt", "a") as fp:
            fp.write(json.dumps(ret) + "\n")

    return taskid


def query_all_tasks(savepath=None, **kwargs) -> tuple[int, int]:
    """Query status of all locally recorded tasks."""
    savepath = Path(savepath) if savepath else Path.cwd() / "online_info"

    online_info = load_all_online_info(savepath)
    task_count = len(online_info)
    finished = 0

    for task in online_info:
        taskid = task["taskid"]

        if isinstance(taskid, list):
            status = "finished"
            for taskid_i in taskid:
                if not (savepath / f"{taskid_i}.txt").exists():
                    taskinfo = query_by_taskid(taskid_i)
                    if taskinfo["status"] in (TASK_STATUS_SUCCESS, TASK_STATUS_FAILED):
                        write_taskinfo(taskid_i, taskinfo, savepath)
                    else:
                        status = "unfinished"
            if status == "finished":
                finished += 1

        elif isinstance(taskid, str):
            if not (savepath / f"{taskid}.txt").exists():
                taskinfo = query_by_taskid(taskid)
                if taskinfo["status"] in (TASK_STATUS_SUCCESS, TASK_STATUS_FAILED):
                    write_taskinfo(taskid, taskinfo, savepath)
                    finished += 1
                else:
                    finished += 1
            else:
                finished += 1
        else:
            raise RuntimeError("Invalid Taskid.")

    return finished, task_count


def query_all_task(savepath=None, **kwargs):
    """Deprecated — use :func:`query_all_tasks` instead."""
    warnings.warn(DeprecationWarning("Use query_all_tasks instead"))
    return query_all_tasks(savepath)
