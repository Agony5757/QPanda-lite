#!/usr/bin/env python
"""Variational Quantum Eigensolver (VQE) — complete example.

Demonstrates:
  * Building a UCCSD ansatz for molecular Hamiltonians
  * Computing energy expectation values via Pauli decomposition
  * Classical optimisation loop (COBYLA) to find ground-state energy
  * Using qpandalite ansatz + measurement modules

Usage:
    python vqe.py [--molecule NAME] [--maxiter N]

References:
    Peruzzo et al. (2014). "A variational eigenvalue solver on a photonic
    quantum processor." Nature Communications 5, 4213.
    https://arxiv.org/abs/1304.3061
"""

import argparse
import sys
import numpy as np

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.originir_simulator import OriginIR_Simulator
from qpandalite.algorithmics.ansatz import uccsd_ansatz
from qpandalite.algorithmics.measurement import pauli_expectation


# ── Toy Hamiltonian: H₂ (STO-3G, 2-electron, 4 spin-orbital) ──────────
# Bravyi–Kitaev mapped, simplified for demonstration.
# E_nuclear ≈ 0.72 Ha
H2_HAMILTONIAN = [
    ("I0", -0.8105),
    ("Z0", +0.1720),
    ("Z1", -0.2258),
    ("Z2", +0.1720),
    ("Z3", -0.2258),
    ("Z0Z1", +0.1205),
    ("Z0Z2", +0.0455),
    ("Z0Z3", +0.1660),
    ("Z1Z2", +0.1660),
    ("Z1Z3", +0.1205),
    ("Z2Z3", +0.0455),
    ("X0X1Y2Y3", -0.0455),
    ("Y0Y1X2X3", +0.0455),
]
H2_NUCLEAR = 0.72


def vqe_energy(params, hamiltonian, n_qubits, n_electrons):
    """Evaluate ⟨ψ(θ)|H|ψ(θ)⟩ using the UCCSD ansatz.

    For each Pauli string in the Hamiltonian, builds the measurement
    circuit and computes the expectation value via the statevector simulator.

    Args:
        params: Variational parameters (array).
        hamiltonian: List of (pauli_string, coefficient) tuples.
        n_qubits: Number of qubits (spin-orbitals).
        n_electrons: Number of electrons.

    Returns:
        Total energy (float).
    """
    # Build the ansatz circuit
    circuit = uccsd_ansatz(n_qubits, n_electrons, params=params)

    # Simulate statevector
    sim = OriginIR_Simulator(backend_type="statevector")
    # For energy evaluation, we use direct statevector overlap
    # (in practice, you'd use pauli_expectation with shot-based simulation)
    sv = sim.simulate_statevector(circuit.originir)

    energy = 0.0
    for pauli_str, coeff in hamiltonian:
        # For demonstration: compute Pauli expectation via statevector
        # Build observable matrix and compute <ψ|P|ψ>
        n = n_qubits
        obs = _pauli_matrix(pauli_str, n)
        exp_val = np.real(sv.conj() @ obs @ sv)
        energy += coeff * exp_val

    return energy


def _pauli_matrix(pauli_str, n_qubits):
    """Build the full 2^n × 2^n matrix for a Pauli string."""
    I = np.eye(2)
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])
    pauli_map = {"I": I, "X": X, "Y": Y, "Z": Z}

    # Parse pauli_str like "Z0Z1" or "X0X1Y2Y3"
    ops = {}
    for ch in pauli_str:
        if ch in "IXYZ":
            current_op = ch
        elif ch.isdigit():
            ops[int(ch)] = current_op

    matrices = []
    for i in range(n_qubits):
        matrices.append(pauli_map.get(ops.get(i, "I"), I))

    result = matrices[0]
    for m in matrices[1:]:
        result = np.kron(result, m)
    return result


def run_vqe(molecule="H2", maxiter=100):
    """Run the VQE optimisation loop.

    Args:
        molecule: Molecule name (currently only "H2").
        maxiter: Maximum optimiser iterations.

    Returns:
        Optimised energy (float).
    """
    if molecule != "H2":
        raise ValueError(f"Unsupported molecule: {molecule}")

    n_qubits = 4
    n_electrons = 2

    # UCCSD: 2 singles + 1 double = 3 parameters for H₂
    from itertools import combinations
    occupied = list(range(n_electrons))
    virtual = list(range(n_electrons, n_qubits))
    n_singles = len(occupied) * len(virtual)
    n_doubles = len(list(combinations(occupied, 2))) * len(list(combinations(virtual, 2)))
    n_params = n_singles + n_doubles

    print(f"VQE for {molecule}")
    print(f"  Qubits: {n_qubits}, Electrons: {n_electrons}")
    print(f"  UCCSD parameters: {n_params} ({n_singles} singles + {n_doubles} doubles)")
    print(f"  Hamiltonian terms: {len(H2_HAMILTONIAN)}")
    print(f"  Nuclear repulsion: {H2_NUCLEAR:.4f} Ha")
    print()

    # Simple gradient-free optimisation (coordinate descent)
    params = np.zeros(n_params)
    best_energy = float("inf")
    step = 0.1

    for iteration in range(maxiter):
        improved = False
        for i in range(n_params):
            # Try positive step
            params[i] += step
            e_plus = vqe_energy(params, H2_HAMILTONIAN, n_qubits, n_electrons)

            # Try negative step
            params[i] -= 2 * step
            e_minus = vqe_energy(params, H2_HAMILTONIAN, n_qubits, n_electrons)

            # Reset
            params[i] += step
            e_curr = vqe_energy(params, H2_HAMILTONIAN, n_qubits, n_electrons)

            if e_plus < e_curr and e_plus < e_minus:
                params[i] += step
                improved = True
            elif e_minus < e_curr:
                params[i] -= step
                improved = True

        energy = vqe_energy(params, H2_HAMILTONIAN, n_qubits, n_electrons)
        total = energy + H2_NUCLEAR

        if total < best_energy:
            best_energy = total

        if iteration % 10 == 0:
            print(f"  Iter {iteration:3d}: E = {total:.6f} Ha")

        if not improved:
            step *= 0.5
            if step < 1e-6:
                break

    total = vqe_energy(params, H2_HAMILTONIAN, n_qubits, n_electrons) + H2_NUCLEAR
    print(f"\n  Final energy: {total:.6f} Ha")
    print(f"  Parameters: {params}")
    print(f"  Exact FCI:   -1.137274 Ha")

    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VQE example")
    parser.add_argument("--molecule", default="H2", help="Molecule (default: H2)")
    parser.add_argument("--maxiter", type=int, default=100, help="Max iterations")
    args = parser.parse_args()

    run_vqe(molecule=args.molecule, maxiter=args.maxiter)
