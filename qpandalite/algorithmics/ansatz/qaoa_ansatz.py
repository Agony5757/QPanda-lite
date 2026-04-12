"""QAOA (Quantum Approximate Optimization Algorithm) ansatz.

Constructs the alternating-operator ansatz used in QAOA for solving
combinatorial optimisation problems.
"""

__all__ = ["qaoa_ansatz"]

from typing import List, Optional, Tuple
import numpy as np
from qpandalite.circuit_builder import Circuit


def _parse_pauli_string(pauli_string: str) -> List[Tuple[str, int]]:
    """Parse a Pauli string like 'Z0Z1' or 'X0Y1Z2' into [(op, qubit), ...]."""
    terms = []
    current_op = None
    current_idx = ""
    for ch in pauli_string:
        if ch in "XYZI":
            if current_op is not None:
                terms.append((current_op, int(current_idx)))
            current_op = ch
            current_idx = ""
        elif ch.isdigit():
            current_idx += ch
    if current_op is not None:
        terms.append((current_op, int(current_idx)))
    return terms


def _apply_cost_unitary(
    circuit: Circuit,
    hamiltonian_terms: List[Tuple[str, float]],
    gamma: float,
) -> None:
    """Apply the cost-function unitary exp(-i γ H_C).

    For each Pauli string with coefficient h, applies exp(-i γ h P).
    """
    for pauli_str, coeff in hamiltonian_terms:
        angle = 2 * gamma * coeff
        terms = _parse_pauli_string(pauli_str)

        # Filter out identity terms
        non_id = [(op, q) for op, q in terms if op != "I"]
        if not non_id:
            continue

        # Apply basis rotation for non-Z terms, then CNOT cascade, Rz, undo
        # Step 1: Rotate non-Z qubits to Z basis
        for op, q in non_id:
            if op == "X":
                circuit.h(q)
            elif op == "Y":
                circuit.rz(q, -np.pi / 2 + 1e-15)
                circuit.h(q)

        # Step 2: CNOT cascade
        for i in range(len(non_id) - 1):
            circuit.cx(non_id[i][1], non_id[i + 1][1])

        # Step 3: Rz on last qubit
        if abs(angle) > 1e-15:
            circuit.rz(non_id[-1][1], float(angle))

        # Step 4: Undo CNOT cascade
        for i in range(len(non_id) - 2, -1, -1):
            circuit.cx(non_id[i][1], non_id[i + 1][1])

        # Step 5: Undo basis rotations
        for op, q in non_id:
            if op == "X":
                circuit.h(q)
            elif op == "Y":
                circuit.h(q)
                circuit.rz(q, np.pi / 2 + 1e-15)


def _apply_mixer_unitary(
    circuit: Circuit,
    n_qubits: int,
    qubits: List[int],
    beta: float,
) -> None:
    """Apply the mixer unitary exp(-i β Σ X_i) = Π Rx(2β)."""
    for q in qubits:
        circuit.h(q)
        if abs(2 * beta) > 1e-15:
            circuit.rz(q, float(2 * beta))
        circuit.h(q)


def qaoa_ansatz(
    cost_hamiltonian: List[Tuple[str, float]],
    p: int = 1,
    qubits: Optional[List[int]] = None,
    betas: Optional[np.ndarray] = None,
    gammas: Optional[np.ndarray] = None,
) -> Circuit:
    """Build a QAOA ansatz circuit.

    The ansatz alternates between the cost unitary
    :math:`U_C(\\gamma) = e^{-i\\gamma H_C}` and the mixer unitary
    :math:`U_M(\\beta) = e^{-i\\beta \\sum X_i}` for *p* layers.

    Args:
        cost_hamiltonian: List of ``(pauli_string, coefficient)`` tuples.
            Pauli strings use the format ``"Z0Z1"``, ``"X0Y1Z2"``, etc.
        p: Number of QAOA layers.
        qubits: Qubit indices.  ``None`` → auto-detect from hamiltonian.
        betas: Mixer angles, length *p*.  ``None`` → random.
        gammas: Cost angles, length *p*.  ``None`` → random.

    Returns:
        A :class:`Circuit` object.

    Raises:
        ValueError: Angle arrays have wrong length.

    Example:
        >>> from qpandalite.algorithmics.ansatz import qaoa_ansatz
        >>> H = [("Z0Z1", 1.0), ("Z1Z2", 1.0), ("Z0Z2", 0.5)]
        >>> c = qaoa_ansatz(H, p=2)
    """
    # Determine qubit set
    all_qubits = set()
    for pauli_str, _ in cost_hamiltonian:
        for _, q in _parse_pauli_string(pauli_str):
            all_qubits.add(q)
    n_qubits = max(all_qubits) + 1 if all_qubits else 0

    if qubits is None:
        qubits = list(range(n_qubits))
    else:
        qubits = list(qubits)

    if betas is None:
        betas = np.random.uniform(0, np.pi, size=p)
    if gammas is None:
        gammas = np.random.uniform(0, np.pi, size=p)

    betas = np.asarray(betas)
    gammas = np.asarray(gammas)

    if len(betas) != p:
        raise ValueError(f"betas length ({len(betas)}) must equal p ({p})")
    if len(gammas) != p:
        raise ValueError(f"gammas length ({len(gammas)}) must equal p ({p})")

    circuit = Circuit()

    # Initial state: Hadamard on all qubits (uniform superposition)
    for q in qubits:
        circuit.h(q)

    # QAOA layers
    for layer in range(p):
        _apply_cost_unitary(circuit, cost_hamiltonian, float(gammas[layer]))
        _apply_mixer_unitary(circuit, n_qubits, qubits, float(betas[layer]))

    return circuit
