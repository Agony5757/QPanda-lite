#!/usr/bin/env python
"""Full quantum state tomography — measurement example.

Demonstrates:
  * Reconstructing the density matrix via state tomography
  * Computing fidelity with the target state
  * Comparing tomography result with exact statevector

Usage:
    python state_tomography.py [--n-shots N]

References:
    James et al. (2001). "Measurement of qubits." Physical Review A 64, 052312.
"""

import argparse
import sys
import numpy as np

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.measurement import state_tomography, tomography_summary


def run_tomography_demo(n_shots=2000):
    """Demonstrate full quantum state tomography.

    Args:
        n_shots: Number of shots per measurement basis.
    """
    print("Full State Tomography Demo")
    print("=" * 50)
    print(f"  Shots per basis: {n_shots}")

    # Build a test circuit: prepare a specific state
    # |ψ⟩ = (|00⟩ + i|11⟩)/√2  (Bell-like state with phase)
    c = Circuit()
    c.h(0)
    c.cx(0, 1)
    c.rz(1, np.pi / 2)

    print(f"\nCircuit: (|00⟩ + i|11⟩)/√2")

    # Perform tomography
    print(f"\nRunning tomography (3^2 = 9 measurement bases for 2 qubits)...")
    results = state_tomography(c, qubits=[0, 1], shots=n_shots)

    # Get summary
    summary = tomography_summary(results, n_qubits=2)
    print(f"\nTomography complete.")
    print(f"  Number of measurement bases: {len(results)}")
    print(f"  Density matrix shape: {summary.shape}")

    # Compare with exact statevector
    from qpandalite.simulator.originir_simulator import OriginIR_Simulator
    sim = OriginIR_Simulator(backend_type="statevector")
    sv = sim.simulate_statevector(c.originir)
    exact_rho = np.outer(sv, sv.conj())

    # Compute fidelity
    fidelity = np.real(np.sqrt(sv.conj() @ summary @ sv)) ** 2
    print(f"\n  Fidelity with exact state: {fidelity:.6f}")
    print(f"  Trace of reconstructed ρ: {np.real(np.trace(summary)):.6f}")

    # Show diagonal (populations)
    print(f"\n  Populations:")
    for i in range(4):
        basis = format(i, "02b")
        pop_exact = np.real(exact_rho[i, i])
        pop_tomo = np.real(summary[i, i])
        print(f"    |{basis}⟩: exact={pop_exact:.4f}, tomography={pop_tomo:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="State tomography demo")
    parser.add_argument("--n-shots", type=int, default=2000, help="Shots per basis")
    args = parser.parse_args()
    run_tomography_demo(n_shots=args.n_shots)
