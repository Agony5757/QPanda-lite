"""Expectation value calculations for quantum measurement results."""

__all__ = ["calculate_expectation", "calculate_exp_X", "calculate_exp_Y", "calculate_multi_basis_expectation"]

from typing import Dict, List, Optional, Union

import numpy as np


def _calculate_expectation_dict(
    measured_result: Dict[str, float],
    h: str,
    nqubit: int,
) -> float:
    exp = 0.0
    for result in measured_result:
        if len(result) != nqubit:
            raise ValueError(
                "The Hamiltonian must have the same size with the measured result."
            )
        p = measured_result[result]
        for i in range(nqubit):
            if (h[i] == "Z" or h[i] == "z") and result[i] == "1":
                p *= -1
        exp += p
    return exp


def _calculate_expectation_list(
    measured_result: List[float],
    h: str,
    nqubit: int,
) -> float:
    exp = 0.0
    if len(measured_result) != 2**nqubit:
        raise ValueError(
            "The Hamiltonian must have the same size with the measured result."
        )
    for j, p in enumerate(measured_result):
        for i in range(nqubit):
            if (h[i] == "Z" or h[i] == "z") and ((j >> (nqubit - i - 1)) & 1):
                p *= -1
        exp += p
    return exp


def calculate_expectation(
    measured_result: Union[Dict[str, float], List[float]],
    hamiltonian: Union[List[str], str],
) -> Union[float, List[float]]:
    """Calculate expectation value of a Hamiltonian from measurement results.

    The Hamiltonian may contain only Z and I (identity) terms. This function
    works with results measured in the Z basis. For X or Y basis expectations,
    use :func:`calculate_exp_X` or :func:`calculate_exp_Y` instead.

    Args:
        measured_result: Measurement outcomes in either:

            - **key-value dict**: Maps outcome strings (e.g. ``"00"``) to
              probabilities, e.g. ``{"00": 0.5, "11": 0.5}``.
            - **list**: Probability vector in computational-basis order, e.g.
              ``[0.5, 0, 0, 0.5]`` for a 2-qubit system.

        hamiltonian: A Hamiltonian string (e.g. ``"ZZ"``) or a list of such
            strings. Each character must be ``Z``, ``z``, ``I``, or ``i``.
            The length must match the number of qubits.

    Raises:
        ValueError: Hamiltonian contains invalid characters, or its length
            does not match the number of qubits in ``measured_result``.
        TypeError: ``measured_result`` is neither a dict nor a list.

    Returns:
        The expectation value(s). If ``hamiltonian`` is a list, returns a list
        of floats; otherwise a single float.

    Example:
        >>> result = {"00": 0.5, "11": 0.5}
        >>> calculate_expectation(result, "ZZ")   # Bell state |Φ+⟩
        1.0
        >>> calculate_expectation(result, "ZI")
        0.0
        >>> calculate_expectation(result, ["ZZ", "ZI"])
        [1.0, 0.0]

        >>> # Using list format (2 qubits)
        >>> probs = [0.5, 0, 0, 0.5]  # |00⟩ and |11⟩ each with prob 0.5
        >>> calculate_expectation(probs, "ZZ")
        1.0
    """
    if isinstance(hamiltonian, list):
        return [calculate_expectation(measured_result, h) for h in hamiltonian]

    if not isinstance(hamiltonian, str):
        raise ValueError(
            "The Hamiltonian input must be a str (only containing Z or I or z or i)."
        )

    for h_char in hamiltonian:
        if h_char not in ("Z", "z", "I", "i"):
            raise ValueError(
                "The Hamiltonian input must be a str (only containing Z or I or z or i)."
            )

    nqubit = len(hamiltonian)

    if isinstance(measured_result, dict):
        return _calculate_expectation_dict(measured_result, hamiltonian, nqubit)
    elif isinstance(measured_result, list):
        return _calculate_expectation_list(measured_result, hamiltonian, nqubit)
    else:
        raise ValueError("measured_result must be a Dict or a List.")


def calculate_multi_basis_expectation(
    measured_results: Dict[str, Union[Dict[str, float], List[float]]],
    nqubit: int,
) -> Dict[str, float]:
    """Calculate expectation values for multiple measurement bases at once.

    Given measurement results in different bases (X, Y, Z, or custom),
    compute the expectation value for each basis and return them as a dict.

    The user is responsible for performing the correct basis rotation
    on the quantum circuit before measurement. For example:

    - **Z basis**: measure directly (no rotation).
    - **X basis**: apply ``H`` before measurement.
    - **Y basis**: apply ``S^\\dagger H`` before measurement.

    Each basis label maps to a single expectation value for the MSB qubit
    (index 0). For per-qubit expectations, call :func:`calculate_exp_X` /
    :func:`calculate_exp_Y` directly with the desired ``qubit_index``.

    Note:
        For Z-basis entries, this computes ``⟨ZZ...Z⟩`` (the tensor product
        of Z on all qubits), **not** individual ``⟨Z_k⟩``. For per-qubit Z
        expectations, use :func:`calculate_expectation` with Hamiltonians
        like ``"ZI"`` or ``"IZ"``.

    Args:
        measured_results: A dict mapping basis labels to measurement outcomes.
            Each key is a basis name (e.g. ``"X"``, ``"Y"``, ``"Z"``, or
            a custom label like ``"X0Z1"``). Each value is either:

            - **key-value dict**: ``{"00": 0.5, "11": 0.5}``
            - **list**: ``[0.5, 0, 0, 0.5]`` in computational-basis order.

        nqubit: Number of qubits.

    Returns:
        Dict[str, float]: Mapping from basis label to expectation value.
        For Pauli-X bases, :func:`calculate_exp_X` is used; for Pauli-Y,
        :func:`calculate_exp_Y`; otherwise Z-basis calculation via
        :func:`calculate_expectation` with a ``"ZZ...Z"`` Hamiltonian.

    Example:
        >>> z_result = {"0": 1.0}
        >>> x_result = {"0": 1.0}  # After H rotation on |0⟩
        >>> calculate_multi_basis_expectation(
        ...     {"Z": z_result, "X": x_result}, nqubit=1
        ... )
        {'Z': 1.0, 'X': 1.0}
    """
    results: Dict[str, float] = {}
    for basis_label, result in measured_results.items():
        if basis_label.upper().startswith("X"):
            results[basis_label] = calculate_exp_X(result, nqubit)
        elif basis_label.upper().startswith("Y"):
            results[basis_label] = calculate_exp_Y(result, nqubit)
        else:
            # Default: Z basis. Compute ⟨ZZ...Z⟩.
            hamiltonian = "Z" * nqubit
            results[basis_label] = calculate_expectation(result, hamiltonian)
    return results


def _ensure_dict(
    measured_result: Union[Dict[str, float], List[float]],
    nqubit: int,
) -> Dict[str, float]:
    """Convert list-format measurement results to dict if needed."""
    if isinstance(measured_result, list):
        keys = [f"{i:0{nqubit}b}" for i in range(len(measured_result))]
        return dict(zip(keys, measured_result))
    return measured_result


def calculate_exp_X(
    measured_result: Union[Dict[str, float], List[float]],
    nqubit: int,
    qubit_index: int = 0,
) -> float:
    """Calculate the expectation value of the Pauli-X operator.

    The input ``measured_result`` must contain results measured **after**
    applying a Hadamard gate on the target qubit (X-basis rotation).

    The formula is: ``⟨X_k⟩ = Σ_b sign(b_k) * prob(b)``, where
    ``sign(b_k) = +1`` when bit ``k`` is ``0`` and ``-1`` when ``1``.

    Args:
        measured_result: Z-basis measurement outcomes (after H rotation).
            Supports:

            - **key-value dict**: ``{"00": 0.5, "11": 0.5}``.
            - **list**: ``[p0, p1, ...]`` in computational-basis order.

        nqubit: Number of qubits.
        qubit_index: Which qubit to calculate ⟨X⟩ for (0 = MSB).
            Defaults to 0.

    Returns:
        The expectation value ``⟨X⟩`` as a float in ``[-1, 1]``.

    Example:
        >>> # Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 has ⟨X⊗X⟩ = 1
        >>> result = {"00": 0.5, "11": 0.5}
        >>> calculate_exp_X(result, nqubit=2)
        1.0

        >>> # Single-qubit |+⟩ state (H|0⟩) has ⟨X⟩ = 1
        >>> result = {"0": 0.5, "1": 0.5}
        >>> calculate_exp_X(result, nqubit=1)
        1.0
    """
    measured_result = _ensure_dict(measured_result, nqubit)

    # ⟨X_k⟩ = p(bit_k=0) - p(bit_k=1)
    exp = 0.0
    for outcome, prob in measured_result.items():
        if outcome[qubit_index] == "0":
            exp += prob
        else:
            exp -= prob
    return exp


def calculate_exp_Y(
    measured_result: Union[Dict[str, float], List[float]],
    nqubit: int,
    qubit_index: int = 0,
) -> float:
    """Calculate the expectation value of the Pauli-Y operator.

    The input ``measured_result`` must contain results measured **after**
    applying ``S^† H`` on the target qubit (Y-basis rotation).

    The formula is the same as for X: ``⟨Y_k⟩ = p(bit_k=0) - p(bit_k=1)``
    applied to the rotated measurement results.

    Args:
        measured_result: Z-basis measurement outcomes (after S†H rotation).
            Supports:

            - **key-value dict**: ``{"00": 0.5, "11": 0.5}``.
            - **list**: ``[p0, p1, ...]`` in computational-basis order.

        nqubit: Number of qubits.
        qubit_index: Which qubit to calculate ⟨Y⟩ for (0 = MSB).
            Defaults to 0.

    Returns:
        The expectation value ``⟨Y⟩`` as a float in ``[-1, 1]``.

    Example:
        >>> # |+i⟩ state = (|0⟩ + i|1⟩)/√2, after S†H rotation
        >>> # measures |0⟩ with probability 1.0 → ⟨Y⟩ = 1.0
        >>> result = {"0": 1.0}
        >>> calculate_exp_Y(result, nqubit=1)
        1.0

        >>> # Single-qubit |0⟩ has ⟨Y⟩ = 0 (after rotation: 50/50)
        >>> result = {"0": 0.5, "1": 0.5}
        >>> calculate_exp_Y(result, nqubit=1)
        0.0
    """
    measured_result = _ensure_dict(measured_result, nqubit)

    # ⟨Y_k⟩ = p(bit_k=0) - p(bit_k=1) (same sign formula as X)
    exp = 0.0
    for outcome, prob in measured_result.items():
        if outcome[qubit_index] == "0":
            exp += prob
        else:
            exp -= prob
    return exp
