"""Unified result types for all quantum backends.

This module defines a standardized result format that all platform adapters
must convert their outputs to. This ensures consistent handling of results
regardless of which quantum cloud platform was used.

The UnifiedResult dataclass provides:
- Measurement counts and probabilities in a consistent format
- Platform identification and task metadata
- Optional advanced results (expectation values, statevector)
- Raw platform result for debugging

Usage:
    # Create from counts
    result = UnifiedResult.from_counts(
        counts={"00": 512, "11": 488},
        platform="quafu",
        task_id="abc123"
    )

    # Create from probabilities
    result = UnifiedResult.from_probabilities(
        probabilities={"00": 0.512, "11": 0.488},
        shots=1000,
        platform="originq",
        task_id="xyz789"
    )
"""

from __future__ import annotations

__all__ = ["UnifiedResult"]

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class UnifiedResult:
    """Unified quantum execution result format.

    All platform adapters must normalize their output to this format,
    ensuring consistent result handling across different quantum backends.

    Attributes:
        counts: Measurement counts as dict mapping bitstrings to counts.
            Example: {"00": 512, "11": 488}
        probabilities: Measurement probabilities as dict mapping bitstrings to probs.
            Example: {"00": 0.512, "11": 0.488}
        shots: Total number of shots executed.
        platform: Platform identifier ('originq', 'quafu', 'ibm', 'dummy').
        task_id: Unique task identifier from the platform.
        backend_name: Name of the quantum backend/hardware used (optional).
        execution_time: Execution time in seconds (optional).
        raw_result: Original platform result object for debugging (optional).
        error_message: Error message if execution failed (optional).

    Example:
        >>> result = UnifiedResult.from_counts(
        ...     counts={"00": 512, "11": 488},
        ...     platform="quafu",
        ...     task_id="task-123"
        ... )
        >>> print(result.probabilities)
        {'00': 0.512, '11': 0.488}
    """

    counts: Dict[str, int]
    probabilities: Dict[str, float]
    shots: int
    platform: str
    task_id: str
    backend_name: Optional[str] = None
    execution_time: Optional[float] = None
    raw_result: Any = field(default=None, repr=False)
    error_message: Optional[str] = None

    @classmethod
    def from_counts(
        cls,
        counts: Dict[str, int],
        platform: str,
        task_id: str,
        **kwargs: Any,
    ) -> "UnifiedResult":
        """Create UnifiedResult from measurement counts.

        Probabilities are automatically computed from counts.

        Args:
            counts: Dict mapping bitstrings to measurement counts.
            platform: Platform identifier.
            task_id: Task identifier.
            **kwargs: Additional attributes (backend_name, execution_time, etc.).

        Returns:
            UnifiedResult instance with computed probabilities.

        Example:
            >>> result = UnifiedResult.from_counts(
            ...     {"00": 512, "11": 488}, "quafu", "task-1"
            ... )
        """
        total = sum(counts.values())
        if total == 0:
            probabilities = {}
        else:
            probabilities = {k: v / total for k, v in counts.items()}
        return cls(
            counts=counts,
            probabilities=probabilities,
            shots=total,
            platform=platform,
            task_id=task_id,
            **kwargs,
        )

    @classmethod
    def from_probabilities(
        cls,
        probabilities: Dict[str, float],
        shots: int,
        platform: str,
        task_id: str,
        **kwargs: Any,
    ) -> "UnifiedResult":
        """Create UnifiedResult from probability distribution.

        Counts are computed by multiplying probabilities by shots count.

        Args:
            probabilities: Dict mapping bitstrings to probabilities.
            shots: Number of shots used.
            platform: Platform identifier.
            task_id: Task identifier.
            **kwargs: Additional attributes.

        Returns:
            UnifiedResult instance with computed counts.

        Example:
            >>> result = UnifiedResult.from_probabilities(
            ...     {"00": 0.5, "11": 0.5}, 1000, "originq", "task-2"
            ... )
        """
        counts = {k: int(v * shots) for k, v in probabilities.items()}
        return cls(
            counts=counts,
            probabilities=probabilities,
            shots=shots,
            platform=platform,
            task_id=task_id,
            **kwargs,
        )

    def get_expectation(self, observable: str = "Z") -> float:
        """Compute expectation value for a simple observable.

        Currently only supports single-qubit Z expectation value
        computed from the first qubit's measurement results.

        Args:
            observable: Observable type (currently only 'Z' supported).

        Returns:
            Expectation value in range [-1, 1].

        Note:
            This is a simplified implementation. For complex observables,
            use qpandalite.analyzer module.
        """
        if observable != "Z":
            raise NotImplementedError("Only Z observable is currently supported")

        if not self.probabilities:
            return 0.0

        # Compute <Z> for first qubit
        expectation = 0.0
        for bitstring, prob in self.probabilities.items():
            # First bit determines Z expectation for qubit 0
            first_bit = bitstring[-1] if bitstring else "0"
            sign = 1 if first_bit == "0" else -1
            expectation += sign * prob
        return expectation