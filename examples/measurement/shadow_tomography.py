#!/usr/bin/env python
"""Classical Shadow tomography — measurement example.

Demonstrates:
  * Using classical_shadow for efficient state characterisation
  * Computing shadow expectation values
  * Comparing shadow estimates with exact statevector

Usage:
    python shadow_tomography.py [--n-shots N] [--n-shadow N]

References:
    Huang, Kueng, Preskill (2020). "Predicting many properties of a quantum
    system from very few measurements." Nature Physics 16, 1050–1057.
"""

import argparse
import sys
import numpy as np

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.measurement import classical_shadow, shadow_expectation


def run_shadow_demo(n_shots=1000, n_shadow=100):
    """Demonstrate Classical Shadow tomography.

    Args:
        n_shots: Shots per measurement basis.
        n_shadow: Number of shadow snapshots.
    """
    print("Classical Shadow Tomography Demo")
    print("=" * 50)
    print(f"  Shots per basis: {n_shots}")
    print(f"  Shadow snapshots: {n_shadow}")

    # Build a simple test circuit: Bell state |Φ⁺⟩
    c = Circuit()
    c.h(0)
    c.cx(0, 1)

    print(f"\nCircuit: Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")

    # 1. Perform classical shadow measurement
    print(f"\nPerforming {n_shadow} shadow measurements...")
    shadows = classical_shadow(c, qubits=[0, 1], shots=n_shots, n_shadow=n_shadow)
    print(f"  Collected {len(shadows)} shadow snapshots")

    # 2. Estimate ⟨Z₀⟩
    obs_z0 = {"Z0": 1.0}
    est_z0 = shadow_expectation(shadows, obs_z0)
    print(f"\n  ⟨Z₀⟩ estimate: {est_z0:.4f} (exact: 0.0)")

    # 3. Estimate ⟨Z₀Z₁⟩
    obs_z0z1 = {"Z0Z1": 1.0}
    est_z0z1 = shadow_expectation(shadows, obs_z0z1)
    print(f"  ⟨Z₀Z₁⟩ estimate: {est_z0z1:.4f} (exact: 1.0)")

    # 4. Estimate ⟨X₀⟩
    obs_x0 = {"X0": 1.0}
    est_x0 = shadow_expectation(shadows, obs_x0)
    print(f"  ⟨X₀⟩ estimate: {est_x0:.4f} (exact: 1/√2 ≈ 0.707)")

    # 5. Compare with exact values
    from qpandalite.simulator.originir_simulator import OriginIR_Simulator
    sim = OriginIR_Simulator(backend_type="statevector")
    sv = sim.simulate_statevector(c.originir)

    Z = np.array([[1, 0], [0, -1]])
    I = np.eye(2)
    exact_z0 = np.real(sv.conj() @ np.kron(Z, I) @ sv)
    exact_z0z1 = np.real(sv.conj() @ np.kron(Z, Z) @ sv)

    print(f"\n  Exact ⟨Z₀⟩ = {exact_z0:.4f}")
    print(f"  Exact ⟨Z₀Z₁⟩ = {exact_z0z1:.4f}")

    print(f"\n✓ Shadow estimation complete with {n_shadow} snapshots")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classical Shadow tomography demo")
    parser.add_argument("--n-shots", type=int, default=1000, help="Shots per basis")
    parser.add_argument("--n-shadow", type=int, default=100, help="Shadow snapshots")
    args = parser.parse_args()
    run_shadow_demo(n_shots=args.n_shots, n_shadow=args.n_shadow)
