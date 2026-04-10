#!/usr/bin/env python
"""Grover's search algorithm — complete example.

Demonstrates:
  * Oracle construction for an n-qubit Grover search
  * Diffusion operator (amplitude amplification)
  * Running the algorithm with QPanda-lite simulators
  * Using the measurement module for result analysis

Usage:
    python grover.py [--n-qubits N] [--marked-state STATE] [--shots N]

References:
    Grover, L. K. (1996). "A fast quantum mechanical algorithm
    for database search." STOC '96.
    https://arxiv.org/abs/quant-ph/9605043
"""

import argparse
import sys
import math
import numpy as np

# Add parent directory to path so we can import qpandalite when running as a script
sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.measurement import pauli_expectation


def build_oracle(n_qubits: int, marked_state: int) -> tuple[Circuit, list[int]]:
    """Build a Grover oracle that flips the phase of the marked basis state.

    The oracle applies a Z gate on an ancilla qubit (last qubit) conditioned
    on all data qubits being in the marked state.  This implements the standard
    phase-kickback oracle:

        U_φ|x⟩|−⟩ = (−1)^{[x==marked]}|x⟩|−⟩

    where |−⟩ = (|0⟩−|1⟩)/√2 is the ancilla in the magic basis.

    Args:
        n_qubits: Number of data qubits.
        marked_state: Integer encoding the marked basis state (0 to 2^n−1).

    Returns:
        A tuple of (circuit, ancilla_qubits) where ancilla_qubits is the
        list containing the ancilla qubit index.
    """
    total_qubits = n_qubits + 1
    c = Circuit()

    # Initialise ancilla to |−⟩ = X·H·|0⟩
    c.x(n_qubits)
    c.h(n_qubits)

    # Apply multi-controlled Z (MCZ) targeting the ancilla qubit
    # This flips the ancilla phase iff all data qubits are in |1⟩
    # We achieve this with a CCZ (Toffoli equivalent) followed by some X gates
    # to encode the marked-state condition.
    #
    # Strategy: flip data qubits that are |0⟩ in the marked state,
    # then apply MCZ from all data qubits to ancilla, then flip back.
    marked_bits = [(marked_state >> (n_qubits - 1 - i)) & 1 for i in range(n_qubits)]

    # Flip qubits that should be |0⟩ in the marked state
    for i, bit in enumerate(marked_bits):
        if bit == 0:
            c.x(i)

    # Apply multi-controlled Z gate to ancilla
    # We use a sequence of Toffoli (CCX) gates to implement MCZ
    # For n data qubits, we need n-1 ancillas for an efficient MCZ
    # Here we use a simpler approach: apply CCZ if n_qubits=2, or chain Toffolis
    if n_qubits == 1:
        c.cz(i=n_qubits, target=n_qubits)
    elif n_qubits == 2:
        c.ccx(0, 1, n_qubits)
        c.z(n_qubits)  # CCZ = CCX with final Z
        c.ccx(0, 1, n_qubits)
    else:
        # General multi-controlled Z using multiple Toffoli stages
        # MCZ: apply CNOT cascade then H on target then CNOT cascade
        # Using the standard linear-depth circuit
        _apply_mcz(c, list(range(n_qubits)), n_qubits)

    # Flip back
    for i, bit in enumerate(marked_bits):
        if bit == 0:
            c.x(i)

    # Return circuit with measurements on data qubits only
    c.measure(*list(range(n_qubits)))
    return c, list(range(n_qubits))


def _apply_mcz(circuit: Circuit, controls: list[int], target: int) -> None:
    """Apply multi-controlled Z gate using the standard linear-depth circuit.

    Circuit:
        (H on target)
        CNOT cascade up
        CNOT cascade down
        (H on target)

    This is equivalent to applying Z on the target iff all controls are |1⟩.
    """
    n = len(controls)
    if n == 0:
        circuit.z(target)
        return
    if n == 1:
        circuit.cz(controls[0], target)
        return

    # H on target
    circuit.h(target)

    # Cascade CNOTs from controls to target
    circuit.cx(controls[0], controls[1])
    for i in range(1, n - 1):
        circuit.cx(controls[i], controls[i + 1])
    circuit.cx(controls[-1], target)

    # Cascade back
    for i in range(n - 2, 0, -1):
        circuit.cx(controls[i], controls[i + 1])
    circuit.cx(controls[0], controls[1])

    # H on target
    circuit.h(target)


def build_diffusion(n_qubits: int) -> Circuit:
    """Build the Grover diffusion operator for amplitude amplification.

    D = H^{⊗n} · Z · H^{⊗n} · A_0

    where A_0 = H^{⊗n}·Z^{⊗n} is the initialisation (uniform superposition).
    D = 2|s⟩⟨s| − I where |s⟩ = H^{⊗n}|0⟩^{⊗n}.

    Args:
        n_qubits: Number of qubits.

    Returns:
        A Circuit implementing the diffusion operator.
    """
    c = Circuit()
    # Apply Hadamard to all
    for i in range(n_qubits):
        c.h(i)
    # Apply X to all
    for i in range(n_qubits):
        c.x(i)
    # Multi-controlled Z (phase flip)
    if n_qubits == 1:
        c.z(0)
    elif n_qubits == 2:
        c.ccx(0, 1, n_qubits)
        c.z(n_qubits)
        c.ccx(0, 1, n_qubits)
    else:
        # Use ancilla at position n_qubits as target for MCZ
        _apply_mcz(c, list(range(n_qubits)), n_qubits)
    # Flip back X
    for i in range(n_qubits):
        c.x(i)
    # Flip back H
    for i in range(n_qubits):
        c.h(i)
    return c


def run_grover(
    n_qubits: int,
    marked_state: int,
    shots: int = 4096,
) -> dict[str, float]:
    """Run Grover's search for the given marked state.

    Args:
        n_qubits: Number of data qubits (search space = 2^n qubits).
        marked_state: The integer index of the target state.
        shots: Number of measurement shots.

    Returns:
        Dictionary of measurement outcome frequencies.
    """
    total_qubits = n_qubits + 1

    # Initialise all data qubits to |+⟩ (uniform superposition)
    c = Circuit()
    for i in range(n_qubits):
        c.h(i)

    # Optimal number of Grover iterations
    n_iterations = int(math.pi / 4 * math.sqrt(2**n_qubits))
    n_iterations = max(1, min(n_iterations, 10))  # cap for small n

    for _ in range(n_iterations):
        # Oracle
        oracle_c = Circuit()
        for i in range(n_qubits):
            oracle_c.cx(i, n_qubits)  # CCNOT-style phase flip
        # Marked-state flip: flip the marked state's amplitude
        # We encode the marked state as a sequence of X gates
        marked_bits = [(marked_state >> (n_qubits - 1 - i)) & 1 for i in range(n_qubits)]
        for i, bit in enumerate(marked_bits):
            if bit == 0:
                oracle_c.x(i)
        oracle_c.ccx(0, 1, n_qubits)
        oracle_c.z(n_qubits)
        oracle_c.ccx(0, 1, n_qubits)
        for i, bit in enumerate(marked_bits):
            if bit == 0:
                oracle_c.x(i)
        # (End oracle)

        # Diffusion
        for i in range(n_qubits):
            oracle_c.h(i)
        for i in range(n_qubits):
            oracle_c.x(i)
        if n_qubits == 2:
            oracle_c.ccx(0, 1, n_qubits)
            oracle_c.z(n_qubits)
            oracle_c.ccx(0, 1, n_qubits)
        else:
            _apply_mcz(oracle_c, list(range(n_qubits)), n_qubits)
        for i in range(n_qubits):
            oracle_c.x(i)
        for i in range(n_qubits):
            oracle_c.h(i)

    c.extend(oracle_c)
    c.measure(*list(range(n_qubits)))

    # Simulate
    sim = QASM_Simulator(least_qubit_remapping=False)
    result = sim.simulate_shots(c.qasm, shots=shots)
    total = sum(result.values())
    return {f"{k:0{n_qubits}b}": v / total for k, v in result.items()}


def main():
    parser = argparse.ArgumentParser(description="Grover's Search Algorithm")
    parser.add_argument("--n-qubits", type=int, default=3, help="Number of data qubits")
    parser.add_argument(
        "--marked-state",
        type=int,
        default=5,
        help="Integer index of the marked state (0 to 2^n−1)",
    )
    parser.add_argument("--shots", type=int, default=4096, help="Number of shots")
    args = parser.parse_args()

    n = args.n_qubits
    marked = args.marked_state
    if marked >= 2**n:
        print(f"Error: marked_state {marked} is out of range for {n} qubits (max {2**n-1})")
        sys.exit(1)

    print(f" Grover's Search — {n} data qubits")
    print(f" Marked state: {marked} ({marked:0{n}b})")
    print(f" Search space: {2**n} states")
    print()

    result = run_grover(n, marked, shots=args.shots)

    marked_str = f"{marked:0{n}b}"
    marked_prob = result.get(marked_str, 0.0)

    print(f" Results (top 5 most probable states):")
    sorted_results = sorted(result.items(), key=lambda x: x[1], reverse=True)
    for state, prob in sorted_results[:5]:
        marker = " ← TARGET" if state == marked_str else ""
        print(f"   |{state}⟩  {prob*100:5.1f}%{marker}")

    print()
    print(f" Target probability: {marked_prob*100:.1f}%")
    print(f" Expected (ideal): ~{95.0:.1f}% (after optimal iterations)")
    print()
    print(f"  ✓ Run complete.")


if __name__ == "__main__":
    main()
