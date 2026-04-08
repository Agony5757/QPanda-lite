"""BAQIS Quafu (ScQ) quantum cloud platform backend."""

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
import traceback
import warnings
from pathlib import Path

import requests

try:
    import quafu
    from quafu import QuantumCircuit, Task, User
except ImportError:
    quafu = None  # type: ignore[assignment]
    QuantumCircuit = None  # type: ignore[assignment]
    User = None  # type: ignore[assignment]
    Task = None  # type: ignore[assignment]

from qpandalite.originir.originir_line_parser import OriginIR_LineParser
from qpandalite.task.task_utils import load_all_online_info, write_taskinfo

# Initialize default_online_config with a default or dummy value
default_online_config: dict[str, str] = {"default_token": "dummy_token"}
default_token: str = "dummy_token"

# Only attempt to read the config file if we're not generating docs
if os.getenv("SPHINX_DOC_GEN") != "1":
    try:
        with open("quafu_online_config.json", encoding="utf-8") as fp:
            default_online_config = json.load(fp)
    except FileNotFoundError as e:
        raise ImportError(
            "Import quafu backend failed.\n"
            "quafu_online_config.json is not found. "
            "It should be always placed at current working directory (cwd)."
        ) from e
    except Exception as e:
        raise ImportError(
            "Import quafu backend failed.\n" "Unknown import error.\n" f"{traceback.format_exc()}"
        ) from e

    try:
        default_token = default_online_config["default_token"]
    except KeyError as e:
        raise ImportError(
            'Import quafu backend failed.\n'
            'default_online_config.json should have the "default_token" key.'
        ) from e
    except Exception as e:
        raise ImportError(
            f"Import quafu backend failed.\n" f"Unknown import error. Original exception is:\n" f"{str(e)}"
        ) from e


# Valid chip IDs
VALID_CHIP_IDS: frozenset[str] = frozenset(
    {"ScQ-P10", "ScQ-P18", "ScQ-P136", "ScQ-P10C", "Dongling"}
)


class Translation_OriginIR_to_QuafuCircuit(OriginIR_LineParser):  # noqa: N801
    """Translate OriginIR circuits to Quafu ``QuantumCircuit`` objects."""

    @staticmethod
    def reconstruct_qasm(
        qc: QuantumCircuit,
        operation: str | None,
        qubit: int | list[int],
        cbit: int | None,
        parameter: float | list[float] | None,
    ) -> QuantumCircuit:
        """Append a single gate operation to a Quafu ``QuantumCircuit``.

        Args:
            qc: Target circuit to modify in-place.
            operation: Gate name (e.g. ``'H'``, ``'CNOT'``).
            qubit: Target qubit index or list of indices.
            cbit: Classical bit index (for measurements).
            parameter: Rotation parameter for parametric gates.

        Returns:
            The updated circuit.
        """
        if operation == "RX":
            qc.rx(int(qubit), parameter)  # type: ignore[arg-type]
        elif operation == "RY":
            qc.ry(int(qubit), parameter)  # type: ignore[arg-type]
        elif operation == "RZ":
            qc.rz(int(qubit), parameter)  # type: ignore[arg-type]
        elif operation == "H":
            qc.h(int(qubit))  # type: ignore[arg-type]
        elif operation == "X":
            qc.x(int(qubit))  # type: ignore[arg-type]
        elif operation == "CZ":
            qc.cz(int(qubit[0]), int(qubit[1]))  # type: ignore[index]
        elif operation == "CNOT":
            qc.cnot(int(qubit[0]), int(qubit[1]))  # type: ignore[index]
        elif operation == "MEASURE":
            qc.measure([int(qubit)], [int(cbit)])  # type: ignore[list-item]
        elif operation is None or operation == "CREG":
            pass
        else:
            raise RuntimeError(f"Unknown OriginIR operation. Operation: {operation}.")

        return qc

    @staticmethod
    def translate(originir: str) -> QuantumCircuit:
        """Translate a full OriginIR string into a Quafu ``QuantumCircuit``.

        Args:
            originir: An OriginIR circuit string.

        Returns:
            The translated circuit.
        """
        lines = originir.splitlines()
        qc: QuantumCircuit | None = None
        for line in lines:
            operation, qubit, cbit, parameter = OriginIR_LineParser.parse_line(line)
            if operation == "QINIT":
                qc = quafu.QuantumCircuit(int(qubit))  # type: ignore[arg-type]
                continue
            if qc is None:
                raise RuntimeError("QINIT must appear before any gate operation.")
            qc = Translation_OriginIR_to_QuafuCircuit.reconstruct_qasm(
                qc, operation, qubit, cbit, parameter
            )

        if qc is None:
            raise RuntimeError("OriginIR string produced no circuit.")
        return qc


def _submit_task_group(
    circuits: list[str] | None = None,
    task_name: str | None = None,
    chip_id: str | None = None,
    shots: int = 10000,
    auto_mapping: bool = True,
    savepath: Path | str | None = None,
    group_name: str | None = None,
) -> tuple[str | None, list[str]]:
    """Submit a group of circuits to the Quafu platform.

    Returns:
        (group_name, taskid_list)
    """
    if savepath is None:
        savepath = Path.cwd() / "quafu_online_info"
    if not circuits:
        raise ValueError("circuit ??")
    if isinstance(circuits, list):
        user = User(api_token=default_token)  # type: ignore[arg-type]
        user.save_apitoken()
        task = Task()  # type: ignore[arg-type]
        taskid_list: list[str] = []
        for index, c in enumerate(circuits):
            if not isinstance(c, str):
                raise ValueError("Input is not a valid circuit list (a.k.a List[str]).")
            qc = Translation_OriginIR_to_QuafuCircuit.translate(c)
            task.config(backend=chip_id, shots=shots, compile=auto_mapping)

            n_retries = 5
            for i in range(n_retries):
                try:
                    result = task.send(qc, wait=False, name=f"{task_name}-{index}", group=group_name)  # type: ignore[arg-type]
                    break
                except Exception as e:
                    if i != n_retries - 1:
                        print(f"Retry {i + 1} / {n_retries}")
                    raise e
            taskid = result.taskid
            taskid_list.append(taskid)
    return group_name, taskid_list


def submit_task(
    circuit: str | list[str] | None = None,
    task_name: str | None = None,
    chip_id: str | None = None,
    shots: int = 10000,
    auto_mapping: bool = True,
    savepath: Path | str | None = None,
    group_name: str | None = None,
) -> str | list[str]:
    """Submit one or more quantum circuits for execution on the Quafu platform.

    Returns:
        Task ID(s) for the submitted circuit(s).
    """
    if chip_id not in VALID_CHIP_IDS:
        raise RuntimeError(
            r"Invalid chip_id. "
            r"Current quafu chip_id list: "
            r"['ScQ-P10','ScQ-P18','ScQ-P136', 'ScQ-P10C', 'Dongling']"
        )

    if isinstance(circuit, str):
        qc = Translation_OriginIR_to_QuafuCircuit.translate(circuit)

        user = User(api_token=default_token)  # type: ignore[arg-type]
        user.save_apitoken()
        task = Task()  # type: ignore[arg-type]
        task.config(backend=chip_id, shots=shots, compile=auto_mapping)

        n_retries = 5
        for i in range(n_retries):
            try:
                result = task.send(qc, wait=False, name=task_name)  # type: ignore[arg-type]
                break
            except Exception as e:
                if i != n_retries - 1:
                    print(f"Retry {i + 1} / {n_retries}")
                raise e

        taskid: str = result.taskid

        if savepath:
            task_info: dict[str, str | None] = {
                "taskid": taskid,
                "taskname": task_name,
                "backend": chip_id,
            }
            savepath = Path(savepath)
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            with open(savepath / "online_info.txt", "a", encoding="utf-8") as fp:
                fp.write(json.dumps(task_info) + "\n")

    elif isinstance(circuit, list):
        group_name, taskid_list = _submit_task_group(
            circuits=circuit,
            task_name=task_name,
            chip_id=chip_id,
            shots=shots,
            auto_mapping=auto_mapping,
            savepath=savepath,
            group_name=group_name,
        )

        if savepath:
            all_task_info: list[dict[str, str | None]] = []
            for task_id in taskid_list:
                task_info = {
                    "groupname": group_name,
                    "taskid": task_id,
                    "taskname": task_name,
                    "backend": chip_id,
                }
                all_task_info.append(task_info)
            savepath = Path(savepath)
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            with open(savepath / "online_info.txt", "a", encoding="utf-8") as fp:
                for task_info in all_task_info:
                    fp.write(json.dumps(task_info) + "\n")
            taskid = taskid_list  # type: ignore[assignment]
    else:
        raise ValueError("Input is not a valid originir string.")

    return taskid


def query_by_taskid_single(
    taskid: str, savepath: Path | str
) -> str | dict[str, str | int | dict[str, str]]:
    """Query a single task's status from the Quafu platform.

    Returns:
        ``'Running'``, ``'Failed'``, or the full result dict.
    """
    data: dict[str, str] = {"task_id": taskid}
    url = "https://quafu.baqis.ac.cn/qbackend/scq_task_recall/"

    headers: dict[str, str] = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "api_token": default_token,
    }
    res = requests.post(url, headers=headers, data=data)

    res_dict: dict[str, str | int | dict[str, str]] = json.loads(res.text)
    # status {0: "In Queue", 1: "Running", 2: "Completed", "Canceled": 3, 4: "Failed"}

    if res_dict["status"] in (0, 1):  # type: ignore[index]
        return "Running"
    if res_dict["status"] in (3, 4):  # type: ignore[index]
        return "Failed"

    results: dict[str, str | int | dict[str, str]] = res_dict
    savepath = Path(savepath)
    if not os.path.exists(savepath / f"{taskid}.txt"):
        write_taskinfo(taskid, results, savepath)

    return results


def query_by_taskid(
    taskid: str | list[str],
    savepath: Path | str | None = None,
) -> dict[str, str | list[dict[str, str | int | dict[str, str]]]]:
    """Query task status by task ID (non-blocking).

    Returns:
        Aggregated status and results dict.
    """
    if savepath is None:
        savepath = Path.cwd() / "quafu_online_info"
    if not taskid:
        raise ValueError("Task id ??")
    if isinstance(taskid, list):
        taskinfo: dict[str, str | list[dict[str, str | int | dict[str, str]]]] = {
            "status": "success",
            "result": [],
        }
        for taskid_i in taskid:
            taskinfo_i = query_by_taskid_single(taskid_i, savepath)
            if taskinfo_i == "Failed":
                taskinfo["status"] = "failed"  # type: ignore[literal]
                break
            elif taskinfo_i == "Running":
                taskinfo["status"] = "running"  # type: ignore[literal]
            if taskinfo["status"] == "success":
                taskinfo["result"].append(taskinfo_i)  # type: ignore[union-attr]

    elif isinstance(taskid, str):
        taskinfo = query_by_taskid_single(taskid, savepath)  # type: ignore[assignment]
    else:
        raise ValueError("Invalid Taskid")

    return taskinfo  # type: ignore[return-value]


def query_by_taskid_sync(
    taskid: str | list[str],
    interval: float = 2.0,
    timeout: float = 60.0,
    retry: int = 5,
) -> list[dict[str, str | int | dict[str, str]]]:
    """Query task status by task ID (blocking) until completion or timeout.

    Returns:
        Execution results once the task succeeds.
    """
    starttime = time.time()
    while True:
        try:
            now = time.time()
            if now - starttime > timeout:
                raise TimeoutError("Reach the maximum timeout.")
            time.sleep(interval)
            taskinfo = query_by_taskid(taskid)
            if taskinfo["status"] == "running":  # type: ignore[comparison-overlap]
                continue
            if taskinfo["status"] == "success":  # type: ignore[comparison-overlap]
                result = taskinfo["result"]  # type: ignore[union-attr]
                return result
            if taskinfo["status"] == "failed":  # type: ignore[comparison-overlap]
                errorinfo = taskinfo["result"]  # type: ignore[union-attr]
                raise RuntimeError(f"Failed to execute, errorinfo = {errorinfo}")
        except RuntimeError as e:
            if retry > 0:
                retry -= 1
                print(f"Query failed. Retry remains {retry} times.")
            else:
                print("Retry count exhausted.")
                raise e


def query_task_by_group(
    group_name: str,
    history: dict[str, list[str]] | None = None,
    verbose: bool = True,
    savepath: Path | str | None = None,
) -> list:
    """Retrieve all tasks belonging to a named Quafu group.

    Returns:
        A list of Quafu result objects.
    """
    if not group_name:
        raise ValueError("Task id ??")
    if not isinstance(group_name, str):
        raise ValueError("Invalid group name")
    if savepath is None:
        savepath = Path.cwd() / "quafu_online_info"

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
    user = User(api_token=default_token)  # type: ignore[arg-type]
    user.save_apitoken()
    task = Task()  # type: ignore[arg-type]
    group_result = task.retrieve_group(group_name, history, verbose)  # type: ignore[arg-type]
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
    online_info = load_all_online_info(savepath)
    history: dict[str, list[str]] = {}
    for task in online_info:
        if "groupname" in task:
            group = task["groupname"]
            if task["groupname"] not in history:
                history[group] = [task["taskid"]]
            else:
                history[group].append(task["taskid"])
    while True:
        try:
            now = time.time()
            if now - starttime > timeout:
                raise TimeoutError("Reach the maximum timeout.")
            time.sleep(interval)
            group_taskinfo = query_task_by_group(group_name, history, verbose, savepath)
            status = [task.task_status for task in group_taskinfo]
            if len(status) != len(history[group_name]):
                continue
            else:
                return group_taskinfo
        except RuntimeError as e:
            if retry > 0:
                retry -= 1
                print(f"Query failed. Retry remains {retry} times.")
            else:
                print("Retry count exhausted.")
                raise e


def query_all_tasks(
    savepath: Path | str | None = None,
) -> None:
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
