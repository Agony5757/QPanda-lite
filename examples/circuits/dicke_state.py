#!/usr/bin/env python
"""Dicke state preparation circuit — example.

Demonstrates the dicke_state_circuit building block for preparing
Dicke states |D(n,k)⟩ — equal superpositions of all n-bit strings
with exactly k ones.

Usage:
    python dicke_state.py [--n-qubits N] [--k K] [--shots N]
"""

import argparse
import sys
import math
from collections import Counter

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, __file__.rsplit("/", 2)[0])

import numpy as np

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.circuits import dicke_state_circuit


def run_dicke(n_qubits, k, shots):
    """Run Dicke state preparation and verify probability distribution."""
    c = Circuit(n_qubits)
    dicke_state_circuit(c, k=k)
    c.measure(list(range(n_qubits)))

    sim = QASM_Simulator()
    result = sim.simulate(c.to_qasm(), shots=shots)

    # Expected number of basis states with exactly k ones
    from math import comb
    n_expected = comb(n_qubits, k)
    expected_prob = 1.0 / n_expected

    total = sum(result.values())
    probs = {state: count / total for state, count in sorted(result.items())}

    print(f"Dicke State |D({n_qubits},{k})⟩ Preparation")
    print(f"Expected: {n_expected} basis states, each with probability {expected_prob:.6f}")
    print(f"\nMeasured probability distribution (shots={shots}):")
    print(f"  {'State':<12s} {'Measured':>10s} {'Weight':>8s} {'Theory':>10s}")
    print(f"  {'-'*12} {'-'*10} {'-'*8} {'-'*10}")

    correct_weight = 0
    for state, prob in probs.items():
        n_ones = bin(int(state, 2)).count("1")
        mark = "✓" if n_ones == k else "✗"
        if n_ones == k:
            correct_weight += prob
        print(f"  |{state}⟩  {prob:10.6f} {n_ones:>6d}{mark}  {expected_prob if n_ones == k else 0:10.6f}")

    print(f"\nTotal weight on Hamming-weight-{k} subspace: {correct_weight:.6f} (expected: 1.0)")


def main():
    parser = argparse.ArgumentParser(description="Dicke state preparation example")
    parser.add_argument("--n-qubits", type=int, default=4, help="Number of qubits (default: 4)")
    parser.add_argument("--k", type=int, default=2, help="Number of excitations (default: 2)")
    parser.add_argument("--shots", type=int, default=8192, help="Number of measurement shots (default: 8192)")
    args = parser.parse_args()

    if args.k < 1 or args.k > args.n_qubits:
        print(f"Error: k must satisfy 1 <= k <= n_qubits (got k={args.k}, n={args.n_qubits})")
        sys.exit(1)

    run_dicke(args.n_qubits, args.k, args.shots)


if __name__ == "__main__":
    main()
