"""OriginQ Cloud backend adapter.

Submits OriginIR circuits to the OriginQ Cloud service using pyqpanda3.

Installation:
    pip install qpandalite[originq]
"""

from __future__ import annotations

__all__ = ["OriginQAdapter"]

import time
import warnings
from typing import Any

from qpandalite.task.adapters.base import (
    TASK_STATUS_FAILED,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCESS,
    QuantumAdapter,
)
from qpandalite.task.config import load_originq_config
from qpandalite.task.optional_deps import require


class OriginQAdapter(QuantumAdapter):
    """Adapter for OriginQ Cloud (本源量子云) using pyqpanda3.

    This adapter uses pyqpanda3's QCloudService API for cloud task submission,
    which simplifies configuration by only requiring an API key.

    Note:
        The pyqpanda3 package is required for this adapter.
        Install with: pip install qpandalite[originq]
    """

    name = "originq"

    def __init__(self) -> None:
        config = load_originq_config()
        self._api_key = config["api_key"]
        self._task_group_size = config.get("task_group_size", 200)
        self._available_qubits = config.get("available_qubits", [])

        # Lazy-loaded pyqpanda3 components
        self._service: Any = None
        self._QCloudOptions: Any = None
        self._QCloudJob: Any = None
        self._JobStatus: Any = None
        self._convert_originir: Any = None

    def _ensure_imports(self) -> None:
        """Lazily import pyqpanda3 modules."""
        if self._service is None:
            pyqpanda3 = require("pyqpanda3", "originq")
            from pyqpanda3.qcloud import QCloudService, QCloudOptions, QCloudJob, JobStatus
            from pyqpanda3.intermediate_compiler import convert_originir_string_to_qprog

            self._service = QCloudService(api_key=self._api_key)
            self._QCloudOptions = QCloudOptions
            self._QCloudJob = QCloudJob
            self._JobStatus = JobStatus
            self._convert_originir = convert_originir_string_to_qprog

    def is_available(self) -> bool:
        """Check if the OriginQ adapter is available (credentials configured).

        Returns:
            bool: True if api_key is configured.
        """
        return bool(self._api_key)

    # -------------------------------------------------------------------------
    # Circuit translation (OriginIR to QProg)
    # -------------------------------------------------------------------------

    def translate_circuit(self, originir: str) -> Any:
        """Convert OriginIR string to QProg using pyqpanda3.

        Args:
            originir: OriginIR format circuit string.

        Returns:
            QProg object for pyqpanda3.
        """
        self._ensure_imports()
        return self._convert_originir(originir)

    # -------------------------------------------------------------------------
    # Task submission
    # -------------------------------------------------------------------------

    def submit(
        self, circuit: str, *, shots: int = 1000, **kwargs: Any
    ) -> str:
        """Submit a single circuit to OriginQ Cloud.

        Args:
            circuit: OriginIR format circuit string.
            shots: Number of measurement shots.
            **kwargs: Additional options:
                - backend_name: Backend name (e.g., 'origin:wuyuan:d5')
                - circuit_optimize: Enable circuit optimization (default: True)
                - measurement_amend: Enable measurement amendment (default: False)
                - auto_mapping: Enable automatic qubit mapping (default: False)

        Returns:
            Task ID string.
        """
        self._ensure_imports()

        backend_name = kwargs.get("backend_name", "origin:wuyuan:d5")
        circuit_optimize = kwargs.get("circuit_optimize", True)
        measurement_amend = kwargs.get("measurement_amend", False)
        auto_mapping = kwargs.get("auto_mapping", False)

        # Get backend
        backend = self._service.backend(backend_name)

        # Convert OriginIR to QProg
        qprog = self.translate_circuit(circuit)

        # Configure options
        options = self._create_options(
            amend=measurement_amend,
            mapping=auto_mapping,
            optimization=circuit_optimize,
        )

        # Submit job
        job = backend.run(qprog, shots=shots, options=options)
        return job.job_id()

    def submit_batch(
        self, circuits: list[str], *, shots: int = 1000, **kwargs: Any
    ) -> str | list[str]:
        """Submit circuits as a group.

        Note: pyqpanda3 handles batch submission internally. This method
        submits circuits sequentially if needed for grouping.

        Args:
            circuits: List of OriginIR format circuit strings.
            shots: Number of measurement shots.
            **kwargs: Additional options (see submit()).

        Returns:
            Single task ID or list of task IDs if split into groups.
        """
        self._ensure_imports()

        backend_name = kwargs.get("backend_name", "origin:wuyuan:d5")
        circuit_optimize = kwargs.get("circuit_optimize", True)
        measurement_amend = kwargs.get("measurement_amend", False)
        auto_mapping = kwargs.get("auto_mapping", False)

        backend = self._service.backend(backend_name)
        options = self._create_options(
            amend=measurement_amend,
            mapping=auto_mapping,
            optimization=circuit_optimize,
        )

        # If circuits fit in one group, submit all together
        if len(circuits) <= self._task_group_size:
            qprogs = [self.translate_circuit(c) for c in circuits]
            job = backend.run(qprogs, shots=shots, options=options)
            return job.job_id()

        # Split into groups
        task_ids: list[str] = []
        for i in range(0, len(circuits), self._task_group_size):
            group = circuits[i:i + self._task_group_size]
            qprogs = [self.translate_circuit(c) for c in group]
            job = backend.run(qprogs, shots=shots, options=options)
            task_ids.append(job.job_id())

        return task_ids

    def _create_options(self, amend: bool, mapping: bool, optimization: bool) -> Any:
        """Create QCloudOptions from adapter parameters.

        Args:
            amend: Enable measurement amendment.
            mapping: Enable automatic qubit mapping.
            optimization: Enable circuit optimization.

        Returns:
            QCloudOptions instance.
        """
        options = self._QCloudOptions()
        options.set_amend(amend)
        options.set_mapping(mapping)
        options.set_optimization(optimization)
        return options

    # -------------------------------------------------------------------------
    # Task query
    # -------------------------------------------------------------------------

    def query(self, taskid: str) -> dict[str, Any]:
        """Query a single task's status.

        Args:
            taskid: Task ID to query.

        Returns:
            dict with keys: taskid, status, result (if completed)
        """
        self._ensure_imports()

        job = self._QCloudJob(taskid)
        status = job.status()

        if status == self._JobStatus.FINISHED:
            result = job.result()
            counts = result.get_counts()
            return {
                "taskid": taskid,
                "status": TASK_STATUS_SUCCESS,
                "result": self._format_counts(counts),
            }
        elif status == self._JobStatus.FAILED:
            return {
                "taskid": taskid,
                "status": TASK_STATUS_FAILED,
                "result": {"error": "Job failed on cloud"},
            }
        else:
            # RUNNING, QUEUING, WAITING
            return {
                "taskid": taskid,
                "status": TASK_STATUS_RUNNING,
            }

    def query_batch(self, taskids: list[str]) -> dict[str, Any]:
        """Query multiple tasks and merge results.

        Args:
            taskids: List of task IDs to query.

        Returns:
            Combined result dict with status and merged results.
        """
        taskinfo: dict[str, Any] = {"status": TASK_STATUS_SUCCESS, "result": []}

        for taskid in taskids:
            result_i = self.query(taskid)

            if result_i["status"] == TASK_STATUS_FAILED:
                taskinfo["status"] = TASK_STATUS_FAILED
                break
            elif result_i["status"] == TASK_STATUS_RUNNING:
                taskinfo["status"] = TASK_STATUS_RUNNING

            if taskinfo["status"] == TASK_STATUS_SUCCESS:
                taskinfo["result"].extend(result_i.get("result", []))

        return taskinfo

    def _format_counts(self, counts: Any) -> list[dict]:
        """Format pyqpanda3 counts to adapter result format.

        Args:
            counts: Counts from QCloudResult.get_counts().

        Returns:
            List of result dicts with 'key' and 'value' keys.
        """
        if isinstance(counts, dict):
            return [{"key": k, "value": v} for k, v in counts.items()]
        elif isinstance(counts, list):
            # Handle list of counts (for batch results)
            results = []
            for c in counts:
                if isinstance(c, dict):
                    results.extend([{"key": k, "value": v} for k, v in c.items()])
            return results
        else:
            return [{"key": str(counts), "value": 1}]

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
        """Poll task status until completion or timeout.

        Args:
            taskid: Task ID or list of task IDs.
            interval: Polling interval in seconds.
            timeout: Maximum wait time in seconds.
            retry: Number of retries on query failure.

        Returns:
            List of result dicts.

        Raises:
            TimeoutError: If timeout is reached.
            RuntimeError: If task fails or retry exhausted.
        """
        taskids = [taskid] if isinstance(taskid, str) else taskid
        starttime = time.time()

        while True:
            elapsed = time.time() - starttime
            if elapsed > timeout:
                raise TimeoutError("Reached the maximum timeout.")

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
