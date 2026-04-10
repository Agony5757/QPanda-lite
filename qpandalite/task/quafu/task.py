"""BAQIS Quafu (ScQ) quantum cloud platform backend.

All HTTP communication is routed through ``QuafuAdapter`` in the
``adapters`` layer — the raw ``requests.post`` to the Quafu URL has been
removed from this module.

Configuration is loaded from environment variables (preferred) or from
``quafu_online_config.json`` (deprecated fallback):

    QUAFU_API_TOKEN: API token for Quafu

Public API:
    - submit_task           — Submit circuit(s) for execution on Quafu.
    - query_by_taskid       — Asynchronously query task status by task ID.
    - query_by_taskid_sync  — Synchronously query task status (blocking).
    - query_task_by_group   — Retrieve all tasks in a named group.
    - query_all_tasks       — Query all locally recorded tasks.
"""

from __future__ import annotations

__all__ = [
    "Translation_OriginIR_to_QuafuCircuit",
    "submit_task",
    "query_by_taskid",
    "query_by_taskid_sync",
    "query_task_by_group",
    "query_task_by_group_sync",
    "query_all_tasks",
    "query_all_task",
]

import json
import os
import time
import warnings
from pathlib import Path
from typing import Any, Union

from qpandalite.task.adapters import QuafuAdapter
from qpandalite.task.task_utils import load_all_online_info, write_taskinfo

# Module-level singleton adapter
_adapter: QuafuAdapter | None = None


def _get_adapter() -> QuafuAdapter:
    """Lazily create and cache the QuafuAdapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = QuafuAdapter()
    return _adapter


# Re-export the translation class for backwards compatibility
class Translation_OriginIR_to_QuafuCircuit:
    """Translate OriginIR circuits to Quafu QuantumCircuit objects.

    Deprecated: use ``adapter.translate_circuit(originir)`` instead.
    """

    @staticmethod
    def reconstruct_qasm(
        qc,
        operation: str | None,
        qubit: int | list[int],
        cbit: int | None,
        parameter: float | list[float] | None,
    ):
        adapter = _get_adapter()
        return adapter._reconstruct_qasm(qc, operation, qubit, cbit, parameter)

    @staticmethod
    def translate(originir: str):
        adapter = _get_adapter()
        return adapter.translate_circuit(originir)


# ---------------------------------------------------------------------------
# Task submission
# ---------------------------------------------------------------------------


def submit_task(
    circuit: str | list[str] | None = None,
    task_name: str | None = None,
    chip_id: str | None = None,
    shots: int = 10000,
    auto_mapping: bool = True,
    savepath: Path | str | None = None,
    group_name: str | None = None,
    **kwargs,
) -> str | list[str]:
    """Submit one or more quantum circuits for execution on the Quafu platform.

    Args:
        circuit: OriginIR circuit string or list of strings.
        task_name: Human-readable task name.
        chip_id: Target chip ID (e.g. ``'ScQ-P10'``).
        shots: Number of measurement shots.
        auto_mapping: Whether to enable automatic qubit mapping / compilation.
        savepath: Directory for local task records.
        group_name: Optional group name for batch submissions.

    Returns:
        str or list[str]: Task ID(s) for the submitted circuit(s).
    """
    adapter = _get_adapter()
    savepath = Path(savepath) if savepath else Path.cwd() / "quafu_online_info"

    if isinstance(circuit, str):
        qc = adapter.translate_circuit(circuit)
        taskid = adapter.submit(
            circuit=qc,
            shots=shots,
            chip_id=chip_id,
            auto_mapping=auto_mapping,
            task_name=task_name,
        )

        if savepath:
            _ensure_savepath(savepath)
            task_info: dict[str, Any] = {
                "taskid": taskid,
                "taskname": task_name,
                "backend": chip_id,
            }
            with open(savepath / "online_info.txt", "a", encoding="utf-8") as fp:
                fp.write(json.dumps(task_info) + "\n")

    elif isinstance(circuit, list):
        circuits_qc = [adapter.translate_circuit(c) for c in circuit]
        taskids = adapter.submit_batch(
            circuits=circuits_qc,
            shots=shots,
            chip_id=chip_id,
            auto_mapping=auto_mapping,
            task_name=task_name,
            group_name=group_name,
        )

        if savepath:
            _ensure_savepath(savepath)
            all_task_info: list[dict[str, Any]] = []
            for task_id in taskids:
                task_info = {
                    "groupname": group_name,
                    "taskid": task_id,
                    "taskname": task_name,
                    "backend": chip_id,
                }
                all_task_info.append(task_info)
            with open(savepath / "online_info.txt", "a", encoding="utf-8") as fp:
                for task_info in all_task_info:
                    fp.write(json.dumps(task_info) + "\n")
    else:
        raise ValueError("Input must be a valid originir string or list of strings.")

    return taskid if isinstance(circuit, str) else taskids


def _ensure_savepath(savepath: Path) -> None:
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    if not (savepath / "online_info.txt").exists():
        (savepath / "online_info.txt").touch()


# ---------------------------------------------------------------------------
# Task query
# ---------------------------------------------------------------------------


def query_by_taskid_single(
    taskid: str, savepath: Path | str
) -> str | dict[str, Any]:
    """Query a single task's status from the Quafu platform."""
    adapter = _get_adapter()
    result = adapter.query(taskid)
    savepath = Path(savepath)
    if result["status"] in ("Running",):
        return "Running"
    if result["status"] in ("Failed",):
        return "Failed"
    if not os.path.exists(savepath / f"{taskid}.txt"):
        write_taskinfo(taskid, result, savepath)
    return result


def query_by_taskid(
    taskid: str | list[str],
    savepath: Path | str | None = None,
) -> dict[str, Any]:
    """Query task status by task ID (non-blocking)."""
    adapter = _get_adapter()
    savepath = Path(savepath) if savepath else Path.cwd() / "quafu_online_info"

    if not taskid:
        raise ValueError("Task id ??")

    if isinstance(taskid, list):
        taskinfo: dict[str, Any] = {"status": "success", "result": []}
        for taskid_i in taskid:
            taskinfo_i = query_by_taskid_single(taskid_i, savepath)
            if taskinfo_i == "Failed":
                taskinfo["status"] = "failed"
                break
            elif taskinfo_i == "Running":
                taskinfo["status"] = "running"
            if taskinfo["status"] == "success":
                taskinfo["result"].append(taskinfo_i)
    elif isinstance(taskid, str):
        taskinfo = query_by_taskid_single(taskid, savepath)
    else:
        raise ValueError("Invalid Taskid")

    return taskinfo


def query_by_taskid_sync(
    taskid: str | list[str],
    interval: float = 2.0,
    timeout: float = 60.0,
    retry: int = 5,
) -> list[dict[str, Any]]:
    """Query task status by task ID (blocking) until completion or timeout."""
    adapter = _get_adapter()
    starttime = time.time()

    while True:
        elapsed = time.time() - starttime
        if elapsed > timeout:
            raise TimeoutError("Reach the maximum timeout.")

        time.sleep(interval)

        taskinfo = query_by_taskid(taskid)
        if taskinfo["status"] == "running":
            continue
        if taskinfo["status"] == "success":
            return taskinfo.get("result", [])
        if taskinfo["status"] == "failed":
            raise RuntimeError(f"Failed to execute, errorinfo = {taskinfo.get('result')}")

        if retry > 0:
            retry -= 1
            print(f"Query failed. Retry remains {retry} times.")
        else:
            print("Retry count exhausted.")
            raise RuntimeError("Retry count exhausted.")


def query_task_by_group(
    group_name: str,
    history: dict[str, list[str]] | None = None,
    verbose: bool = True,
    savepath: Path | str | None = None,
) -> list:
    """Retrieve all tasks belonging to a named Quafu group."""
    if not group_name:
        raise ValueError("Task id ??")
    if not isinstance(group_name, str):
        raise ValueError("Invalid group name")
    if savepath is None:
        savepath = Path.cwd() / "quafu_online_info"

    savepath = Path(savepath)
    if history is None:
        online_info = load_all_online_info(savepath)
        history = {}
        for task in online_info:
            if "groupname" in task:
                group = task["groupname"]
                if task["groupname"] not in history:
                    history[group] = [task["taskid"]]
                else:
                    history[group].append(task["taskid"])

    from quafu import Task, User

    config = _get_adapter().api_token
    user = User(api_token=config)
    user.save_apitoken()
    task = Task()
    group_result = task.retrieve_group(group_name, history, verbose)
    for result in group_result:
        result_dict = dict(result.__dict__)
        del result_dict["transpiled_circuit"]
        write_taskinfo(result.taskid, result_dict, savepath=savepath)
    return group_result


def query_task_by_group_sync(
    group_name: str,
    verbose: bool = True,
    savepath: Path | str | None = None,
    interval: float = 2.0,
    timeout: float = 60.0,
    retry: int = 5,
) -> list:
    """Blocking query for all tasks in a named Quafu group."""
    if savepath is None:
        savepath = Path.cwd() / "quafu_online_info"

    starttime = time.time()
    online_info = load_all_online_info(Path(savepath))
    history: dict[str, list[str]] = {}
    for task in online_info:
        if "groupname" in task:
            group = task["groupname"]
            if task["groupname"] not in history:
                history[group] = [task["taskid"]]
            else:
                history[group].append(task["taskid"])

    while True:
        elapsed = time.time() - starttime
        if elapsed > timeout:
            raise TimeoutError("Reach the maximum timeout.")

        time.sleep(interval)

        group_taskinfo = query_task_by_group(group_name, history, verbose, savepath)
        status = [task.task_status for task in group_taskinfo]
        if len(status) != len(history[group_name]):
            continue
        else:
            return group_taskinfo


def query_all_tasks(savepath: Path | str | None = None) -> None:
    """Query all locally recorded Quafu tasks and cache results."""
    if savepath is None:
        savepath = Path.cwd() / "quafu_online_info"

    online_info = load_all_online_info(savepath)
    for task in online_info:
        taskid = task["taskid"]
        if not os.path.exists(Path(savepath) / f"{taskid}.txt"):
            ret = query_by_taskid(taskid)
            if ret is None:
                continue
            elif ret == "Failed":
                write_taskinfo(taskid, {}, savepath=savepath)
            else:
                write_taskinfo(taskid, ret, savepath=savepath)


def query_all_task(savepath: Path | str | None = None) -> None:
    """Deprecated — use :func:`query_all_tasks` instead."""
    warnings.warn(DeprecationWarning("Use query_all_tasks instead"), stacklevel=2)
    query_all_tasks(savepath)
