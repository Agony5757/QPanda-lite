"""Quantum cloud backend adapters.

Each adapter provides a consistent interface (submit / query / translate)
for a specific quantum computing provider, encapsulating all network
communication within the adapter layer.
"""

from __future__ import annotations

__all__ = [
    "QuantumAdapter",
    "OriginQAdapter",
    "QuafuAdapter",
    "QiskitAdapter",
    # Constants (re-exported from base for convenience)
    "TASK_STATUS_FAILED",
    "TASK_STATUS_SUCCESS",
    "TASK_STATUS_RUNNING",
]

from qpandalite.task.adapters.base import (
    TASK_STATUS_FAILED,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCESS,
    QuantumAdapter,
)
from qpandalite.task.adapters.originq_adapter import OriginQAdapter
from qpandalite.task.adapters.quafu_adapter import QuafuAdapter
from qpandalite.task.adapters.qiskit_adapter import QiskitAdapter
