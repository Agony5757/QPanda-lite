"""Arbitrary state preparation via rotation method.

Uses the Shende–Bullock–Markov (SBM) decomposition: disentangles qubits
one at a time, then reverses the gate sequence.
"""

__all__ = ["rotation_prepare"]

from typing import List, Optional
import numpy as np
from qpandalite.circuit_builder import Circuit


def _apply_multiplexed_ry(
    circuit: Circuit,
    target: int,
    controls: List[int],
    angles: np.ndarray,
) -> None:
    """Apply a uniformly-controlled Ry (multiplexed Ry).

    For each control pattern k (0 to 2^n-1), apply Ry(angles[k]) on target.
    Uses the standard recursive decomposition into CNOTs and single Ry.
    """
    n = len(controls)
    if n == 0:
        # Base case: no control qubits, just a single rotation.
        # angles has length 1.
        if abs(angles[0]) > 1e-15:
            circuit.ry(target, float(angles[0]))
        return

    assert len(angles) == 2**n, (
        f"Expected {2**n} angles for {n} controls, got {len(angles)}"
    )

    # Recursive decomposition:
    # Split angles into even (k with MSB=0) and odd (k with MSB=1)
    even_angles = angles[0::2]  # control[0] = 0
    odd_angles = angles[1::2]   # control[0] = 1

    # Compute sum and difference
    sum_angles = (even_angles + odd_angles) / 2.0
    diff_angles = (even_angles - odd_angles) / 2.0

    inner_controls = controls[1:]

    _apply_multiplexed_ry(circuit, target, inner_controls, diff_angles)
    circuit.cx(controls[0], target)
    _apply_multiplexed_ry(circuit, target, inner_controls, sum_angles)
    circuit.cx(controls[0], target)


def _apply_multiplexed_rz(
    circuit: Circuit,
    target: int,
    controls: List[int],
    angles: np.ndarray,
) -> None:
    """Apply a uniformly-controlled Rz (multiplexed Rz)."""
    n = len(controls)
    if n == 0:
        # Base case: no control qubits, just a single rotation.
        if abs(angles[0]) > 1e-15:
            circuit.rz(target, float(angles[0]))
        return

    assert len(angles) == 2**n, (
        f"Expected {2**n} angles for {n} controls, got {len(angles)}"
    )

    even_angles = angles[0::2]
    odd_angles = angles[1::2]
    sum_angles = (even_angles + odd_angles) / 2.0
    diff_angles = (even_angles - odd_angles) / 2.0

    inner_controls = controls[1:]
    _apply_multiplexed_rz(circuit, target, inner_controls, diff_angles)
    circuit.cx(controls[0], target)
    _apply_multiplexed_rz(circuit, target, inner_controls, sum_angles)
    circuit.cx(controls[0], target)


def rotation_prepare(
    circuit: Circuit,
    target_vector: np.ndarray,
    qubits: Optional[List[int]] = None,
) -> None:
    """Prepare an arbitrary quantum state from a complex amplitude vector.

    Uses the Shende–Bullock–Markov state-preparation algorithm.  The
    method works by computing the circuit that would *disentangle* the
    target state back to ``|00...0>``, collecting the gates, then applying
    them in reverse order.

    Gate count: O(2^n) for n qubits.

    The vector is automatically normalised.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        target_vector: 1-D complex array of length ``2**n`` specifying
            the target state amplitudes.
        qubits: Qubit indices to use.  ``None`` → first n qubits.

    Raises:
        ValueError: *target_vector* length is not a power of 2.
        ValueError: *target_vector* is the zero vector.

    Example:
        >>> import numpy as np
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.state_preparation import rotation_prepare
        >>> target = np.array([1, 0, 0, 1]) / np.sqrt(2)  # Bell state
        >>> c = Circuit()
        >>> rotation_prepare(c, target)
    """
    target_vector = np.asarray(target_vector, dtype=complex)
    d = len(target_vector)

    if d == 0:
        raise ValueError("target_vector must not be empty")

    n = int(round(np.log2(d)))
    if 2**n != d:
        raise ValueError(f"target_vector length ({d}) must be a power of 2")

    norm = np.linalg.norm(target_vector)
    if norm < 1e-15:
        raise ValueError("target_vector must not be the zero vector")

    alpha = target_vector / norm

    if qubits is None:
        qubits = list(range(n))
    else:
        qubits = list(qubits)

    # Collect gates in DISENTANGLING order, then reverse.
    # We disentangle qubits from 0 (LSB) to n-1 (MSB).
    # At each level l, qubit l is disentangled (set to |0>),
    # controlled by qubits l+1 .. n-1.

    gates_reverse: list[tuple] = []  # (gate_type, args)

    for level in range(n):
        q = qubits[level]
        controls = qubits[level + 1:]
        n_ctrl = len(controls)
        n_blocks = 2**n_ctrl

        # Pair amplitudes: for each control pattern k,
        # pair (alpha[2k], alpha[2k+1]) where the level-th bit is 0/1.
        # alpha is indexed with level-th bit as the LSB of the remaining state.

        ry_angles = np.zeros(n_blocks)
        rz_angles = np.zeros(n_blocks)

        for k in range(n_blocks):
            # Reconstruct full indices: control pattern k determines bits
            # for qubits level+1..n-1, and the current qubit (level) varies.
            idx_even = 2 * k      # level-th bit = 0
            idx_odd = 2 * k + 1   # level-th bit = 1

            a_e = alpha[idx_even]
            a_o = alpha[idx_odd]

            r_e = abs(a_e)
            r_o = abs(a_o)

            # Ry angle to disentangle: map (r_e, r_o) → (sqrt(r_e²+r_o²), 0)
            ry_angles[k] = -2.0 * np.arctan2(r_o, r_e)

            # Phase correction
            if r_e > 1e-15 and r_o > 1e-15:
                rz_angles[k] = np.angle(a_o) - np.angle(a_e)

        gates_reverse.append(('rz', q, controls, rz_angles.copy()))
        gates_reverse.append(('ry', q, controls, ry_angles.copy()))

        # Update alpha: collapse pairs
        new_alpha = np.zeros(n_blocks, dtype=complex)
        for k in range(n_blocks):
            idx_even = 2 * k
            idx_odd = 2 * k + 1
            a_e = alpha[idx_even]
            a_o = alpha[idx_odd]
            # Use the larger-magnitude element's phase as reference
            # to avoid phase noise when one amplitude is near zero
            ref = a_e if abs(a_e) >= abs(a_o) else a_o
            new_alpha[k] = np.sqrt(
                abs(a_e)**2 + abs(a_o)**2
            ) * np.exp(1j * np.angle(ref))
        alpha = new_alpha

    # Apply gates in REVERSE order (preparation = reverse of disentangling)
    for gate_type, q, controls, angles in reversed(gates_reverse):
        if gate_type == 'ry':
            _apply_multiplexed_ry(circuit, q, controls, angles)
        else:
            _apply_multiplexed_rz(circuit, q, controls, angles)
