#!/usr/bin/env python
"""Entangled State Preparation — GHZ, W, and Cluster states.

Demonstrates:
  * Preparing GHZ, W, and Cluster entangled states
  * Measuring and displaying probability distributions
  * Using the entangled_states module from qpandalite

Usage:
    python entangled_states.py --state [ghz|w|cluster] [--n-qubits N] [--shots N]

References:
    * GHZ: Greenberger, D. M., Horne, M. A. & Zeilinger, A. (1989).
      "Going Beyond Bell's Theorem." In Bell's Theorem, Quantum Theory
      and Conceptions of the Universe, 69–72.
    * W state: Dür, W., Vidal, G. & Cirac, J. I. (2000).
      "Three qubits can be entangled in two inequivalent ways."
      Physical Review A, 62(6), 062314.
    * Cluster: Briegel, H. J. & Raussendorf, R. (2001).
      "Persistent Entanglement in Arrays of Interacting Particles."
      Physical Review Letters, 86(5), 910.
"""

import argparse
import sys

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.circuits import ghz_state, w_state, cluster_state


def run_state(state_type: str, n_qubits: int, shots: int = 4096) -> dict:
    """Prepare an entangled state and measure.

    Args:
        state_type: One of 'ghz', 'w', 'cluster'.
        n_qubits: Number of qubits.
        shots: Number of measurement shots.

    Returns:
        Dictionary with probability distribution.
    """
    c = Circuit(n_qubits)

    if state_type == "ghz":
        ghz_state(c)
    elif state_type == "w":
        w_state(c)
    elif state_type == "cluster":
        cluster_state(c)
    else:
        raise ValueError(f"Unknown state type: {state_type}")

    # Measure all qubits
    c.measure(*list(range(n_qubits)))

    # Simulate
    sim = QASM_Simulator(least_qubit_remapping=False)
    result = sim.simulate_shots(c.qasm, shots=shots)
    total = sum(result.values())
    probs = {f"{int(k):0{n_qubits}b}": v / total for k, v in result.items()}

    return dict(sorted(probs.items()))


def main():
    parser = argparse.ArgumentParser(description="Entangled State Preparation")
    parser.add_argument(
        "--state",
        type=str,
        default="ghz",
        choices=["ghz", "w", "cluster"],
        help="Type of entangled state",
    )
    parser.add_argument("--n-qubits", type=int, default=4, help="Number of qubits")
    parser.add_argument("--shots", type=int, default=4096, help="Number of shots")
    args = parser.parse_args()

    n = args.n_qubits
    state = args.state

    print(f" {state.upper()} State — {n} qubits")
    print()

    probs = run_state(state, n, args.shots)

    # Show only non-zero probabilities
    print(" Probability distribution:")
    for basis, p in probs.items():
        if p > 0.001:
            bar = "█" * int(p * 50)
            print(f"   |{basis}⟩: {p:.4f} {bar}")

    # Entanglement verification: show only dominant basis states
    dominant = {k: v for k, v in probs.items() if v > 0.01}
    print(f"\n Dominant basis states ({len(dominant)}):")
    for basis, p in sorted(dominant.items(), key=lambda x: -x[1]):
        print(f"   |{basis}⟩: {p:.4f}")


if __name__ == "__main__":
    main()
