#!/usr/bin/env python
"""Quantum Amplitude Estimation (QAE) — complete example.

Demonstrates:
  * Building a simple oracle for amplitude estimation
  * Running QAE to estimate the probability of "good" states
  * Using the amplitude_estimation_result function to extract the estimate

Usage:
    python amplitude_estimation.py [--n-qubits N] [--n-eval-qubits M] [--shots N]

References:
    Brassard, G., Høyer, P., Mosca, M. & Tapp, A. (2002).
    "Quantum Amplitude Amplification and Estimation."
    AMS Contemporary Mathematics, 305, 53–74.
"""

import argparse
import sys
import math

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.circuits import (
    amplitude_estimation_circuit,
    amplitude_estimation_result,
)


def build_simple_oracle(n_qubits: int, marked_state: int) -> Circuit:
    """Build a phase-flip oracle that marks a specific computational basis state.

    Flips the phase of |marked_state⟩ by:
    1. X gates on qubits where marked_state has 0
    2. Multi-controlled Z on all qubits
    3. Undo X gates

    Args:
        n_qubits: Number of qubits in the search register.
        marked_state: Integer representing the marked basis state.

    Returns:
        Oracle circuit.
    """
    oracle = Circuit(n_qubits)
    bits = format(marked_state, f"0{n_qubits}b")

    # Flip qubits where bit is 0
    for i, bit in enumerate(bits):
        if bit == "0":
            oracle.x(i)

    # Apply multi-controlled Z
    if n_qubits == 1:
        oracle.z(0)
    elif n_qubits == 2:
        oracle.cz(0, 1)
    else:
        # For n > 2, use toffoli cascade
        oracle.h(n_qubits - 1)
        oracle.toffoli(0, 1, n_qubits - 1)
        oracle.h(n_qubits - 1)

    # Undo X flips
    for i, bit in enumerate(bits):
        if bit == "0":
            oracle.x(i)

    return oracle


def run_qae(n_qubits: int, n_eval_qubits: int, marked_state: int, shots: int = 4096) -> dict:
    """Run QAE and return results.

    Args:
        n_qubits: Number of search register qubits.
        n_eval_qubits: Number of evaluation qubits (precision).
        marked_state: The marked state for the oracle.
        shots: Number of measurement shots.

    Returns:
        Dictionary with estimated probability and measurement counts.
    """
    total_qubits = n_qubits + n_eval_qubits
    oracle = build_simple_oracle(n_qubits, marked_state)

    c = Circuit(total_qubits)
    amplitude_estimation_circuit(
        c,
        oracle,
        qubits=list(range(n_eval_qubits, total_qubits)),
        n_eval_qubits=n_eval_qubits,
    )

    # Simulate
    sim = QASM_Simulator(least_qubit_remapping=False)
    result = sim.simulate_shots(c.qasm, shots=shots)

    # Convert to bit-strings
    counts = {f"{int(k):0{n_eval_qubits}b}": v for k, v in result.items()}

    # Estimate amplitude
    estimated_a = amplitude_estimation_result(counts, n_eval_qubits)

    # True probability (for uniform superposition with one marked state)
    true_a = 1.0 / (2 ** n_qubits)

    return {
        "estimated": estimated_a,
        "true": true_a,
        "counts": counts,
    }


def main():
    parser = argparse.ArgumentParser(description="Quantum Amplitude Estimation (QAE)")
    parser.add_argument("--n-qubits", type=int, default=2, help="Number of search qubits")
    parser.add_argument(
        "--n-eval-qubits", type=int, default=3, help="Number of evaluation qubits"
    )
    parser.add_argument("--shots", type=int, default=4096, help="Number of shots")
    args = parser.parse_args()

    n = args.n_qubits
    m = args.n_eval_qubits
    marked = 0  # Mark |0...0⟩

    print(f" Quantum Amplitude Estimation")
    print(f" Search qubits: {n}, Eval qubits: {m}")
    print(f" Marked state: |{marked:0{n}b}⟩")
    print()

    result = run_qae(n, m, marked, args.shots)

    print(f" Estimated probability: {result['estimated']:.6f}")
    print(f" True probability:      {result['true']:.6f}")
    print(f" Error:                 {abs(result['estimated'] - result['true']):.6f}")
    print()
    print(" Measurement counts (eval register):")
    for outcome, count in sorted(result["counts"].items()):
        print(f"   |{outcome}⟩: {count}")


if __name__ == "__main__":
    main()
