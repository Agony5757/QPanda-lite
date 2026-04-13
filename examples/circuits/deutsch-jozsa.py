#!/usr/bin/env python
"""Deutsch-Jozsa algorithm — complete example.

Demonstrates:
  * Building constant and balanced oracles
  * Running the Deutsch-Jozsa algorithm
  * Distinguishing constant from balanced functions with a single query

Usage:
    python deutsch-jozsa.py [--n-qubits N] [--oracle-type TYPE] [--shots N]

References:
    Deutsch, D. & Jozsa, R. (1992). "Rapid solutions of problems by
    quantum computation." Proceedings of the Royal Society of London A.
"""

import argparse
import sys

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.circuits import deutsch_jozsa_circuit, deutsch_jozsa_oracle


def run_deutsch_jozsa(
    n_qubits: int,
    oracle_type: str = "balanced",
    shots: int = 4096,
) -> dict:
    """Run the Deutsch-Jozsa algorithm.

    Args:
        n_qubits: Number of data qubits.
        oracle_type: "constant" or "balanced".
        shots: Number of measurement shots.

    Returns:
        Dictionary mapping bit-strings to frequencies.
    """
    balanced = oracle_type == "balanced"
    oracle = deutsch_jozsa_oracle(n_qubits, balanced=balanced)

    c = Circuit(n_qubits + 1)
    deutsch_jozsa_circuit(c, oracle)

    sim = QASM_Simulator(least_qubit_remapping=False)
    result = sim.simulate_shots(c.qasm, shots=shots)
    total = sum(result.values())
    return {f"{int(k):0{n_qubits}b}": v / total for k, v in result.items()}


def main():
    parser = argparse.ArgumentParser(description="Deutsch-Jozsa Algorithm")
    parser.add_argument("--n-qubits", type=int, default=3, help="Number of data qubits")
    parser.add_argument(
        "--oracle-type",
        choices=["constant", "balanced"],
        default="balanced",
        help="Oracle type (default: balanced)",
    )
    parser.add_argument("--shots", type=int, default=4096, help="Number of shots")
    args = parser.parse_args()

    n = args.n_qubits
    otype = args.oracle_type

    print(f" Deutsch-Jozsa Algorithm — {n} data qubits")
    print(f" Oracle type: {otype}")
    print()

    result = run_deutsch_jozsa(n, oracle_type=otype, shots=args.shots)

    all_zero = "0" * n
    zero_prob = result.get(all_zero, 0.0)

    sorted_results = sorted(result.items(), key=lambda x: x[1], reverse=True)
    print(f" Results (top outcomes):")
    for bitstr, freq in sorted_results[:5]:
        marker = " ← all zeros" if bitstr == all_zero else ""
        print(f"   |{bitstr}⟩  {freq * 100:5.1f}%{marker}")

    print()
    if zero_prob > 0.9:
        print(f"  → CONSTANT function (all measurements = |{all_zero}⟩)")
    else:
        print(f"  → BALANCED function (non-zero measurements detected)")

    print()
    print(f"  ✓ Run complete.")


if __name__ == "__main__":
    main()
