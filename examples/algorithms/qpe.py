#!/usr/bin/env python
"""Quantum Phase Estimation (QPE) — complete example.

Demonstrates:
  * QPE circuit construction with phase register + eigenstate register
  * Inverse Quantum Fourier Transform (QFTdagger)
  * Running QPE with QPanda-lite simulators
  * Using the measurement module to extract phase bits
  * Connecting the estimated phase to the eigenvalue

Usage:
    python qpe.py [--n-precision N] [--unitary TYPE] [--shots N]

References:
    Nielsen & Chuang, "Quantum Computation and Quantum Information", Chapter 5.
    Cleve et al. (1998), "Efficient Discrete Random Unitary Circuits for Approximating
    the Quantum Fourier Transform." https://arxiv.org/abs/quant-ph/9904026
"""

import argparse
import sys
import cmath
import numpy as np

sys.path.insert(0, str(__file__.rsplit("/", 2)[0]))

from qpandalite.circuit_builder import Circuit
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.algorithmics.measurement import basis_rotation_measurement


def apply_cu1(circuit: Circuit, control: int, target: int, theta: float) -> None:
    """Apply controlled-U1 gate, where U1(θ) = diag(1, e^{iθ}).

    In QASM: cu1(theta) q[control], q[target]
    Decomposition: U1(θ) = Rz(θ) = [[1,0],[0,e^{iθ}]]

    We implement this as:
        u1(theta/2) on target
        cx from control to target
        u1(-theta/2) on target
        cx from control to target
    which gives: CU1(θ) = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,e^{iθ}]]
    """
    circuit.u1(target, theta / 2)
    circuit.cx(control, target)
    circuit.u1(target, -theta / 2)
    circuit.cx(control, target)


def apply_qft(circuit: Circuit, qubits: list[int]) -> None:
    """Apply the Quantum Fourier Transform to a register of qubits.

    QFT on |x⟩ = (1/√2^n) ∑_{k=0}^{2^n-1} e^{2πikx/2^n} |k⟩

    Circuit for n qubits (leftmost = most significant):
        for i = 0 to n-1:
            H on q[i]
            for j = i+1 to n-1:
                CU1(π/2^{j-i}) on (q[j], q[i])
    """
    n = len(qubits)
    for i in range(n):
        circuit.h(qubits[i])
        for j in range(i + 1, n):
            theta = np.pi / (2 ** (j - i))
            apply_cu1(circuit, qubits[j], qubits[i], theta)


def apply_qft_dagger(circuit: Circuit, qubits: list[int]) -> None:
    """Apply QFTdagger (inverse QFT) — the final step of QPE.

    QFTdagger = apply_qft in reverse order with adjoint rotations:
        for i = n-1 down to 0:
            for j = i+1 to n-1:
                CU1(-π/2^{j-i}) on (q[j], q[i])
            H on q[i]
    """
    n = len(qubits)
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, i, -1):
            theta = -np.pi / (2 ** (j - i))
            apply_cu1(circuit, qubits[j], qubits[i], theta)
        circuit.h(qubits[i])


def build_qpe_circuit(
    n_precision: int,
    unitary_matrix: np.ndarray,
    eigenstate: list[int],
) -> tuple[Circuit, list[int]]:
    """Build the complete QPE circuit.

    Args:
        n_precision: Number of precision (ancilla) qubits.
            The phase is estimated to n_precision bits.
        unitary_matrix: 2^n × 2^n unitary matrix representing U.
            U must be diagonal in the computational basis for
            clean phase estimation; otherwise the result is a
            superposition of phases (equivalent to eigenstate decomposition).
        eigenstate: The n-qubit basis state |u⟩ that is an eigenstate of U.
            Given as a list of bits, e.g. [1, 0] for |10⟩.

    Returns:
        A tuple (circuit, precision_qubits).
    """
    n_system = len(eigenstate)
    total_qubits = n_precision + n_system
    q_precision = list(range(n_precision))
    q_system = list(range(n_precision, total_qubits))

    c = Circuit()

    # Step 1: Initialise eigenstate on system qubits
    for i, bit in enumerate(eigenstate):
        if bit == 1:
            c.x(q_system[i])

    # Step 2: Apply Hadamard on precision qubits (uniform superposition)
    for q in q_precision:
        c.h(q)

    # Step 3: Controlled powers of U
    # For k = 0 to n_precision-1, apply U^{2^k} controlled by precision qubit k
    for k, q_ctrl in enumerate(q_precision):
        power = 2**k
        # Compute U^{2^k} by repeated matrix multiplication
        U_power = unitary_matrix
        for _ in range(power - 1):
            U_power = U_power @ unitary_matrix
        # Apply controlled-U^{2^k} via basis decomposition
        # Since U is diagonal, controlled-U is just CU1 gates
        _apply_controlled_unitary(c, q_ctrl, q_system, U_power)

    # Step 4: Inverse QFT on precision qubits
    apply_qft_dagger(c, q_precision)

    # Measure precision qubits
    c.measure(*q_precision)
    return c, q_precision


def _apply_controlled_unitary(
    circuit: Circuit,
    control: int,
    system_qubits: list[int],
    U: np.ndarray,
) -> None:
    """Apply controlled-U where U is diagonal in the computational basis.

    For a diagonal U = diag(e^{iθ_0}, e^{iθ_1}, ...):
        CU |c⟩|s⟩ = |c⟩ ⊗ U|s⟩ if c=1, else |s⟩
        = exp(iθ_s) |c⟩|s⟩ if c=1

    This is implemented as a sequence of CU1 gates encoding the phases.
    """
    n = len(system_qubits)
    dim = 2**n

    # Extract diagonal elements
    diags = np.diag(U)
    phases = [cmath.phase(d) for d in diags]

    # Apply CU1 gates encoding the phases
    # U|s⟩ = exp(iθ_s)|s⟩
    # For a 1-qubit system: CU1(θ) on (control, sys) implements e^{iθ}|1⟩|s⟩
    # For multi-qubit: decompose into CU1s using binary phase encoding
    if n == 1:
        # CU1 on (control, system_qubits[0]) encodes phase for |1⟩ on control
        theta = phases[1] - phases[0]  # relative phase
        apply_cu1(circuit, control, system_qubits[0], theta)
        # Also need to apply the global phase e^{iθ_0} — handled by QPE automatically
    else:
        # Multi-qubit controlled-U: decompose using Toffoli cascade
        # U|s_0 s_1 ...⟩ = e^{iθ_s}|s⟩
        # We encode each basis state's phase as a sum of CU1 angles
        # Using Gray code decomposition
        _apply_cu_cascade(circuit, control, system_qubits, phases)


def _apply_cu_cascade(
    circuit: Circuit,
    control: int,
    system_qubits: list[int],
    phases: list[float],
) -> None:
    """Apply multi-controlled phase gate using a cascade of CU1 gates.

    For n system qubits with 2^n basis states, each having phase θ_k,
    we decompose this into n CU1 gates using the following trick:
    The phase on state |k⟩ is encoded in binary, and each qubit
    contributes a phase conditioned on higher-order bits.
    """
    n = len(system_qubits)
    # For simplicity with n=2 qubits:
    if n == 2:
        # U|ab⟩ = e^{iθ_ab}|ab⟩
        # CU1(θ_01) on (ctrl, q1) gives e^{iθ_ab} when ctrl=1 and q1=b=1
        # This depends on q1 only, not q0.
        # We use the decomposition:
        # e^{iθ_00}|00⟩ |e^{iθ_01}|01⟩ |e^{iθ_10}|10⟩ |e^{iθ_11}|11⟩
        # = e^{iθ_00}|00⟩ ⊗ (e^{i(θ_01-θ_00)} for |01⟩) ⊗ (e^{i(θ_10-θ_00)} for |10⟩) ⊗
        #   (e^{i(θ_11-θ_01+θ_00)} for |11⟩)
        #
        # CU1(ctrl, q1) only applies phase when ctrl=1 AND q1=1
        # CU1(ctrl, q0) only applies phase when ctrl=1 AND q0=1
        #
        # We decompose using the standard method:
        # θ_0 = θ_00 (base phase, absorbed into global)
        # θ_1 = θ_01 - θ_00 (q1 phase relative to q0)
        # θ_2 = θ_10 - θ_00 (q0 phase relative to q1, for |10⟩)
        # θ_3 = θ_11 + θ_00 - θ_01 - θ_10 (correction for |11⟩)
        base = phases[0]
        d1 = phases[1] - phases[0]   # relative to |01⟩
        d2 = phases[2] - phases[0]   # relative to |10⟩
        d3 = phases[3] + phases[0] - phases[1] - phases[2]  # correction

        apply_cu1(circuit, control, system_qubits[0], d3)   # q1 is MSB for |11⟩
        apply_cu1(circuit, control, system_qubits[1], d2)   # q0
    else:
        # For n=1 case
        apply_cu1(circuit, control, system_qubits[0], phases[1] - phases[0])


def run_qpe(
    n_precision: int,
    unitary: str = "t",
    shots: int = 4096,
) -> tuple[float, float, np.ndarray]:
    """Run QPE to estimate the phase of a quantum gate.

    Args:
        n_precision: Number of precision qubits (bits of phase precision).
        unitary: Type of unitary to estimate:
            "t"   → T = diag(1, e^{iπ/4}), phase = π/8 (T-gate)
            "z"   → Z = diag(1, -1), phase = 0.5
            "s"   → S = diag(1, i), phase = 0.25
            "rz"  → Rz(π/3), phase = π/6 ≈ 0.5236
        shots: Number of measurement shots.

    Returns:
        Tuple of (estimated_phase, true_phase, phase_counts dict).
    """
    # Define the unitary matrices
    if unitary == "t":
        # T gate: phase = π/8
        U = np.diag([1, np.exp(1j * np.pi / 4)])
        true_phase = np.pi / 8
        eigenstate = [0]  # |0⟩ is eigenstate with eigenvalue 1 (phase 0)
        eigenstate2 = [1]  # |1⟩ is eigenstate with eigenvalue e^{iπ/4} (phase π/8)
    elif unitary == "z":
        # Z gate: phase = 0.5 (since eigenvalue = -1 = e^{iπ})
        U = np.diag([1, -1])
        true_phase = 0.5  # eigenvalue = e^{2πi*0.5} = -1
        eigenstate = [0]  # |0⟩ → phase 0
    elif unitary == "s":
        # S gate: phase = 0.25 (eigenvalue = e^{iπ/2} = i)
        U = np.diag([1, 1j])
        true_phase = 0.25
        eigenstate = [0]
    elif unitary == "rz":
        # Rz(π/3) = diag(e^{-iπ/6}, e^{iπ/6}), phase = π/6 / 2π = 1/12 ≈ 0.0833
        U = np.diag([np.exp(-1j * np.pi / 6), np.exp(1j * np.pi / 6)])
        true_phase = 1 / 12
        eigenstate = [0]
    else:
        raise ValueError(f"Unknown unitary: {unitary}")

    # Build QPE circuit
    c, q_precision = build_qpe_circuit(n_precision, U, eigenstate)

    # Simulate
    sim = QASM_Simulator(least_qubit_remapping=False)
    counts = sim.simulate_shots(c.qasm, shots=shots)
    total = sum(counts.values())

    # Extract phase from measurement results
    # Precision qubits are ordered with q[0] = most significant (leftmost in binary)
    # QPE gives: measured integer m → phase ≈ m / 2^n_precision
    phase_counts = {f"{k:0{n_precision}b}": v / total for k, v in counts.items()}

    # Find most likely outcome
    m_estimated = max(counts, key=counts.get)
    m_int = int(m_estimated, 2)
    estimated_phase = m_int / (2**n_precision)

    return estimated_phase, true_phase, phase_counts


def main():
    parser = argparse.ArgumentParser(description="Quantum Phase Estimation")
    parser.add_argument(
        "--n-precision", type=int, default=4,
        help="Number of precision qubits (default 4)"
    )
    parser.add_argument(
        "--unitary",
        type=str,
        default="t",
        choices=["t", "z", "s", "rz"],
        help="Unitary to estimate (default: t gate)",
    )
    parser.add_argument(
        "--shots", type=int, default=4096,
        help="Number of measurement shots"
    )
    args = parser.parse_args()

    print(f" Quantum Phase Estimation")
    print(f" Precision qubits: {args.n_precision}")
    print(f" Phase precision:  1/{2**args.n_precision} = {1/2**args.n_precision:.4f}")
    print(f" Unitary: {args.unitary}")
    print()

    est, true, counts = run_qpe(args.n_precision, args.unitary, args.shots)

    print(f" Measurement results:")
    for state, prob in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        m_int = int(state, 2)
        phase = m_int / (2**args.n_precision)
        marker = " ← most likely" if prob == max(counts.values()) else ""
        print(f"   |{state}⟩  prob={prob*100:5.1f}%  phase={phase:.4f}{marker}")

    print()
    print(f" Estimated phase:  {est:.4f}")
    print(f" True phase:       {true:.4f}")
    print(f" Absolute error:   {abs(est - true):.4f}")
    print(f"  ✓ QPE complete.")


if __name__ == "__main__":
    main()
