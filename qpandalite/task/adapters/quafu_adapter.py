"""Quafu backend adapter.

Translates OriginIR circuits to Quafu QuantumCircuit objects and submits
via the ``quafu`` package (User / Task API).  No raw REST calls.
"""

from __future__ import annotations

__all__ = ["QuafuAdapter"]

from typing import TYPE_CHECKING, Any

from qpandalite.task.adapters.base import (
    TASK_STATUS_FAILED,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCESS,
    QuantumAdapter,
)
from qpandalite.task.config import load_quafu_config

if TYPE_CHECKING:
    import quafu


class QuafuAdapter(QuantumAdapter):
    """Adapter for the BAQIS Quafu (ScQ) quantum cloud platform."""

    name = "quafu"

    # Valid chip IDs
    VALID_CHIP_IDS = frozenset(
        {"ScQ-P10", "ScQ-P18", "ScQ-P136", "ScQ-P10C", "Dongling"}
    )

    @property
    def api_token(self) -> str:
        return self._api_token

    def __init__(self) -> None:
        config = load_quafu_config()
        self._api_token: str = config["api_token"]
        # Internal task history: group_name -> {taskid: task_index}
        # Updated on each submit_batch call so retrieve() can work without
        # requiring the caller to pass history.
        self._task_history: dict[str, dict[str, int]] = {}

        import quafu
        from quafu import QuantumCircuit, Task, User

        self._quafu = quafu
        self._QuantumCircuit = QuantumCircuit
        self._Task = Task
        self._User = User

    def is_available(self) -> bool:
        return self._quafu is not None

    # -------------------------------------------------------------------------
    # Circuit translation
    # -------------------------------------------------------------------------

    def translate_circuit(self, originir: str) -> "QuantumCircuit":
        """Translate an OriginIR string to a Quafu QuantumCircuit."""
        from qpandalite.originir.originir_line_parser import OriginIR_LineParser

        lines = originir.splitlines()
        qc: "QuantumCircuit | None" = None

        for line in lines:
            operation, qubit, cbit, parameter = OriginIR_LineParser.parse_line(line)
            if operation == "QINIT":
                qc = self._QuantumCircuit(int(qubit))  # type: ignore[arg-type]
                continue
            if qc is None:
                raise RuntimeError("QINIT must appear before any gate operation.")
            qc = self._reconstruct_qasm(qc, operation, qubit, cbit, parameter)

        if qc is None:
            raise RuntimeError("OriginIR string produced no circuit.")
        return qc

    def _reconstruct_qasm(
        self,
        qc: "QuantumCircuit",
        operation: str | None,
        qubit: int | list[int],
        cbit: int | None,
        parameter: float | list[float] | None,
    ) -> "QuantumCircuit":
        """Append a single gate to a Quafu QuantumCircuit."""
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
            raise RuntimeError(
                f"Unknown OriginIR operation in quafu adapter: {operation}."
            )
        return qc

    # -------------------------------------------------------------------------
    # Task submission
    # -------------------------------------------------------------------------

    def submit(
        self, circuit: "QuantumCircuit", *, shots: int = 10000, **kwargs: Any
    ) -> str:
        """Submit a single circuit to Quafu."""
        chip_id: str | None = kwargs.get("chip_id")
        auto_mapping: bool = kwargs.get("auto_mapping", True)
        task_name: str | None = kwargs.get("task_name")

        if chip_id not in self.VALID_CHIP_IDS:
            raise RuntimeError(
                r"Invalid chip_id. "
                r"Current quafu chip_id list: "
                r"['ScQ-P10','ScQ-P18','ScQ-P136', 'ScQ-P10C', 'Dongling']"
            )

        user = self._User(api_token=self._api_token)
        user.save_apitoken()
        task = self._Task()
        task.config(backend=chip_id, shots=shots, compile=auto_mapping)

        result = task.send(circuit, wait=False, name=task_name)  # type: ignore[arg-type]
        return result.taskid

    def submit_batch(
        self, circuits: list["QuantumCircuit"], *, shots: int = 10000, **kwargs: Any
    ) -> list[str]:
        """Submit multiple circuits as a group to Quafu."""
        chip_id: str | None = kwargs.get("chip_id")
        auto_mapping: bool = kwargs.get("auto_mapping", True)
        task_name: str | None = kwargs.get("task_name")
        group_name: str | None = kwargs.get("group_name")

        if chip_id not in self.VALID_CHIP_IDS:
            raise RuntimeError(
                r"Invalid chip_id. "
                r"Current quafu chip_id list: "
                r"['ScQ-P10','ScQ-P18','ScQ-P136', 'ScQ-P10C', 'Dongling']"
            )

        user = self._User(api_token=self._api_token)
        user.save_apitoken()
        task = self._Task()
        task.config(backend=chip_id, shots=shots, compile=auto_mapping)

        taskids: list[str] = []
        for index, c in enumerate(circuits):
            result = task.send(
                c, wait=False, name=f"{task_name}-{index}", group=group_name  # type: ignore[arg-type]
            )
            taskids.append(result.taskid)

        # Maintain history so query() can retrieve without caller-supplied history
        if group_name:
            if group_name not in self._task_history:
                self._task_history[group_name] = {}
            for i, taskid in enumerate(taskids):
                self._task_history[group_name][taskid] = i

        return taskids

    # -------------------------------------------------------------------------
    # Task query
    # -------------------------------------------------------------------------

    def query(self, taskid: str) -> dict[str, Any]:
        """Query a single Quafu task's status via SDK ``Task.retrieve()``.

        Uses the internally maintained history dict so the caller does not
        need to pass any additional context.
        """
        user = self._User(api_token=self._api_token)
        user.save_apitoken()
        task = self._Task()

        # Build a minimal history dict: try all known groups.
        # Task.retrieve(taskid, history) will look up the taskid in history.
        for group_name, id_to_idx in self._task_history.items():
            if taskid in id_to_idx:
                result = task.retrieve(taskid, history={group_name: {taskid: id_to_idx[taskid]}})
                return self._result_to_dict(result)

        # Fallback: try without history (may work if server accepts taskid alone)
        result = task.retrieve(taskid)
        return self._result_to_dict(result)

    def _result_to_dict(self, result) -> dict[str, Any]:
        """Convert a quafu ExecResult to the adapter's standard result dict."""
        status_map = {
            "Completed": TASK_STATUS_SUCCESS,
            "Running": TASK_STATUS_RUNNING,
            "In Queue": TASK_STATUS_RUNNING,
            "Failed": TASK_STATUS_FAILED,
            "Canceled": TASK_STATUS_FAILED,
        }
        status_str = result.task_status
        status = status_map.get(status_str, TASK_STATUS_RUNNING)
        if status == TASK_STATUS_SUCCESS:
            return {
                "status": status,
                "result": {
                    "counts": result.counts,
                    "probabilities": result.probabilities,
                },
            }
        return {"status": status}

    def query_batch(self, taskids: list[str]) -> dict[str, Any]:
        """Query multiple Quafu tasks and merge results."""
        taskinfo: dict[str, Any] = {"status": TASK_STATUS_SUCCESS, "result": []}
        for taskid in taskids:
            result_i = self.query(taskid)
            if result_i["status"] == TASK_STATUS_FAILED:
                taskinfo["status"] = TASK_STATUS_FAILED
                break
            elif result_i["status"] == TASK_STATUS_RUNNING:
                taskinfo["status"] = TASK_STATUS_RUNNING
            if taskinfo["status"] == TASK_STATUS_SUCCESS:
                taskinfo["result"].append(result_i.get("result", {}))
        return taskinfo
