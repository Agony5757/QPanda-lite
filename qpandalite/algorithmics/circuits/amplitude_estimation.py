"""Quantum Amplitude Estimation (QAE) circuit."""

__all__ = [
    "amplitude_estimation_circuit",
    "amplitude_estimation_result",
    "grover_operator",
]

from typing import List, Optional
import math

from qpandalite.circuit_builder import Circuit


def _copy_circuit_gates(src: Circuit, dst: Circuit) -> None:
    """Copy all gates from src circuit into dst circuit."""
    for op in src.opcode_list:
        dst.opcode_list.append(op)
        dst.record_qubit(
            op[1] if isinstance(op[1], list) else [op[1]]
        )


def _copy_circuit_gates_controlled(
    src: Circuit,
    dst: Circuit,
    control_qubit: int,
) -> None:
    """Copy all gates from src circuit into dst, each controlled by control_qubit."""
    for op in src.opcode_list:
        op_name, qubits, cbits, params, dagger, ctrl = op
        # Merge existing controls with new control qubit
        if ctrl is None:
            new_ctrl = [control_qubit]
        elif isinstance(ctrl, list):
            new_ctrl = ctrl + [control_qubit]
        else:
            new_ctrl = [ctrl, control_qubit]
        new_op = (op_name, qubits, cbits, params, dagger, new_ctrl)
        dst.opcode_list.append(new_op)
        qubits_list = qubits if isinstance(qubits, list) else [qubits]
        dst.record_qubit(qubits_list + new_ctrl)


def _reflect_zero(circuit: Circuit, qubits: List[int]) -> None:
    """Apply reflection about |0⟩: 2|0⟩⟨0| - I.

    Decomposition: X on all qubits → multi-controlled Z → X on all qubits.
    """
    n = len(qubits)
    if n == 0:
        return

    for q in qubits:
        circuit.x(q)

    if n == 1:
        circuit.z(qubits[0])
    elif n == 2:
        circuit.cz(qubits[0], qubits[1])
    else:
        # Multi-controlled Z = H(target) + multi-controlled X + H(target)
        circuit.h(qubits[-1])
        _multi_controlled_x(circuit, qubits[:-1], qubits[-1])
        circuit.h(qubits[-1])

    for q in qubits:
        circuit.x(q)


def _multi_controlled_x(
    circuit: Circuit,
    controls: List[int],
    target: int,
) -> None:
    """Apply multi-controlled X gate.

    Uses toffoli decomposition with intermediate qubits from the same
    register as working ancillas. For n controls > 2, chains toffoli
    gates pairwise.
    """
    n_controls = len(controls)
    if n_controls == 0:
        circuit.x(target)
    elif n_controls == 1:
        circuit.cnot(controls[0], target)
    elif n_controls == 2:
        circuit.toffoli(controls[0], controls[1], target)
    else:
        # Use pairwise toffoli decomposition with available qubits as ancilla
        # Strategy: chain toffoli gates, using intermediate qubits
        # e.g. for 3 controls [c0,c1,c2] -> target:
        #   toffoli(c0, c1, c2)  [reuse c2 as ancilla]
        #   toffoli(c2, c3, target) if needed
        # Then uncompute.
        #
        # General: build a tree of toffoli gates
        _multi_controlled_x_chain(circuit, controls, target)


def _multi_controlled_x_chain(
    circuit: Circuit,
    controls: List[int],
    target: int,
) -> None:
    """Implement multi-controlled X using pairwise toffoli chain.

    Uses intermediate qubits as ancillas (taken from the control list).
    For k controls, uses k-2 ancilla qubits from the available qubit pool.
    The ancilla qubits are the control qubits themselves (they get
    temporarily modified and then restored).
    """
    n = len(controls)
    if n == 0:
        circuit.x(target)
        return
    if n == 1:
        circuit.cnot(controls[0], target)
        return
    if n == 2:
        circuit.toffoli(controls[0], controls[1], target)
        return

    # For n >= 3: use the last control as an ancilla target for the
    # intermediate toffoli, then chain.
    # Decompose: MCCX(c[0..n-2], c[n-1]) then CCX(c[n-1], last_control_unused, target)
    # Actually use a simpler recursive approach:
    # Step 1: toffoli(c[0], c[1], target) — but this modifies target
    # Better: use the linear-chain method
    #
    # We use the standard decomposition:
    # 1. toffoli(c[n-2], c[n-1], target)
    # 2. For i = n-3 down to 1: toffoli(c[i], c[i+1], c[i+1]) — store in next qubit
    # 3. toffoli(c[0], c[1], c[2])
    # Then reverse step 2 to uncompute.
    #
    # Simpler approach: just use add_gate with control_qubits directly
    # since the Circuit supports it natively
    circuit.add_gate(
        "X",
        target,
        control_qubits=controls,
    )


def grover_operator(
    circuit: Circuit,
    oracle: Circuit,
    qubits: List[int],
) -> None:
    r"""Apply one Grover iteration G = A · S₀ · A† · S_f.

    Where:
    - S_f is the oracle (phase flip on marked states)
    - A† is the inverse of the state preparation
    - S₀ is the reflection about |0⟩
    - A is the state preparation

    In the standard QAE formulation, A = H^{⊗n} (uniform superposition),
    and S_f is provided by the oracle circuit.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
        oracle: Oracle circuit implementing phase flip on target states.
            Must use the same qubit indices as *qubits*.
        qubits: Qubit indices for the search register.
    """
    n = len(qubits)
    if n < 1:
        raise ValueError("grover_operator requires at least 1 qubit")

    # S_f: Apply oracle gates into main circuit
    _copy_circuit_gates(oracle, circuit)

    # A†: Inverse of H^{⊗n} = H^{⊗n} (H is self-inverse)
    for q in qubits:
        circuit.h(q)

    # S₀: Reflect about |0⟩
    _reflect_zero(circuit, qubits)

    # A: H^{⊗n}
    for q in qubits:
        circuit.h(q)


def amplitude_estimation_circuit(
    circuit: Circuit,
    oracle: Circuit,
    qubits: Optional[List[int]] = None,
    n_eval_qubits: int = 3,
) -> None:
    r"""Apply Quantum Amplitude Estimation (QAE).

    Estimates the probability *a* that a measurement of the state prepared
    by A|0⟩ yields a "good" outcome (as defined by the oracle).

    Uses the canonical QPE-based construction:

    1. Prepare evaluation register in uniform superposition (H^{⊗m}).
    2. For each evaluation qubit *j*, apply 2^j controlled-Grover
       iterations on the search register.
    3. Apply inverse QFT on the evaluation register.
    4. Measure the evaluation register.

    The search register is initialized with H^{⊗n} (uniform superposition)
    before the controlled-Grover operations.

    Args:
        circuit: Quantum circuit to operate on (mutated in-place).
            Must have at least ``len(qubits) + n_eval_qubits`` qubits.
        oracle: Oracle circuit implementing the phase flip on marked states.
        qubits: Qubit indices for the search register. ``None`` means
            ``list(range(n_eval_qubits, n_eval_qubits + 2))``.
        n_eval_qubits: Number of evaluation (precision) qubits.

    Raises:
        ValueError: Invalid parameters.

    Example:
        >>> from qpandalite.circuit_builder import Circuit
        >>> from qpandalite.algorithmics.circuits import amplitude_estimation_circuit
        >>> oracle = Circuit()
        >>> oracle.z(0)
        >>> c = Circuit(5)
        >>> amplitude_estimation_circuit(c, oracle, qubits=[3, 4], n_eval_qubits=3)
    """
    total_qubits = circuit.max_qubit + 1

    if qubits is None:
        qubits = list(range(n_eval_qubits, total_qubits))

    n_search = len(qubits)
    if n_search < 1:
        raise ValueError("At least 1 search qubit is required")

    if n_eval_qubits < 1:
        raise ValueError("n_eval_qubits must be at least 1")

    if n_eval_qubits + n_search > total_qubits:
        raise ValueError(
            f"Not enough qubits: need {n_eval_qubits + n_search}, "
            f"have {total_qubits}"
        )

    eval_qubits = list(range(n_eval_qubits))

    # Step 1: Initialize evaluation register in superposition
    for q in eval_qubits:
        circuit.h(q)

    # Step 2: Initialize search register in uniform superposition
    for q in qubits:
        circuit.h(q)

    # Step 3: Apply controlled-Grover iterations
    for j in eval_qubits:
        n_iters = 2 ** j
        for _ in range(n_iters):
            _controlled_grover(circuit, oracle, qubits, j)

    # Step 4: Inverse QFT on evaluation register
    _inverse_qft(circuit, eval_qubits)

    # Step 5: Measure evaluation register
    for q in eval_qubits:
        circuit.measure(q)


def _controlled_grover(
    circuit: Circuit,
    oracle: Circuit,
    qubits: List[int],
    control_qubit: int,
) -> None:
    """Apply a controlled Grover iteration.

    Each gate is conditioned on control_qubit.
    """
    # S_f (oracle) — controlled
    _copy_circuit_gates_controlled(oracle, circuit, control_qubit)

    # A† = H^{⊗n} — controlled H on each search qubit
    for q in qubits:
        circuit.add_gate("H", q, control_qubits=[control_qubit])

    # S₀: controlled reflection about |0⟩
    # Controlled-X on all qubits
    for q in qubits:
        circuit.cnot(control_qubit, q)

    # Controlled multi-controlled Z
    n = len(qubits)
    if n == 1:
        # Controlled-Z: use H-CX-H decomposition
        circuit.h(qubits[0])
        circuit.cnot(control_qubit, qubits[0])
        circuit.h(qubits[0])
    elif n == 2:
        # Controlled CCZ = controlled-Toffoli + Z
        circuit.h(qubits[-1])
        circuit.toffoli(control_qubit, qubits[0], qubits[-1])
        circuit.h(qubits[-1])
    else:
        # For larger n, use native multi-controlled gate support
        circuit.h(qubits[-1])
        all_controls = [control_qubit] + qubits[:-1]
        circuit.add_gate("X", qubits[-1], control_qubits=all_controls)
        circuit.h(qubits[-1])

    # Controlled-X on all qubits (undo)
    for q in qubits:
        circuit.cnot(control_qubit, q)

    # A = H^{⊗n} — controlled
    for q in qubits:
        circuit.add_gate("H", q, control_qubits=[control_qubit])


def _inverse_qft(circuit: Circuit, qubits: List[int]) -> None:
    """Apply inverse QFT on the given qubits (without swaps)."""
    n = len(qubits)
    for j in range(n - 1, -1, -1):
        for k in range(n - 1, j, -1):
            angle = -math.pi / (2 ** (k - j))
            # Controlled phase via CNOT-Rz-CNOT decomposition
            circuit.rz(angle / 2, qubits[k])
            circuit.cnot(qubits[j], qubits[k])
            circuit.rz(-angle / 2, qubits[k])
            circuit.cnot(qubits[j], qubits[k])
        circuit.h(qubits[j])


def amplitude_estimation_result(
    counts: dict,
    n_eval_qubits: int,
) -> float:
    """Estimate probability *a* from QAE measurement results.

    Converts the most-frequent measurement outcome to an angle θ and
    computes a = sin²(θ).

    Args:
        counts: Dictionary mapping measurement outcomes (bit-strings or
            integers) to frequencies/counts.
        n_eval_qubits: Number of evaluation qubits used in QAE.

    Returns:
        Estimated probability *a* ∈ [0, 1].
    """
    if not counts:
        return 0.0

    best = max(counts, key=counts.get)

    if isinstance(best, str):
        m = int(best, 2)
    else:
        m = int(best)

    M = n_eval_qubits
    theta = math.pi * m / (2 ** M)
    a = math.sin(theta) ** 2

    return a
