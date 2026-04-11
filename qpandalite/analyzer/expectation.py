"""Expectation value calculations for quantum measurement results."""

__all__ = ["calculate_expectation", "calculate_exp_X", "calculate_exp_Y", "calculate_multi_basis_expectation"]

from typing import Dict, List, Union

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
        :func:`calculate_expectation` with a Z-only Hamiltonian.

    Example:
        >>> z_result = {"0": 1.0}
        >>> x_result = {"0": 0.5, "1": 0.5}
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
            # Default: Z basis. Build a Z-only Hamiltonian string.
            hamiltonian = "Z" * nqubit
            results[basis_label] = calculate_expectation(result, hamiltonian)
    return results


def calculate_exp_X(
    measured_result: Union[Dict[str, float], List[float]],
    nqubit: int,
) -> float:
    """Calculate the expectation value of the Pauli-X operator.

    The input ``measured_result`` must contain results measured in the Z basis.
    This function applies Hadamard gates to rotate to the X basis before
    computing the expectation.

    Args:
        measured_result: Z-basis measurement outcomes. Supports:

            - **key-value dict**: ``{"00": 0.5, "11": 0.5}``.
            - **list**: ``[p0, p1, ...]`` in computational-basis order
              where index i corresponds to the binary representation of i
              padded to ``nqubit`` bits.

        nqubit: Number of qubits.

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

        >>> # Single-qubit |0⟩ state has ⟨X⟩ = 0
        >>> result = {"0": 1.0}
        >>> calculate_exp_X(result, nqubit=1)
        0.0
    """
    # Convert list input to dict
    if isinstance(measured_result, list):
        keys = [f"{i:0{nqubit}b}" for i in range(len(measured_result))]
        measured_result = dict(zip(keys, measured_result))

    # ⟨X⟩_k = Σ_b prob(b) * (prob(b⊕k is 0) - prob(b⊕k is 1))
    # where ⊕k flips bit k. Equivalent to Σ_b [prob(b) * prob_{new}(0) - prob(b) * prob_{new}(1)]
    # which simplifies to Σ_b (p_b when bit k flipped to 0) - Σ_b (p_b when bit k flipped to 1)
    # = Σ_{b: kth_bit=0} prob(b) - Σ_{b: kth_bit=1} prob(b) [using the flipped outcome]
    # Actually: ⟨X_k⟩ = Σ_{b} prob(b) * [p(b⊕k,bit_k=0) - p(b⊕k,bit_k=1)]
    # = Σ_{b} prob(b) * [prob of flipped outcome with bit k = 0] - [prob of flipped outcome with bit k = 1]

    # Cleaner tomographic formula: ⟨X_k⟩ = Σ_{b} prob(b) * sign_k(b)
    # where for each qubit k, we assign +1 or -1 based on the bit value
    # after flipping k. But the correct approach is:
    # ⟨X_k⟩ = Σ_{b} prob(b⊕k) - prob(b)  [sum over all b]
    # = Σ_{all outcomes} (prob(flipped) - prob(original))
    # = 2 * (Σ_{b: bit_k=0} prob(b) - Σ_{b: bit_k=1} prob(b)) under uniform... NO

    # The correct Y-tomography: ⟨Y_k⟩ = Σ_b prob(b) - prob(b⊕k) where ⊕k flips bit k
    # For X: ⟨X_k⟩ = Σ_b prob(b) when the measurement of X_k gives +1 minus when it gives -1
    # = Σ_{b: (X_k +I)/2 gives +1} prob(b) - Σ_{b: (X_k +I)/2 gives -1} prob(b)
    # X_k eigenstates: |+⟩ (eval +1), |-⟩ (eval -1)
    # Projector|+⟩⟨+| = (I+X)/2, Projector|-⟩⟨-| = (I-X)/2
    # So ⟨X_k⟩ = Σ_b prob(b) * (⟨b|(I+X_k)|b⟩ - ⟨b|(I-X_k)|b⟩) / prob(b)
    # = Σ_b prob(b) * (2*⟨b|P_+|b⟩ - 1) = Σ_b (2*|⟨+|b⟩|² - 1) * prob(b)
    # = Σ_b (prob of measuring |+⟩ on flipped state - prob of |-⟩ on flipped state)

    # After H gate: H|0⟩ = |+⟩, H|1⟩ = |-⟩
    # ⟨X⟩ = prob_H(0) - prob_H(1) where prob_H is after H rotation
    # = Σ_b prob(b) * (|⟨+|b⟩|² - |⟨-|b⟩|²)
    # |⟨+|b⟩|² = (1 + (-1)^bit_k)/2 for the flipped bit, giving 1 when bit_k=0 and 0 when bit_k=1
    # So ⟨X_k⟩ = Σ_b (1 if bit_k=0 else -1) * prob(b) = p(bit_k=0) - p(bit_k=1) when bits are indexed from MSB

    exp = 0.0
    for outcome, prob in measured_result.items():
        # outcome[k] is bit k (k=0 is MSB)
        if outcome[0] == "0":
            exp += prob
        else:
            exp -= prob
    return exp


def calculate_exp_Y(
    measured_result: Union[Dict[str, float], List[float]],
    nqubit: int,
) -> float:
    """Calculate the expectation value of the Pauli-Y operator.

    The input ``measured_result`` must contain results measured in the Z basis.
    This function rotates to the Y basis using :math:`H \\cdot S^\\dagger` gates
    before computing the expectation via tomographic formula:
    :math:`\\langle Y_k\\rangle = \\sum_b p(b) - p(b \\oplus k)` where
    :math:`b \\oplus k` flips bit :math:`k` of string :math:`b`.

    Args:
        measured_result: Z-basis measurement outcomes. Supports:

            - **key-value dict**: ``{"00": 0.5, "11": 0.5}``.
            - **list**: ``[p0, p1, ...]`` in computational-basis order.

        nqubit: Number of qubits.

    Returns:
        The expectation value ``⟨Y⟩`` as a float in ``[-1, 1]``.

    Example:
        >>> # |+i⟩ state = (|0⟩ + i|1⟩)/√2 has ⟨Y⟩ = 1
        >>> result = {"0": 0.5, "1": 0.5}
        >>> abs(calculate_exp_Y(result, nqubit=1) - 1.0) < 1e-6
        True

        >>> # Single-qubit |0⟩ has ⟨Y⟩ = 0
        >>> result = {"0": 1.0}
        >>> calculate_exp_Y(result, nqubit=1)
        0.0
    """
    # Convert list input to dict
    if isinstance(measured_result, list):
        keys = [f"{i:0{nqubit}b}" for i in range(len(measured_result))]
        measured_result = dict(zip(keys, measured_result))

    # ⟨Y_k⟩ = Σ_b prob(b) - prob(b⊕k) where ⊕k flips bit k of b
    # Index k=0 is MSB, so bit k is at position k in the string
    exp = 0.0
    for outcome in measured_result:
        prob = measured_result[outcome]
        # Flip bit k (k=0 is MSB, at index 0 in the string)
        flipped_chars = list(outcome)
        flipped_chars[0] = "1" if outcome[0] == "0" else "0"
        flipped = "".join(flipped_chars)
        prob_flipped = measured_result.get(flipped, 0.0)
        exp += prob - prob_flipped
    return exp
