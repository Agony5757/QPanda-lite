#!/usr/bin/env python
"""Quantum Approximate Optimization Algorithm (QAOA) — complete example.

Demonstrates:
  * Building a QAOA ansatz for MaxCut
  * Evaluating the cost function via Pauli measurements
  * Classical optimisation to find approximate solutions
  * Using qpandalite ansatz + measurement modules

Usage:
    python qaoa.py [--p LAYERS] [--maxiter N] [--graph FILE]

References:
    Farhi, E. et al. (2014). "A Quantum Approximate Optimization Algorithm."
    arXiv:1411.4028.
"""

import argparse
import sys
import numpy as np

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.originir_simulator import OriginIR_Simulator
from qpandalite.algorithmics.ansatz import qaoa_ansatz


# ── Example graph: triangle (3-node ring) ──────────────────────────────
TRIANGLE_EDGES = [(0, 1), (1, 2), (0, 2)]


def maxcut_hamiltonian(edges, n_nodes):
    """Build the MaxCut cost Hamiltonian.

    H_C = -½ Σ_{(i,j)∈E} (1 - Z_i Z_j)

    Maximising -H_C ⟺ maximising the number of cut edges.

    Args:
        edges: List of (i, j) tuples.
        n_nodes: Number of graph nodes.

    Returns:
        List of (pauli_string, coefficient) tuples.
    """
    hamiltonian = [("I" + str(0), -len(edges) / 2.0)]  # constant term (dummy)
    # We'll handle the constant separately
    terms = []
    for i, j in edges:
        terms.append((f"Z{i}Z{j}", 0.5))  # -½ × (-Z_i Z_j) = +½ Z_i Z_j
    return terms, -len(edges) / 2.0  # (pauli_terms, constant_offset)


def qaoa_energy(betas_gammas, cost_terms, p, n_qubits):
    """Evaluate ⟨ψ(β,γ)|H_C|ψ(β,γ)⟩.

    Args:
        betas_gammas: Concatenated [β₁...βₚ, γ₁...γₚ].
        cost_terms: Pauli terms from maxcut_hamiltonian.
        p: Number of QAOA layers.
        n_qubits: Number of qubits.

    Returns:
        Expected cut value (float).
    """
    betas = betas_gammas[:p]
    gammas = betas_gammas[p:]

    circuit = qaoa_ansatz(cost_terms, p=p, betas=betas, gammas=gammas)

    sim = OriginIR_Simulator(backend_type="statevector")
    sv = sim.simulate_statevector(circuit.originir)

    # Compute expectation value of each Pauli term
    energy = 0.0
    for pauli_str, coeff in cost_terms:
        obs = _pauli_matrix(pauli_str, n_qubits)
        exp_val = np.real(sv.conj() @ obs @ sv)
        energy += coeff * exp_val

    return energy


def _pauli_matrix(pauli_str, n_qubits):
    """Build matrix for a Pauli string."""
    I = np.eye(2)
    Z = np.array([[1, 0], [0, -1]])
    pauli_map = {"I": I, "Z": Z, "X": np.array([[0, 1], [1, 0]]),
                 "Y": np.array([[0, -1j], [1j, 0]])}

    ops = {}
    current_op = None
    for ch in pauli_str:
        if ch in "IXYZ":
            current_op = ch
        elif ch.isdigit():
            ops[int(ch)] = current_op

    matrices = [pauli_map.get(ops.get(i, "I"), I) for i in range(n_qubits)]
    result = matrices[0]
    for m in matrices[1:]:
        result = np.kron(result, m)
    return result


def run_qaoa(p=2, maxiter=80, edges=None):
    """Run QAOA for MaxCut.

    Args:
        p: Number of QAOA layers.
        maxiter: Maximum optimiser iterations.
        edges: Graph edges. Defaults to triangle.

    Returns:
        Best energy and parameters.
    """
    if edges is None:
        edges = TRIANGLE_EDGES

    n_nodes = max(max(i, j) for i, j in edges) + 1
    cost_terms, const_offset = maxcut_hamiltonian(edges, n_nodes)

    print(f"QAOA for MaxCut")
    print(f"  Graph: {len(edges)} edges, {n_nodes} nodes")
    print(f"  Layers (p): {p}")
    print(f"  Max possible cut: {len(edges)}")
    print()

    # Coordinate-descent optimisation
    rng = np.random.default_rng(42)
    params = rng.uniform(0, np.pi, size=2 * p)
    best_energy = float("inf")
    best_params = params.copy()
    step = 0.2

    for iteration in range(maxiter):
        improved = False
        for i in range(2 * p):
            original = params[i]

            params[i] = original + step
            e_plus = qaoa_energy(params, cost_terms, p, n_nodes)

            params[i] = original - step
            e_minus = qaoa_energy(params, cost_terms, p, n_nodes)

            params[i] = original
            e_curr = qaoa_energy(params, cost_terms, p, n_nodes)

            if e_plus < e_curr and e_plus <= e_minus:
                params[i] = original + step
                improved = True
            elif e_minus < e_curr:
                params[i] = original - step
                improved = True

        energy = qaoa_energy(params, cost_terms, p, n_nodes)
        cut_value = -(energy + const_offset)

        if energy < best_energy:
            best_energy = energy
            best_params = params.copy()

        if iteration % 20 == 0:
            print(f"  Iter {iteration:3d}: cut ≈ {cut_value:.3f}")

        if not improved:
            step *= 0.5
            if step < 1e-6:
                break

    energy = qaoa_energy(best_params, cost_terms, p, n_nodes)
    cut_value = -(energy + const_offset)
    print(f"\n  Best cut value: {cut_value:.3f} / {len(edges)}")
    print(f"  Approximation ratio: {cut_value / len(edges):.3f}")

    return cut_value, best_params


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QAOA MaxCut example")
    parser.add_argument("-p", type=int, default=2, help="QAOA layers")
    parser.add_argument("--maxiter", type=int, default=80, help="Max iterations")
    args = parser.parse_args()

    run_qaoa(p=args.p, maxiter=args.maxiter)
