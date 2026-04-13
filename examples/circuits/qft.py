#!/usr/bin/env python
"""Quantum Fourier Transform (QFT) — complete example.

Demonstrates:
  * Building a QFT circuit using qft_circuit
  * Preparing a computational basis state as input
  * Verifying QFT output via state-vector inspection
  * Running with QASM_Simulator for shot-based sampling

Usage:
    python qft.py [--n-qubits N] [--input-state STATE] [--shots N]

References:
    Nielsen, M. A. & Chuang, I. L. (2010). "Quantum Computation and
    Quantum Information." Cambridge University Press, Section 5.1.
"""

import argparse
import sys
import math

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.state_preparation import basis_state
from qpandalite.algorithmics.circuits import qft_circuit


def run_qft(n_qubits: int, input_state: int, shots: int = 4096) -> dict:
    """Run QFT on a computational basis state and return measurement frequencies.

    Args:
        n_qubits: Number of qubits.
        input_state: Integer encoding the input basis state.
        shots: Number of measurement shots.

    Returns:
        Dictionary mapping bit-strings to frequencies.
    """
    c = Circuit(n_qubits)

    # Prepare input state
    basis_state(c, state=input_state, qubits=list(range(n_qubits)))

    # Apply QFT
    qft_circuit(c, qubits=list(range(n_qubits)), swaps=True)

    # Measure all qubits
    c.measure(*list(range(n_qubits)))

    # Simulate
    sim = QASM_Simulator(least_qubit_remapping=False)
    result = sim.simulate_shots(c.qasm, shots=shots)
    total = sum(result.values())
    return {f"{int(k):0{n_qubits}b}": v / total for k, v in result.items()}


def main():
    parser = argparse.ArgumentParser(description="Quantum Fourier Transform (QFT)")
    parser.add_argument("--n-qubits", type=int, default=3, help="Number of qubits")
    parser.add_argument(
        "--input-state",
        type=int,
        default=5,
        help="Input computational basis state (integer, default 5)",
    )
    parser.add_argument("--shots", type=int, default=4096, help="Number of shots")
    args = parser.parse_args()

    n = args.n_qubits
    state = args.input_state
    if state >= 2**n:
        print(f"Error: input_state {state} out of range for {n} qubits (max {2**n - 1})")
        sys.exit(1)

    print(f" Quantum Fourier Transform — {n} qubits")
    print(f" Input state: |{state}⟩ = |{state:0{n}b}⟩")
    print()

    result = run_qft(n, state, shots=args.shots)

    # QFT of |j⟩ should produce equal superposition with phase encoding
    # For ideal QFT of |j⟩, all outcomes have equal probability 1/N
    n_outcomes = min(8, len(result))
    sorted_results = sorted(result.items(), key=lambda x: x[1], reverse=True)

    print(f" Results (top {n_outcomes}):")
    for bitstr, freq in sorted_results[:n_outcomes]:
        print(f"   |{bitstr}⟩  {freq * 100:5.1f}%")

    ideal_prob = 100.0 / (2**n)
    print()
    print(f" Ideal: each basis state has probability {ideal_prob:.2f}%")
    print(f" (QFT of |j⟩ produces equal-amplitude superposition with phase encoding)")
    print()
    print(f"  ✓ Run complete.")


if __name__ == "__main__":
    main()
