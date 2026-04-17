"""Platform-specific result normalizers.

This module provides functions to convert platform-specific result formats
into the unified UnifiedResult format. Each platform (OriginQ, Quafu, IBM)
has its own normalizer that handles the unique output format of that platform.

The normalizers are used by the adapter classes to ensure consistent
result handling across all platforms.

Usage:
    from qpandalite.task.normalizers import normalize_quafu
    from qpandalite.task.result_types import UnifiedResult

    # Convert Quafu result to unified format
    unified = normalize_quafu(quafu_result, task_id="abc123")
"""

from __future__ import annotations

__all__ = ["normalize_originq", "normalize_quafu", "normalize_ibm", "normalize_dummy"]

from typing import Any, Dict, Optional

from .result_types import UnifiedResult


def normalize_originq(
    raw: Dict[str, Any],
    task_id: str,
    shots: int = 1000,
    n_qubits: Optional[int] = None,
) -> UnifiedResult:
    """Normalize OriginQ Cloud result format.

    OriginQ returns results in the format:
        {'key': ['0x0', '0x1', ...], 'value': [0.5, 0.3, ...]}

    where keys are hexadecimal bitstrings and values are probabilities.

    Args:
        raw: Raw result dict from OriginQ Cloud API.
        task_id: Task identifier.
        shots: Number of shots (default 1000).
        n_qubits: Number of qubits. If None, inferred from keys.

    Returns:
        UnifiedResult with normalized probabilities and counts.

    Example:
        >>> raw = {'key': ['0x0', '0x3'], 'value': [0.5, 0.5]}
        >>> result = normalize_originq(raw, "task-1", n_qubits=2)
        >>> print(result.probabilities)
        {'00': 0.5, '11': 0.5}
    """
    keys = raw.get("key", [])
    values = raw.get("value", [])

    if not keys:
        return UnifiedResult.from_probabilities(
            probabilities={},
            shots=shots,
            platform="originq",
            task_id=task_id,
            raw_result=raw,
        )

    # Determine number of qubits if not provided
    if n_qubits is None:
        # Find max bitstring length from hex keys
        max_val = max((int(k, 16) for k in keys), default=0)
        n_qubits = max(1, max_val.bit_length())

    # Convert hex keys to binary bitstrings
    probs: Dict[str, float] = {}
    for hex_key, prob in zip(keys, values):
        try:
            int_val = int(hex_key, 16) if isinstance(hex_key, str) else int(hex_key)
            bin_key = bin(int_val)[2:].zfill(n_qubits)
            probs[bin_key] = float(prob)
        except (ValueError, TypeError):
            continue

    return UnifiedResult.from_probabilities(
        probabilities=probs,
        shots=shots,
        platform="originq",
        task_id=task_id,
        raw_result=raw,
    )


def normalize_quafu(
    result_obj: Any,
    task_id: str,
    backend_name: Optional[str] = None,
) -> UnifiedResult:
    """Normalize Quafu ExecResult format.

    Quafu returns an ExecResult object with attributes:
        - counts: Dict[str, int] measurement counts
        - probabilities: Dict[str, float] measurement probabilities
        - task_status: Status string

    Args:
        result_obj: Quafu ExecResult object.
        task_id: Task identifier.
        backend_name: Optional backend name override.

    Returns:
        UnifiedResult with counts and probabilities.

    Example:
        >>> # result_obj is a quafu ExecResult
        >>> unified = normalize_quafu(result_obj, "task-2")
        >>> print(unified.counts)
        {'00': 512, '11': 488}
    """
    # Extract counts from ExecResult
    counts: Dict[str, int] = {}
    if hasattr(result_obj, "counts") and result_obj.counts is not None:
        counts = dict(result_obj.counts)

    # Try to get backend name from result object
    if backend_name is None and hasattr(result_obj, "task"):
        task_info = getattr(result_obj, "task", {})
        if isinstance(task_info, dict):
            backend_name = task_info.get("backend")

    return UnifiedResult.from_counts(
        counts=counts,
        platform="quafu",
        task_id=task_id,
        backend_name=backend_name,
        raw_result=result_obj,
    )


def normalize_ibm(
    result_obj: Any,
    task_id: str,
) -> UnifiedResult:
    """Normalize IBM Quantum (Qiskit) Result format.

    IBM returns a Qiskit Result object with:
        - get_counts(): Returns dict or list of dicts for measurement counts
        - to_dict(): Returns full result as dict with metadata

    Args:
        result_obj: Qiskit Result object.
        task_id: Task identifier (Qiskit job ID).

    Returns:
        UnifiedResult with counts and probabilities.

    Note:
        For batch jobs, this normalizes the first circuit result only.
        Use result_obj.get_counts() directly for batch results.

    Example:
        >>> # result_obj is a qiskit Result
        >>> unified = normalize_ibm(result_obj, "job-123")
        >>> print(unified.counts)
        {'0x0': 512, '0x3': 488}
    """
    # Get counts from Result object
    counts: Dict[str, int] = {}

    try:
        raw_counts = result_obj.get_counts()
        if isinstance(raw_counts, dict):
            counts = raw_counts
        elif isinstance(raw_counts, list) and len(raw_counts) > 0:
            counts = raw_counts[0] if isinstance(raw_counts[0], dict) else {}
    except (AttributeError, TypeError):
        pass

    # Extract backend name
    backend_name: Optional[str] = None
    try:
        result_dict = result_obj.to_dict()
        backend_name = result_dict.get("backend_name")
    except (AttributeError, TypeError):
        pass

    # Convert hex keys to binary if needed (Qiskit uses hex format)
    normalized_counts: Dict[str, int] = {}
    for key, value in counts.items():
        if isinstance(key, str):
            if key.startswith("0x"):
                # Convert hex to binary
                try:
                    n_qubits = len(key) - 2  # Remove '0x' prefix
                    bin_key = bin(int(key, 16))[2:].zfill(n_qubits * 2)
                    normalized_counts[bin_key] = value
                except ValueError:
                    normalized_counts[key] = value
            else:
                normalized_counts[key] = value
        else:
            normalized_counts[str(key)] = value

    return UnifiedResult.from_counts(
        counts=normalized_counts,
        platform="ibm",
        task_id=task_id,
        backend_name=backend_name,
        raw_result=result_obj,
    )


def normalize_dummy(
    probs_list: list[float],
    task_id: str,
    shots: int = 1000,
) -> UnifiedResult:
    """Normalize local simulator probability output.

    The local OriginIR simulator returns a list of probabilities
    indexed by computational basis state (little-endian).

    Args:
        probs_list: List of probabilities indexed by basis state.
        task_id: Task identifier.
        shots: Number of shots.

    Returns:
        UnifiedResult with probabilities converted to bitstrings.

    Example:
        >>> probs = [0.5, 0.0, 0.0, 0.5]  # |00> and |11> each 50%
        >>> result = normalize_dummy(probs, "task-3")
        >>> print(result.probabilities)
        {'00': 0.5, '11': 0.5}
    """
    n_qubits = len(probs_list).bit_length() - 1
    if n_qubits == 0:
        n_qubits = 1

    probs: Dict[str, float] = {}
    for i, prob in enumerate(probs_list):
        if prob > 0:
            bin_key = bin(i)[2:].zfill(n_qubits)
            probs[bin_key] = prob

    return UnifiedResult.from_probabilities(
        probabilities=probs,
        shots=shots,
        platform="dummy",
        task_id=task_id,
    )