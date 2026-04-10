"""Base adapter interface for quantum cloud backends.

Every backend adapter must implement this interface, providing:
1. Translation from OriginIR string to the provider's native circuit type.
2. Task submission via the provider's Python SDK (not raw REST).
3. Task status query and result retrieval.

The adapter layer replaces all direct ``requests`` REST calls within the
task modules.  Each adapter is a stateful object that holds the provider
session / client and configuration.
"""

from __future__ import annotations

__all__ = ["QuantumAdapter", "TASK_STATUS_FAILED", "TASK_STATUS_SUCCESS", "TASK_STATUS_RUNNING"]

import abc
from enum import Enum
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from qpandalite.circuit_builder.qcircuit import Circuit


TASK_STATUS_FAILED = "failed"
TASK_STATUS_SUCCESS = "success"
TASK_STATUS_RUNNING = "running"


class QuantumAdapter(abc.ABC):
    """Abstract base class for quantum cloud backend adapters.

    Subclass this for each backend (originq_cloud, quafu, ibm, ...).
    Each adapter is instantiated once per task module and reused.
    """

    name: str = "base"

    # -------------------------------------------------------------------------
    # Circuit translation
    # -------------------------------------------------------------------------

    @abc.abstractmethod
    def translate_circuit(self, originir: str) -> Any:
        """Translate an OriginIR circuit string to the provider's native circuit type.

        Args:
            originir: Circuit in OriginIR format.

        Returns:
            Provider-specific circuit object.
        """
        ...

    # -------------------------------------------------------------------------
    # Task submission
    # -------------------------------------------------------------------------

    @abc.abstractmethod
    def submit(self, circuit: Any, *, shots: int = 1000, **kwargs: Any) -> str:
        """Submit a circuit to the backend and return a task ID.

        Args:
            circuit: Provider-native circuit object (result of ``translate_circuit``).
            shots: Number of measurement shots.
            **kwargs: Additional provider-specific parameters
                (e.g. chip_id, auto_mapping, circuit_optimize).

        Returns:
            str: Task ID assigned by the backend.
        """
        ...

    @abc.abstractmethod
    def submit_batch(
        self, circuits: list[Any], *, shots: int = 1000, **kwargs: Any
    ) -> list[str]:
        """Submit multiple circuits as a single batch.

        Args:
            circuits: List of provider-native circuit objects.
            shots: Number of measurement shots.
            **kwargs: Additional provider-specific parameters.

        Returns:
            list[str]: Task IDs (one per circuit), or a single task ID
            if the backend returns a group ID.
        """
        ...

    # -------------------------------------------------------------------------
    # Task query
    # -------------------------------------------------------------------------

    @abc.abstractmethod
    def query(self, taskid: str) -> dict[str, Any]:
        """Query a single task's status and result.

        Args:
            taskid: Task identifier.

        Returns:
            dict with keys:
                - ``status``: ``'success'`` | ``'failed'`` | ``'running'``
                - ``result``: execution result (present when status is ``'success'``
                  or ``'failed'``)
        """
        ...

    @abc.abstractmethod
    def query_batch(self, taskids: list[str]) -> dict[str, Any]:
        """Query multiple tasks' status and merge results.

        Overall status is the worst case:
        ``'failed'`` > ``'running'`` > ``'success'``.

        Args:
            taskids: List of task identifiers.

        Returns:
            dict with keys: ``status``, ``result`` (list of results).
        """
        ...

    # -------------------------------------------------------------------------
    # Utils
    # -------------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if the required packages / credentials are configured.

        Defaults to ``False`` so that subclasses must explicitly opt-in,
        avoiding the risk of an unconfigured adapter incorrectly reporting
        availability.
        """
        return False
