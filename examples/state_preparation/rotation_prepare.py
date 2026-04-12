#!/usr/bin/env python
"""Arbitrary state preparation via rotation — example.

Demonstrates:
  * Preparing specific target states using rotation_prepare
  * Bell state, GHZ state, and random state preparation
  * Verifying fidelity of prepared states

Usage:
    python rotation_prepare.py [--state TYPE]

References:
    Shende, Bullock, Markov (2006). "Synthesis of Quantum Logic Circuits."
    IEEE Transactions on CAD 25(6).
"""

import argparse
import sys
import numpy as np

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.originir_simulator import OriginIR_Simulator
from qpandalite.algorithmics.state_preparation import rotation_prepare


def _fidelity(sv1, sv2):
    """Compute fidelity |⟨ψ₁|ψ₂⟩|²."""
    return abs(np.dot(sv1.conj(), sv2)) ** 2


def bell_state():
    """Prepare and verify a Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2."""
    target = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    c = Circuit()
    rotation_prepare(c, target)
    return target, c


def ghz_state(n):
    """Prepare a GHZ state (|0...0⟩ + |1...1⟩)/√2."""
    d = 2**n
    target = np.zeros(d, dtype=complex)
    target[0] = 1.0 / np.sqrt(2)
    target[-1] = 1.0 / np.sqrt(2)
    c = Circuit()
    rotation_prepare(c, target)
    return target, c


def w_state(n):
    """Prepare a W state: equal superposition of all single-excitation basis states."""
    d = 2**n
    target = np.zeros(d, dtype=complex)
    amp = 1.0 / np.sqrt(n)
    for i in range(n):
        target[1 << i] = amp
    c = Circuit()
    rotation_prepare(c, target)
    return target, c


def random_state(n):
    """Prepare a random normalised state."""
    rng = np.random.default_rng(42)
    d = 2**n
    vec = rng.standard_normal(d) + 1j * rng.standard_normal(d)
    target = vec / np.linalg.norm(vec)
    c = Circuit()
    rotation_prepare(c, target)
    return target, c


def run_demo(state_type="bell"):
    """Run the rotation state preparation demo."""
    print("Rotation-Based State Preparation")
    print("=" * 50)

    sim = OriginIR_Simulator(backend_type="statevector")

    if state_type == "bell":
        target, circuit = bell_state()
        sv = sim.simulate_statevector(circuit.originir)
        print(f"\nBell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
        print(f"  Fidelity: {_fidelity(sv, target):.8f}")
        for i, amp in enumerate(sv):
            print(f"  |{i:02b}⟩: {amp:+.4f}")

    elif state_type == "ghz":
        n = 3
        target, circuit = ghz_state(n)
        sv = sim.simulate_statevector(circuit.originir)
        print(f"\nGHZ state (n={n})")
        print(f"  Fidelity: {_fidelity(sv, target):.8f}")
        for i, amp in enumerate(sv):
            if abs(amp) > 0.001:
                print(f"  |{i:03b}⟩: {amp:+.4f}")

    elif state_type == "w":
        n = 3
        target, circuit = w_state(n)
        sv = sim.simulate_statevector(circuit.originir)
        print(f"\nW state (n={n})")
        print(f"  Fidelity: {_fidelity(sv, target):.8f}")
        for i, amp in enumerate(sv):
            if abs(amp) > 0.001:
                print(f"  |{i:03b}⟩: {amp:+.4f}")

    elif state_type == "random":
        n = 3
        target, circuit = random_state(n)
        sv = sim.simulate_statevector(circuit.originir)
        print(f"\nRandom state (n={n})")
        print(f"  Fidelity: {_fidelity(sv, target):.8f}")

    print(f"\nCircuit:\n{circuit.originir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotation state preparation demo")
    parser.add_argument("--state", default="bell",
                        choices=["bell", "ghz", "w", "random"],
                        help="State type to prepare")
    args = parser.parse_args()
    run_demo(state_type=args.state)
