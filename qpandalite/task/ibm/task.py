"""IBM Quantum backend for task submission and querying via Qiskit.

Submits quantum circuits (OriginIR -> Qiskit QuantumCircuit) to IBM Quantum
devices using the ``qiskit`` and ``qiskit_ibm_provider`` packages.
No raw REST calls — all communication goes through the qiskit SDK.

Configuration is loaded from environment variables (preferred) or from
``ibm_online_config.json`` (deprecated fallback):

    IBM_TOKEN: IBM Quantum API token

Public API:
    - submit_task      — Submit circuit(s) for execution on IBM Quantum.
    - query_by_taskid  — Query task status by job ID.
    - query_by_taskid_sync — Blocking query with polling.
    - query_all_tasks  — Query all locally recorded tasks.
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

import qiskit
import qiskit_ibm_provider

from qpandalite.task.adapters import QiskitAdapter
from qpandalite.task.config import load_ibm_config
from qpandalite.task.task_utils import (
    load_all_online_info,
    make_savepath,
    write_taskinfo,
)

# ---------------------------------------------------------------------------
# Provider initialization (lazy via _get_adapter)
# ---------------------------------------------------------------------------

_adapter: QiskitAdapter | None = None


def _get_adapter() -> QiskitAdapter:
    """Lazily create and cache the QiskitAdapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = QiskitAdapter()
    return _adapter


# ---------------------------------------------------------------------------
# Task query
# ---------------------------------------------------------------------------


def query_by_taskid_single(taskid: str) -> dict:
    """Query a single IBM Quantum job's status (non-blocking)."""
    if not taskid:
        raise ValueError("Task id ??")
    adapter = _get_adapter()
    return adapter.query(taskid)


def query_by_taskid(
    taskid: Union[List[str], str],
) -> dict:
    """Query task status by job ID (non-blocking).

    Supports a single job ID or a list. Results are aggregated; overall
    status reflects the worst case.
    """
    if not taskid:
        raise ValueError("Task id ??")

    adapter = _get_adapter()

    if isinstance(taskid, list):
        taskinfo: dict = {"status": "success", "result": []}
        for taskid_i in taskid:
            taskinfo_i = adapter.query(taskid_i)
            if taskinfo_i["status"] in ("ERROR", "CANCELLED"):
                taskinfo["status"] = "failed"
                break
            elif taskinfo_i["status"] in (
                "INITIALIZING",
                "QUEUED",
                "VALIDATING",
                "RUNNING",
            ):
                taskinfo["status"] = "running"
            if taskinfo_i["status"] == "success":
                if taskinfo["status"] == "success":
                    taskinfo["result"].extend(taskinfo_i.get("result", []))
    elif isinstance(taskid, str):
        taskinfo = adapter.query(taskid)
    else:
        raise ValueError("Invalid Taskid")

    return taskinfo


def query_by_taskid_sync(
    taskid: Union[List[str], str],
    interval: float = 2.0,
    timeout: float = 60.0,
    retry: int = 5,
) -> list:
    """Query task status by job ID (blocking) until completion or timeout."""
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
            raise RuntimeError(
                f"Failed to execute, errorinfo = {taskinfo.get('result')}"
            )

        if retry > 0:
            retry -= 1
            print(f"Query failed. Retry remains {retry} times.")
        else:
            print("Retry count exhausted.")
            raise RuntimeError("Retry count exhausted.")


# ---------------------------------------------------------------------------
# Task submission
# ---------------------------------------------------------------------------


def _translate_circuit(originir: str) -> qiskit.QuantumCircuit:
    """Convert an OriginIR string to a Qiskit QuantumCircuit."""
    from qpandalite.circuit_builder.qcircuit import Circuit

    circuit = Circuit()
    circuit.load_originir(originir)
    return qiskit.QuantumCircuit.from_qasm_str(circuit.qasm)


def submit_task(
    circuit,
    task_name: str | None = None,
    tasktype=None,
    chip_id: str | None = None,
    shots: int = 1000,
    circuit_optimize: bool = True,
    measurement_amend: bool = False,
    auto_mapping: bool = False,
    specified_block=None,
    savepath=None,
    **kwargs,
) -> str:
    """Submit one or more quantum circuits for execution on IBM Quantum.

    Accepts OriginIR strings, Qiskit QuantumCircuit objects, or QASM strings.
    All circuit types are translated to Qiskit QuantumCircuit internally.

    Args:
        circuit: OriginIR string, Qiskit QuantumCircuit, QASM string, or list.
        task_name: Human-readable task name.
        tasktype: Reserved (unused).
        chip_id: IBM backend name.
        shots: Number of measurement shots.
        circuit_optimize: Enable transpiler optimization (level 3).
        measurement_amend: Reserved (unused).
        auto_mapping: Qubit mapping strategy (True=sabre, list=explicit, False=default).
        specified_block: Reserved (unused).
        savepath: Directory for local task records.

    Returns:
        str: The IBM Quantum job ID.
    """
    import json

    adapter = _get_adapter()
    savepath = Path(savepath) if savepath else Path.cwd() / "online_info"

    # Normalise input to list of Qiskit QuantumCircuit
    new_circuit: list[qiskit.QuantumCircuit] = []

    if isinstance(circuit, list):
        for c in circuit:
            if isinstance(c, str):
                new_circuit.append(_translate_circuit(c))
            elif isinstance(c, qiskit.circuit.QuantumCircuit):
                new_circuit.append(c)
            else:
                raise TypeError(
                    "Each circuit must be an OriginIR string, "
                    "Qiskit QuantumCircuit, or QASM string."
                )
    elif isinstance(circuit, str):
        new_circuit.append(_translate_circuit(circuit))
    elif isinstance(circuit, qiskit.circuit.QuantumCircuit):
        new_circuit.append(circuit)
    else:
        raise TypeError(
            "Circuit must be an OriginIR string, "
            "Qiskit QuantumCircuit, QASM string, or list of these."
        )

    if not all(isinstance(i, qiskit.circuit.QuantumCircuit) for i in new_circuit):
        raise TypeError(
            "All circuits must be Qiskit QuantumCircuit type or valid QASM."
        )

    job_id = adapter.submit_batch(
        circuits=new_circuit,
        shots=shots,
        chip_id=chip_id,
        circuit_optimize=circuit_optimize,
        auto_mapping=auto_mapping,
        task_name=task_name,
    )

    ret = {"taskid": job_id, "taskname": task_name}
    if savepath:
        make_savepath(savepath)
        with open(savepath / "online_info.txt", "a") as fp:
            fp.write(json.dumps(ret) + "\n")

    return job_id


def query_all_tasks(savepath=None) -> tuple[int, int]:
    """Query all locally recorded IBM Quantum tasks and cache results."""
    savepath = Path(savepath) if savepath else Path.cwd() / "online_info"

    online_info = load_all_online_info(savepath)
    task_count = len(online_info)
    finished = 0

    for task in online_info:
        taskid = task["taskid"]
        if not (savepath / f"{taskid}.txt").exists():
            ret = query_by_taskid(taskid).copy()
            write_taskinfo(taskid, ret, savepath=savepath)
            finished += 1
        else:
            finished += 1

    return finished, task_count


def query_all_task(savepath=None) -> tuple[int, int]:
    """Deprecated — use :func:`query_all_tasks` instead."""
    warnings.warn(DeprecationWarning("Use query_all_tasks instead"))
    return query_all_tasks(savepath)
