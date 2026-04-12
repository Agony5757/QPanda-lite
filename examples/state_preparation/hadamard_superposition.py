#!/usr/bin/env python
"""Hadamard superposition — state preparation example.

Demonstrates:
  * Creating uniform superposition states with hadamard_superposition
  * Verifying state correctness via statevector simulation
  * Visualising the probability distribution

Usage:
    python hadamard_superposition.py [--n-qubits N]

References:
    Nielsen & Chuang (2010). "Quantum Computation and Quantum Information."
    Chapter 1.
"""

import argparse
import sys
import numpy as np

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.originir_simulator import OriginIR_Simulator
from qpandalite.algorithmics.state_preparation import hadamard_superposition


def run_hadamard_demo(n_qubits=3):
    """Demonstrate Hadamard superposition state preparation.

    Args:
        n_qubits: Number of qubits to put in superposition.
    """
    print(f"Hadamard Superposition Demo ({n_qubits} qubits)")
    print("=" * 50)

    # 1. Create uniform superposition on all qubits
    c = Circuit()
    hadamard_superposition(c, qubits=list(range(n_qubits)))

    sim = OriginIR_Simulator(backend_type="statevector")
    sv = sim.simulate_statevector(c.originir)

    print(f"\nState vector ({len(sv)} amplitudes):")
    expected_amp = 1.0 / np.sqrt(2**n_qubits)
    for i, amp in enumerate(sv):
        basis = format(i, f"0{n_qubits}b")
        print(f"  |{basis}⟩: {amp.real:+.4f} (expected: {expected_amp:+.4f})")

    print(f"\nProbabilities:")
    probs = np.abs(sv) ** 2
    for i, p in enumerate(probs):
        basis = format(i, f"0{n_qubits}b")
        bar = "█" * int(p * 40)
        print(f"  |{basis}⟩: {p:.4f} {bar}")

    # Verify uniformity
    print(f"\nAll amplitudes equal? {np.allclose(np.abs(sv), expected_amp)}")
    print(f"Total probability: {np.sum(probs):.6f}")

    # 2. Hadamard on subset of qubits
    if n_qubits >= 3:
        print(f"\n--- Subset: qubits [0, 2] only ---")
        c2 = Circuit()
        # Touch all qubits to ensure correct allocation
        for i in range(n_qubits):
            c2.x(i); c2.x(i)
        c3 = Circuit()
        for i in range(n_qubits):
            c3.x(i); c3.x(i)
        hadamard_superposition(c3, qubits=[0, 2])

        # Touch qubit 1 to ensure allocation
        c3.x(1); c3.x(1)

        sim2 = OriginIR_Simulator(backend_type="statevector", least_qubit_remapping=False)
        sv2 = sim2.simulate_statevector(c3.originir)
        probs2 = np.abs(sv2) ** 2
        for i, p in enumerate(probs2):
            if p > 0.001:
                basis = format(i, f"0{n_qubits}b")
                print(f"  |{basis}⟩: {p:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hadamard superposition demo")
    parser.add_argument("--n-qubits", type=int, default=3, help="Number of qubits")
    args = parser.parse_args()
    run_hadamard_demo(n_qubits=args.n_qubits)
