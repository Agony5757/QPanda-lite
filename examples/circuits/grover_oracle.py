#!/usr/bin/env python
"""Grover's search using the circuits module.

Demonstrates the full Grover search pipeline using
:func:`~qpandalite.algorithmics.circuits.grover_oracle` and
:func:`~qpandalite.algorithmics.circuits.grover_diffusion`.

Usage:
    python examples/circuits/grover_oracle.py [--n-qubits N] [--marked-state STATE] [--shots N]
"""

import argparse
import math
import sys

sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.circuits.grover_oracle import grover_oracle, grover_diffusion


def run_grover(n_qubits: int, marked_state: int, shots: int = 4096):
    """Run Grover's search and return measurement frequencies."""
    c = Circuit()

    # Uniform superposition on data qubits
    data_qubits = list(range(n_qubits))
    for q in data_qubits:
        c.h(q)

    # Optimal iterations
    n_iter = max(1, min(int(math.pi / 4 * math.sqrt(2**n_qubits)), 10))

    ancilla = None
    for _ in range(n_iter):
        ancilla = grover_oracle(c, marked_state=marked_state, qubits=data_qubits, ancilla=ancilla)
        grover_diffusion(c, qubits=data_qubits, ancilla=ancilla)

    c.measure(*data_qubits)

    sim = QASM_Simulator(least_qubit_remapping=False)
    result = sim.simulate_shots(c.qasm, shots=shots)
    total = sum(result.values())
    return {f"{k:0{n_qubits}b}": v / total for k, v in result.items()}, n_iter


def main():
    parser = argparse.ArgumentParser(description="Grover's Search (circuits module)")
    parser.add_argument("--n-qubits", type=int, default=3, help="Number of data qubits")
    parser.add_argument("--marked-state", type=int, default=5, help="Marked state index")
    parser.add_argument("--shots", type=int, default=4096, help="Measurement shots")
    args = parser.parse_args()

    n = args.n_qubits
    marked = args.marked_state
    if marked >= 2**n:
        print(f"Error: marked_state {marked} out of range for {n} qubits")
        sys.exit(1)

    print(f"  Grover's Search — {n} data qubits")
    print(f"  Marked state: {marked} ({marked:0{n}b})")
    print(f"  Search space: {2**n} states")
    print()

    result, n_iter = run_grover(n, marked, shots=args.shots)
    marked_str = f"{marked:0{n}b}"

    print(f"  Iterations: {n_iter}")
    print(f"  Results (top 5):")
    for state, prob in sorted(result.items(), key=lambda x: -x[1])[:5]:
        tag = " ← TARGET" if state == marked_str else ""
        print(f"    |{state}⟩  {prob*100:5.1f}%{tag}")

    print(f"\n  Target probability: {result.get(marked_str, 0)*100:.1f}%")
    print(f"  ✓ Done.")


if __name__ == "__main__":
    main()
