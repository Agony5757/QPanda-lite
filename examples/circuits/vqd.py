#!/usr/bin/env python
"""Variational Quantum Deflation (VQD) — complete example.

Demonstrates:
  * Finding the ground state of H = Z₀ + Z₁ using VQE (layer 0)
  * Finding the first excited state using VQD with overlap penalty
  * Using scipy.optimize.minimize as the classical optimiser

Usage:
    python vqd.py [--n-qubits N] [--n-layers L] [--penalty B]

References:
    Higgott, O., Wang, D. & Brierley, S. (2019).
    "Variational Quantum Computation of Excited States."
    Quantum 3, 156.
"""

import argparse
import sys

import numpy as np

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.circuits.vqd import (
    vqd_circuit,
    vqd_overlap_circuit,
    _hea_ansatz,
)


def _make_hamiltonian_matrix(n_qubits: int) -> np.ndarray:
    """Build the matrix for H = sum_i Z_i on *n_qubits*."""
    dim = 2**n_qubits
    H = np.zeros((dim, dim), dtype=complex)
    for i in range(n_qubits):
        # Z_i = I⊗...⊗Z⊗...⊗I
        mat = np.array([1.0])
        for j in range(n_qubits):
            if j == i:
                mat = np.kron(mat, np.diag([1.0, -1.0]))
            else:
                mat = np.kron(mat, np.eye(2))
        H += mat
    return H


def _state_from_hea(ansatz_params: np.ndarray, n_qubits: int, n_layers: int) -> np.ndarray:
    """Compute the state vector produced by the HEA ansatz with given params."""
    dim = 2**n_qubits
    # Build unitary matrix by simulating the circuit
    c = Circuit(n_qubits)
    _hea_ansatz(c, list(ansatz_params), n_layers, list(range(n_qubits)))
    # Use state-vector simulation
    sim = QASM_Simulator()
    # Get state vector via QASM — use analytical approach instead
    # Build the unitary by column-by-column simulation
    from qpandalite.simulator.origin_simulator import SingleGateSimulator
    sim2 = SingleGateSimulator(n_qubits)
    # Apply gates manually
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0

    # Apply HEA gates to state vector
    idx = 0
    for _ in range(n_layers):
        for q in range(n_qubits):
            state = _apply_ry(state, ansatz_params[idx], q, n_qubits)
            idx += 1
        for q in range(n_qubits - 1):
            state = _apply_cnot(state, q, q + 1, n_qubits)

    return state


def _apply_ry(state: np.ndarray, theta: float, qubit: int, n_qubits: int) -> np.ndarray:
    """Apply Ry(theta) on qubit to state vector."""
    dim = 2**n_qubits
    new_state = state.copy()
    cos_t = np.cos(theta / 2)
    sin_t = np.sin(theta / 2)
    for i in range(dim):
        if (i >> (n_qubits - 1 - qubit)) & 1 == 0:
            j = i | (1 << (n_qubits - 1 - qubit))
            new_state[i] = cos_t * state[i] - sin_t * state[j]
            new_state[j] = sin_t * state[i] + cos_t * state[j]
    return new_state


def _apply_cnot(state: np.ndarray, control: int, target: int, n_qubits: int) -> np.ndarray:
    """Apply CNOT(control, target) to state vector."""
    dim = 2**n_qubits
    new_state = state.copy()
    for i in range(dim):
        c_bit = (i >> (n_qubits - 1 - control)) & 1
        if c_bit == 1:
            j = i ^ (1 << (n_qubits - 1 - target))
            new_state[i] = state[j]
            new_state[j] = state[i]
    return new_state


def vqe_objective(params: np.ndarray, n_qubits: int, n_layers: int, H: np.ndarray) -> float:
    """VQE cost function: ⟨ψ(θ)|H|ψ(θ)⟩."""
    state = _state_from_hea(params, n_qubits, n_layers)
    return float(np.real(state.conj() @ H @ state))


def vqd_objective(
    params: np.ndarray,
    n_qubits: int,
    n_layers: int,
    H: np.ndarray,
    prev_states: list,
    penalty: float,
) -> float:
    """VQD cost function: ⟨ψ(θ)|H|ψ(θ)⟩ + Σᵢ β|⟨ψ(θ)|φᵢ⟩|²."""
    state = _state_from_hea(params, n_qubits, n_layers)
    energy = float(np.real(state.conj() @ H @ state))
    overlap_penalty = 0.0
    for ps in prev_states:
        overlap_penalty += penalty * abs(np.dot(state.conj(), ps))**2
    return energy + overlap_penalty


def run_vqd(n_qubits: int, n_layers: int, penalty: float) -> None:
    """Run full VQD example: VQE ground state → VQD first excited state."""
    from scipy.optimize import minimize

    H = _make_hamiltonian_matrix(n_qubits)
    n_params = n_qubits * n_layers

    # Exact eigenvalues for reference
    eigenvalues = np.linalg.eigvalsh(H)

    # Step 1: VQE for ground state
    print(f"=== VQD Example: H = Z₀ + ... + Z_{{n-1}} on {n_qubits} qubits ===")
    print(f"n_layers={n_layers}, penalty={penalty}, n_params={n_params}")
    print()
    print(f"Exact eigenvalues: {eigenvalues}")
    print()

    print("--- Step 1: VQE (ground state) ---")
    best_energy = float("inf")
    best_params = None
    for trial in range(5):
        x0 = np.random.uniform(0, 2 * np.pi, n_params)
        res = minimize(vqe_objective, x0, args=(n_qubits, n_layers, H), method="COBYLA")
        if res.fun < best_energy:
            best_energy = res.fun
            best_params = res.x
    gs_state = _state_from_hea(best_params, n_qubits, n_layers)
    print(f"VQE ground state energy: {best_energy:.6f}  (exact: {eigenvalues[0]:.6f})")
    print()

    # Step 2: VQD for first excited state
    print("--- Step 2: VQD (first excited state) ---")
    best_vqd_energy = float("inf")
    best_vqd_params = None
    for trial in range(5):
        x0 = np.random.uniform(0, 2 * np.pi, n_params)
        res = minimize(
            vqd_objective,
            x0,
            args=(n_qubits, n_layers, H, [gs_state], penalty),
            method="COBYLA",
        )
        if res.fun < best_vqd_energy:
            best_vqd_energy = res.fun
            best_vqd_params = res.x

    es_state = _state_from_hea(best_vqd_params, n_qubits, n_layers)
    es_energy = float(np.real(es_state.conj() @ H @ es_state))
    overlap_with_gs = abs(np.dot(es_state.conj(), gs_state))**2

    print(f"VQD first excited state energy: {es_energy:.6f}  (exact: {eigenvalues[1]:.6f})")
    print(f"Overlap with ground state: {overlap_with_gs:.6f}")
    print()
    print("✓ Run complete.")


def main():
    parser = argparse.ArgumentParser(description="Variational Quantum Deflation (VQD)")
    parser.add_argument("--n-qubits", type=int, default=2, help="Number of qubits (default: 2)")
    parser.add_argument("--n-layers", type=int, default=2, help="Number of HEA layers (default: 2)")
    parser.add_argument("--penalty", type=float, default=10.0, help="Overlap penalty β (default: 10.0)")
    args = parser.parse_args()

    np.random.seed(42)
    run_vqd(args.n_qubits, args.n_layers, args.penalty)


if __name__ == "__main__":
    main()
