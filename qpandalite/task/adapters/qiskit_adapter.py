"""Qiskit backend adapter.

Translates OriginIR circuits to Qiskit QuantumCircuit objects and submits
via the ``qiskit`` / ``qiskit_ibm_provider`` packages.  No raw REST calls.
"""

from __future__ import annotations

__all__ = ["QiskitAdapter"]

import time
from typing import TYPE_CHECKING, Any

from qpandalite.task.adapters.base import (
    TASK_STATUS_FAILED,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCESS,
    QuantumAdapter,
)
from qpandalite.task.config import load_ibm_config

if TYPE_CHECKING:
    import qiskit
    import qiskit_ibm_provider  # noqa: F401


class QiskitAdapter(QuantumAdapter):
    """Adapter for IBM Quantum backends via Qiskit."""

    name = "ibm"

    def __init__(self) -> None:
        config = load_ibm_config()
        self._api_token: str = config["api_token"]

        import qiskit_ibm_provider

        qiskit_ibm_provider.IBMProvider.save_account(self._api_token)
        self._provider = qiskit_ibm_provider.IBMProvider(instance="ibm-q/open/main")
        self._backends = self._provider.backends()

    def is_available(self) -> bool:
        """Check if the Qiskit adapter is available (IBM provider initialized).

        Returns:
            bool: True if the IBM provider was successfully initialized.
        """
        return self._provider is not None

    # -------------------------------------------------------------------------
    # Circuit translation
    # -------------------------------------------------------------------------

    def translate_circuit(self, originir: str) -> "qiskit.QuantumCircuit":
        """Translate an OriginIR string to a Qiskit QuantumCircuit.

        The conversion path is OriginIR → QASM string → Qiskit QuantumCircuit.
        This is the most compatible route given the current API surface of
        ``qpandalite.circuit_builder.qcircuit`` (which exposes QASM export
        but not a direct Qiskit-native constructor).  An optimised
        direct path can be evaluated in a future iteration if needed.
        """
        import qiskit
        from qpandalite.circuit_builder.qcircuit import Circuit

        circuit = Circuit()
        circuit.load_originir(originir)
        qasm_str = circuit.qasm

        return qiskit.QuantumCircuit.from_qasm_str(qasm_str)

    # -------------------------------------------------------------------------
    # Task submission
    # -------------------------------------------------------------------------

    def submit(
        self, circuit: "qiskit.QuantumCircuit", *, shots: int = 1000, **kwargs: Any
    ) -> str:
        """Submit a single circuit to IBM Quantum."""
        chip_id: str | None = kwargs.get("chip_id")
        auto_mapping: Any = kwargs.get("auto_mapping", False)
        circuit_optimize: bool = kwargs.get("circuit_optimize", True)
        task_name: str | None = kwargs.get("task_name")

        return self._submit_impl(
            circuits=[circuit],
            chip_id=chip_id,
            shots=shots,
            auto_mapping=auto_mapping,
            circuit_optimize=circuit_optimize,
            task_name=task_name,
        )

    def submit_batch(
        self, circuits: list["qiskit.QuantumCircuit"], *, shots: int = 1000, **kwargs: Any
    ) -> str:
        """Submit multiple circuits as a batch. Returns a single job ID."""
        chip_id: str | None = kwargs.get("chip_id")
        auto_mapping: Any = kwargs.get("auto_mapping", False)
        circuit_optimize: bool = kwargs.get("circuit_optimize", True)
        task_name: str | None = kwargs.get("task_name")

        return self._submit_impl(
            circuits=circuits,
            chip_id=chip_id,
            shots=shots,
            auto_mapping=auto_mapping,
            circuit_optimize=circuit_optimize,
            task_name=task_name,
        )

    def _submit_impl(
        self,
        circuits: list["qiskit.QuantumCircuit"],
        *,
        chip_id: str | None,
        shots: int,
        auto_mapping: Any,
        circuit_optimize: bool,
        task_name: str | None,
    ) -> str:
        """Internal implementation shared by submit / submit_batch."""
        import qiskit

        backends_name = [b.name for b in self._backends]
        if chip_id not in backends_name:
            raise ValueError(f"no such chip, should be one of {backends_name}")

        backend = self._provider.get_backend(chip_id)

        max_shots = backend.max_shots
        if shots > max_shots:
            raise ValueError(
                f"maximum shots number exceeded, should less than {max_shots}"
            )

        if circuit_optimize:
            circuits = qiskit.compiler.transpile(
                circuits, backend=backend, optimization_level=3
            )

        if auto_mapping is True:
            circuits = qiskit.compiler.transpile(
                circuits,
                backend=backend,
                layout_method="sabre",
                optimization_level=1,
            )
        elif isinstance(auto_mapping, list):
            circuits = qiskit.compiler.transpile(
                circuits,
                backend=backend,
                initial_layout=auto_mapping,
                optimization_level=1,
            )
        else:
            circuits = qiskit.compiler.transpile(
                circuits, backend=backend, optimization_level=1
            )

        job = qiskit.execute(experiments=circuits, backend=backend, shots=shots)
        return job.job_id()

    # -------------------------------------------------------------------------
    # Task query
    # -------------------------------------------------------------------------

    def query(self, taskid: str) -> dict[str, Any]:
        """Query a single IBM Quantum job's status."""
        job = self._provider.retrieve_job(job_id=taskid)
        status = job.status().name

        if status not in ("DONE",):
            return {"status": status, "value": job.status().value}

        taskinfo = job.result().to_dict()
        results = []
        for single_result in taskinfo["results"]:
            results.append(single_result["data"]["counts"])

        return {
            "status": TASK_STATUS_SUCCESS,
            "result": results,
            "time": taskinfo["date"].strftime("%a %d %b %Y, %I:%M%p"),
            "backend_name": taskinfo["backend_name"],
        }

    def query_batch(self, taskids: list[str]) -> dict[str, Any]:
        """Query multiple IBM Quantum jobs and merge results."""
        taskinfo: dict[str, Any] = {"status": TASK_STATUS_SUCCESS, "result": []}
        for taskid in taskids:
            result_i = self.query(taskid)
            if result_i["status"] in ("ERROR", "CANCELLED"):
                taskinfo["status"] = TASK_STATUS_FAILED
                break
            elif result_i["status"] in (
                "INITIALIZING",
                "QUEUED",
                "VALIDATING",
                "RUNNING",
            ):
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
        starttime = time.time()
        taskids = [taskid] if isinstance(taskid, str) else taskid

        while True:
            elapsed = time.time() - starttime
            if elapsed > timeout:
                raise TimeoutError("Reach the maximum timeout.")

            taskinfo = self.query_batch(taskids)

            if taskinfo["status"] == TASK_STATUS_RUNNING:
                time.sleep(interval)
                continue
            if taskinfo["status"] == TASK_STATUS_SUCCESS:
                return taskinfo["result"]
            if taskinfo["status"] == TASK_STATUS_FAILED:
                raise RuntimeError(
                    f"Failed to execute, errorinfo = {taskinfo.get('result')}"
                )

            # Retry on transient errors
            if retry > 0:
                retry -= 1
                time.sleep(interval)
            else:
                raise RuntimeError("Retry count exhausted.")
