#!/usr/bin/env python
"""Thermal state preparation circuit — example.

Demonstrates the thermal_state_circuit building block for preparing
thermal (Gibbs) states of H = Σ Z_i at various inverse temperatures β.

Usage:
    python thermal_state.py [--n-qubits N] [--beta BETA] [--shots N]
"""

import argparse
import sys
import math
import numpy as np

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, __file__.rsplit("/", 2)[0])

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.circuits import thermal_state_circuit


def run_thermal(n_qubits, beta, shots):
    """Run thermal state preparation and print probability distribution."""
    c = Circuit(n_qubits)
    thermal_state_circuit(c, beta=beta)
    c.measure(list(range(n_qubits)))

    sim = QASM_Simulator()
    result = sim.simulate(c.to_qasm(), shots=shots)

    # Aggregate counts into probability distribution
    total = sum(result.values())
    probs = {state: count / total for state, count in sorted(result.items())}

    # Theoretical distribution
    exp_b = math.exp(beta)
    exp_nb = math.exp(-beta)
    p0 = exp_b / (exp_b + exp_nb)
    p1 = 1 - p0

    print(f"Thermal State Preparation — {n_qubits} qubits, β = {beta}")
    print(f"Single-qubit probabilities: p₀ = {p0:.6f}, p₁ = {p1:.6f}")
    print(f"\nMeasured probability distribution (shots={shots}):")
    print(f"  {'State':<12s} {'Measured':>10s} {'Theory':>10s}")
    print(f"  {'-'*12} {'-'*10} {'-'*10}")

    for state, prob in probs.items():
        # Compute theoretical probability for this basis state
        n_ones = bin(int(state, 2)).count("1") if state else 0
        n_zeros = n_qubits - n_ones
        theory = p0 ** n_zeros * p1 ** n_ones
        print(f"  |{state}⟩  {prob:10.6f} {theory:10.6f}")


def main():
    parser = argparse.ArgumentParser(description="Thermal state preparation example")
    parser.add_argument("--n-qubits", type=int, default=3, help="Number of qubits (default: 3)")
    parser.add_argument("--beta", type=float, default=1.0, help="Inverse temperature β (default: 1.0)")
    parser.add_argument("--shots", type=int, default=8192, help="Number of measurement shots (default: 8192)")
    args = parser.parse_args()

    run_thermal(args.n_qubits, args.beta, args.shots)


if __name__ == "__main__":
    main()
