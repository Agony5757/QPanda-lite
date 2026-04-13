"""Variational Quantum Deflation (VQD) circuit components."""

__all__ = ["vqd_circuit", "vqd_overlap_circuit"]

from typing import List, Optional

import numpy as np

from qpandalite.circuit_builder import Circuit


def _hea_ansatz(
    circuit: Circuit,
    params: List[float],
    n_layers: int,
    qubits: List[int],
) -> None:
    r"""Apply a Hardware-Efficient Ansatz (HEA) to the circuit.

    Each layer consists of:
    1. ``Ry`` rotation on every qubit.
    2. A chain of CNOT gates between adjacent qubits.

    The total number of parameters required is ``n_qubits * n_layers``.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        params: Rotation angles.  Length must equal ``len(qubits) * n_layers``.
        n_layers: Number of repeating layers.
        qubits: Qubit indices to apply the ansatz on.

    Raises:
        ValueError: Parameter count does not match ``n_qubits * n_layers``.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> c = Circuit(2)
        >>> _hea_ansatz(c, [0.1, 0.2, 0.3, 0.4], n_layers=2, qubits=[0, 1])
    """
    n_qubits = len(qubits)
    expected = n_qubits * n_layers
    if len(params) != expected:
        raise ValueError(
            f"Expected {expected} parameters (n_qubits={n_qubits} × "
            f"n_layers={n_layers}), got {len(params)}"
        )

    idx = 0
    for _ in range(n_layers):
        # Single-qubit Ry rotations
        for q in qubits:
            circuit.ry(params[idx], q)
            idx += 1
        # Entangling CNOT chain
        for i in range(n_qubits - 1):
            circuit.cnot(qubits[i], qubits[i + 1])


def vqd_circuit(
    circuit: Circuit,
    ansatz_params: List[float],
    prev_states: List[np.ndarray],
    qubits: Optional[List[int]] = None,
    penalty: float = 10.0,
    n_layers: int = 2,
) -> None:
    r"""Apply a VQD ansatz circuit to *circuit*.

    Variational Quantum Deflation (VQD) is a hybrid algorithm for finding
    excited states of a Hamiltonian one at a time.  It minimises the
    cost function

    .. math::

        C(\boldsymbol{\theta}) =
        \langle\psi(\boldsymbol{\theta})|H|\psi(\boldsymbol{\theta})\rangle
        + \sum_i \beta_i\,|\langle\psi(\boldsymbol{\theta})|\phi_i\rangle|^2

    where :math:`|\phi_i\rangle` are previously found lower-energy states
    and :math:`\beta_i` are penalty coefficients.

    This function **only** constructs the parameterised ansatz on the
    circuit.  The overlap penalty terms are evaluated separately (see
    :func:`vqd_overlap_circuit`) and combined by a classical optimiser.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        ansatz_params: Parameters for the HEA ansatz.
        prev_states: List of previously found state vectors (used by
            the classical optimiser, not directly in this circuit).
        qubits: Qubit indices.  ``None`` means all qubits of *circuit*.
        penalty: Penalty coefficient :math:`\beta` (used by the caller).
        n_layers: Number of HEA layers.

    Raises:
        ValueError: If *prev_states* is empty (use VQE for the ground state).

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> import numpy as np
        >>> c = Circuit(2)
        >>> gs = np.array([1, 0, 0, 0], dtype=complex)
        >>> vqd_circuit(c, [0.1]*4, prev_states=[gs], n_layers=2)
    """
    if qubits is None:
        qubits = list(range(circuit.n_qubits))

    if len(prev_states) == 0:
        raise ValueError(
            "prev_states is empty. Use VQE (not VQD) for the ground state."
        )

    _hea_ansatz(circuit, ansatz_params, n_layers, qubits)


def vqd_overlap_circuit(
    prev_state: np.ndarray,
    ansatz_params: List[float],
    n_layers: int = 2,
    qubits: Optional[List[int]] = None,
) -> Circuit:
    r"""Build a circuit to compute :math:`|\langle\psi(\boldsymbol{\theta})|\phi\rangle|^2`.

    Uses the **swap test**: an ancilla qubit controls SWAPs between the
    ansatz register and a register prepared in *prev_state*.  Measuring
    the ancilla in the computational basis gives an estimate of the
    overlap.

    Circuit layout (2 data qubits)::

        ancilla: ──H──●──────●──●──────●── Measure
                       |      |  |      |
        data_A:  ──[ansatz]──SWAP──[ansatz]──SWAP──
                       |      |  |      |
        data_B:  ──[prev]──SWAP──[prev]──SWAP──

    Args:
        prev_state: State vector :math:`|\phi\rangle` of dimension :math:`2^n`.
        ansatz_params: Parameters for the HEA ansatz.
        n_layers: Number of HEA layers.
        qubits: Data qubit indices for the ansatz register.
            ``None`` means ``[0, 1, …, n-1]`` where *n* is inferred
            from ``prev_state``.

    Returns:
        A new :class:`Circuit` containing the swap-test circuit with the
        ancilla measured.

    Raises:
        ValueError: *prev_state* is not a power-of-2 length.

    Example:
        >>> import numpy as np
        >>> gs = np.array([1, 0, 0, 0], dtype=complex)
        >>> circ = vqd_overlap_circuit(gs, [0.1]*4, n_layers=2)
    """
    dim = len(prev_state)
    n = int(np.log2(dim))
    if 2**n != dim:
        raise ValueError(
            f"prev_state length {dim} is not a power of 2."
        )

    if qubits is None:
        qubits = list(range(n))

    # Total qubits: 1 ancilla + n (ansatz) + n (prev_state)
    total = 1 + 2 * n
    circ = Circuit(total)

    ancilla = 0
    data_a = list(range(1, 1 + n))       # ansatz register
    data_b = list(range(1 + n, 1 + 2 * n))  # prev-state register

    # Prepare prev_state on data_b using state preparation
    _prepare_state(circ, prev_state, data_b)

    # Apply ansatz on data_a
    _hea_ansatz(circ, ansatz_params, n_layers, data_a)

    # Swap test
    circ.h(ancilla)
    for i in range(n):
        circ.cnot(ancilla, data_a[i])
        circ.cnot(ancilla, data_b[i])
        # Controlled-SWAP decomposition: CSWAP(ancilla, a, b)
        #   = CNOT(b, a) — H(b) — T(b) — CNOT(a, b) — T†(a) — CNOT(ancilla, b)
        #   — T(a) — CNOT(a, b) — T†(b) — H(b) — CNOT(ancilla, a)
        # Simpler: just use three CNOTs with ancilla control
        # Standard decomposition of Toffoli-based CSWAP:
        circ.cnot(data_b[i], data_a[i])
        circ.cnot(ancilla, data_b[i])
        circ.cnot(data_b[i], data_a[i])
        circ.cnot(ancilla, data_b[i])
        circ.cnot(data_a[i], data_b[i])
    circ.h(ancilla)

    circ.measure(ancilla)
    return circ


def _prepare_state(
    circuit: Circuit,
    state: np.ndarray,
    qubits: List[int],
) -> None:
    """Prepare an arbitrary state vector on the given qubits using multiplexed rotations.

    For small state vectors this uses a simple Schmidt-decomposition based
    preparation.  Normalises *state* if needed.

    Args:
        circuit: Circuit to modify in-place.
        state: Target state vector.
        qubits: Qubit indices.
    """
    n = len(qubits)
    dim = len(state)
    if dim != 2**n:
        raise ValueError(
            f"State vector length {dim} does not match {n} qubits (expected {2**n})."
        )

    # Normalise
    norm = np.linalg.norm(state)
    if norm == 0:
        raise ValueError("State vector is zero.")
    state = state / norm

    # Use state preparation via multiplexed Ry rotations (Schmidt decomposition)
    # This is a simplified recursive approach
    _state_prep_recursive(circuit, state, qubits)


def _state_prep_recursive(
    circuit: Circuit,
    state: np.ndarray,
    qubits: List[int],
) -> None:
    """Recursively prepare a state vector using controlled Ry rotations."""
    n = len(qubits)
    dim = len(state)

    if n == 1:
        # Single qubit: just Ry
        alpha = float(state[0])
        beta = float(state[1]) if dim > 1 else 0.0
        amp = np.sqrt(abs(alpha)**2 + abs(beta)**2)
        if amp < 1e-15:
            return
        theta = 2 * np.arccos(np.clip(abs(alpha) / amp, 0, 1))
        circuit.ry(theta, qubits[0])
        if beta != 0 and alpha != 0:
            phase_diff = np.angle(beta) - np.angle(alpha)
            if abs(phase_diff) > 1e-10:
                circuit.rz(phase_diff, qubits[0])
        return

    # Split state into two halves (for most-significant qubit control)
    half = dim // 2
    top = state[:half]
    bot = state[half:]

    norm_top = np.linalg.norm(top)
    norm_bot = np.linalg.norm(bot)
    total = np.sqrt(norm_top**2 + norm_bot**2)

    if total < 1e-15:
        return

    theta = 2 * np.arccos(np.clip(norm_top / total, 0, 1))
    circuit.ry(theta, qubits[0])

    if norm_top > 1e-15:
        _state_prep_recursive(circuit, top / norm_top, qubits[1:])
    # Apply X to flip to bottom half
    circuit.x(qubits[0])
    if norm_bot > 1e-15:
        _state_prep_recursive(circuit, bot / norm_bot, qubits[1:])
    circuit.x(qubits[0])
