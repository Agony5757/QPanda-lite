"""Thermal state (Boltzmann distribution) preparation."""

__all__ = ["thermal_state"]

from typing import List, Optional
import numpy as np
from qpandalite.circuit_builder import Circuit


def thermal_state(
    circuit: Circuit,
    beta: float,
    hamiltonian: Optional[np.ndarray] = None,
    qubits: Optional[List[int]] = None,
) -> None:
    """Prepare a thermal (Gibbs) state for a given inverse temperature β.

    For the default Hamiltonian H = Σ Z_i, each qubit independently
    receives a Ry(θ) gate where θ = 2·arccos(√p₀) with
    p₀ = e^β/(e^β + e^{-β}).

    For a custom Hamiltonian, the function diagonalises H, computes
    Boltzmann weights, and uses :func:`rotation_prepare`.

    Args:
        circuit: Quantum circuit (mutated in-place).
        beta: Inverse temperature.  ``0`` → maximally mixed; ``∞`` → ground state.
        hamiltonian: ``2^n × 2^n`` Hermitian matrix, or ``None`` for H = Σ Z_i.
        qubits: Qubit indices.  ``None`` → all circuit qubits.

    Raises:
        ValueError: *beta* is negative or *hamiltonian* shape is wrong.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.state_preparation import thermal_state
        >>> c = Circuit()
        >>> thermal_state(c, beta=1.0, qubits=[0])
    """
    if beta < 0:
        raise ValueError(f"beta must be non-negative, got {beta}")

    if hamiltonian is None:
        # Default: H = Σ Z_i, independent qubits
        # p(0) = e^β / (e^β + e^{-β}), p(1) = e^{-β} / (e^β + e^{-β})
        p0 = np.exp(beta) / (np.exp(beta) + np.exp(-beta)) if beta < 500 else 1.0
        theta = 2.0 * np.arccos(np.clip(np.sqrt(p0), 0, 1))

        if qubits is None:
            qubits = list(range(circuit.max_qubit + 1))

        for q in qubits:
            if abs(theta) > 1e-15:
                circuit.ry(q, theta)
    else:
        hamiltonian = np.asarray(hamiltonian, dtype=complex)
        d = hamiltonian.shape[0]
        if hamiltonian.shape != (d, d):
            raise ValueError("hamiltonian must be a square matrix")

        if qubits is None:
            n = int(round(np.log2(d)))
            qubits = list(range(n))
        else:
            n = len(qubits)

        if d != 2**n:
            raise ValueError(
                f"hamiltonian dimension ({d}) must equal 2^n = {2**n}"
            )

        eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
        shifted = -beta * eigenvalues
        shifted -= np.max(shifted)
        weights = np.exp(shifted)
        weights /= np.sum(weights)

        state_vector = eigenvectors @ np.sqrt(weights)

        from .rotation_prepare import rotation_prepare
        rotation_prepare(circuit, state_vector, qubits)
