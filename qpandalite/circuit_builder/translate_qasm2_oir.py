"""Translation utilities between OpenQASM 2.0 and OriginIR.

This module provides bidirectional translation between OpenQASM 2.0 and OriginIR
quantum circuit representations. It includes direct mapping dictionaries,
opcode conversion functions, and multi-controlled gate decomposition.

Key exports:
    OriginIR_QASM2_dict: Mapping from OriginIR to QASM2 operations.
    QASM2_OriginIR_dict: Mapping from QASM2 to OriginIR operations.
    direct_mapping_qasm2_to_oir: Function for direct QASM2 to OriginIR lookup.
    get_opcode_from_QASM2: Convert QASM2 operation to OriginIR opcode.
    get_QASM2_from_opcode: Convert OriginIR opcode to QASM2 operation.
    decompose_mcx_qasm_text: Decompose multi-controlled X gates for QASM2.
    decompose_mcu_qasm_text: Decompose multi-controlled single-qubit gates for QASM2.
"""

import math
from typing import List, Optional, Tuple, Union
from .qasm_spec import available_qasm_gates

__all__ = [
    "OriginIR_QASM2_dict",
    "QASM2_OriginIR_dict",
    "direct_mapping_qasm2_to_oir",
    "get_opcode_from_QASM2",
    "get_QASM2_from_opcode",
    "decompose_mcx_qasm_text",
    "decompose_mcu_qasm_text",
]

qasm2_oir_mapping = {
    ("id", "I"),
    ("h", "H"),
    ("x", "X"),
    ("y", "Y"),
    ("z", "Z"),
    ("s", "S"),
    ("sx", "SX"),
    ("t", "T"),
    ("cx", "CNOT"),
    ("cz", "CZ"),
    ("swap", "SWAP"),
    ("ccx", "TOFFOLI"),
    ("cswap", "CSWAP"),
    ("rx", "RX"),
    ("ry", "RY"),
    ("rz", "RZ"),
    ("u1", "U1"),
    ("u2", "U2"),
    ("u3", "U3"),
    ("rxx", "XX"),
    ("ryy", "YY"),
    ("rzz", "ZZ"),
}

# direct mapping from OriginIR opcode to QASM2 operation
QASM2_OriginIR_dict = {qasm: oir for (qasm, oir) in qasm2_oir_mapping}

# direct mapping from QASM2 operation to OriginIR
OriginIR_QASM2_dict = {oir: qasm for (qasm, oir) in qasm2_oir_mapping}


def direct_mapping_qasm2_to_oir(qasm2_operation):
    """
    Return the corresponding OriginIR by given QASM2 operation.
    Return None when there is no direct-mapping.

    Note: There are also operations that do not sastify "direct mapping"
    from QASM -> OIR or OIR -> QASM.
    """
    return QASM2_OriginIR_dict.get(qasm2_operation, None)


def get_opcode_from_QASM2(operation, qubits, cbits, parameters):
    """Here list all supported operations of OpenQASM2.0 and its corresponding operation
    in OriginIR in QPanda-lite.

    Opcode Definition:
    opcodes = (operation,qubits,cbit,parameter,dagger_flag,control_qubits_set)
    """

    # 1-qubit gates
    if operation == "id":
        return ("I", qubits, cbits, parameters, False, None)
    elif operation == "h":
        return ("H", qubits, cbits, parameters, False, None)
    elif operation == "x":
        return ("X", qubits, cbits, parameters, False, None)
    elif operation == "y":
        return ("Y", qubits, cbits, parameters, False, None)
    elif operation == "z":
        return ("Z", qubits, cbits, parameters, False, None)
    elif operation == "s":
        return ("S", qubits, cbits, parameters, False, None)
    elif operation == "sdg":
        return ("S", qubits, cbits, parameters, True, None)
    elif operation == "sx":
        return ("SX", qubits, cbits, parameters, False, None)
    elif operation == "sxdg":
        return ("SX", qubits, cbits, parameters, True, None)
    elif operation == "t":
        return ("T", qubits, cbits, parameters, False, None)
    elif operation == "tdg":
        return ("T", qubits, cbits, parameters, True, None)
    # 2-qubit gates
    elif operation == "cx":
        return ("CNOT", qubits, cbits, parameters, False, None)
    elif operation == "cy":
        return ("Y", qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == "cz":
        return ("CZ", qubits, cbits, parameters, False, None)
    elif operation == "swap":
        return ("SWAP", qubits, cbits, parameters, False, None)
    elif operation == "ch":
        return ("H", qubits, cbits, parameters, False, [qubits[0]])
    # 3-qubit gates
    elif operation == "ccx":
        return ("TOFFOLI", qubits, cbits, parameters, False, None)
    elif operation == "cswap":
        return ("CSWAP", qubits, cbits, parameters, False, None)
    # 4-qubit gates
    elif operation == "c3x":
        return ("X", qubits[3], cbits, parameters, False, qubits[0:3])
    # 1-qubit 1-parameter gates
    elif operation == "rx":
        return ("RX", qubits, cbits, parameters, False, None)
    elif operation == "ry":
        return ("RY", qubits, cbits, parameters, False, None)
    elif operation == "rz":
        return ("RZ", qubits, cbits, parameters, False, None)
    elif operation == "u1":
        return ("U1", qubits, cbits, parameters, False, None)
    # 1-qubit 2-parameter gates
    elif operation == "u2":
        return ("U2", qubits, cbits, parameters, False, None)
    elif operation == "u0":
        return ("U0", qubits, cbits, parameters, False, None)
    # 1-qubit 3-parameter gates
    elif operation == "u" or operation == "u3":
        return ("U3", qubits, cbits, parameters, False, None)
    # 2-qubit 1-parameter gates
    elif operation == "rxx":
        return ("XX", qubits, cbits, parameters, False, None)
    elif operation == "ryy":
        return ("YY", qubits, cbits, parameters, False, None)
    elif operation == "rzz":
        return ("ZZ", qubits, cbits, parameters, False, None)
    elif operation == "cu1":
        return ("U1", qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == "crx":
        return ("RX", qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == "cry":
        return ("RY", qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == "crz":
        return ("RZ", qubits[1], cbits, parameters, False, [qubits[0]])
    # 2-qubit 3-parameter gates
    elif operation == "cu3":
        return ("U3", qubits[1], cbits, parameters, False, [qubits[0]])

    return None


def decompose_mcx_qasm_text(controls: List[int], target: int, qubit_num: int) -> str:
    """Decompose an n-control X (MCX) gate into QASM 2.0 Toffoli-ladder statements.

    Uses a clean-ancilla ladder (Barenco et al. 1995, adapted): n-2 workspace
    qubits are borrowed from existing circuit qubits not involved in the gate.
    The workspace qubits must be in state |0⟩ at the call site; they are
    restored to |0⟩ after the decomposition.

    Args:
        controls: Ordered list of n ≥ 4 control qubit indices.
        target: Target qubit index.
        qubit_num: Total number of qubits declared in the circuit (``qreg q[N]``).

    Returns:
        Multi-line QASM 2.0 string (Toffoli gates only; no semicolon-separated
        single line — the returned string may contain ``\\n``).

    Raises:
        NotImplementedError: Not enough workspace qubits are available in the
            circuit.  Use OriginIR export (which supports arbitrary-width
            controlled gates natively) or add workspace qubits to the circuit.
    """
    n = len(controls)
    assert n >= 4, f"decompose_mcx_qasm_text requires n>=4, got {n}"
    n_workspace = n - 2

    used = set(controls) | {target}
    workspace = [q for q in range(qubit_num) if q not in used][:n_workspace]

    if len(workspace) < n_workspace:
        raise NotImplementedError(
            f"MCX with {n} controls needs {n_workspace} workspace qubits, "
            f"but only {len(workspace)} are available in a {qubit_num}-qubit circuit. "
            "Add workspace qubits to the circuit, or use OriginIR export which "
            "supports arbitrary-width multi-controlled gates natively."
        )

    lines: List[str] = []
    # Forward ladder: compute AND(c0, c1, …, c_{n-2}) into workspace[-1].
    lines.append(f"ccx q[{controls[0]}], q[{controls[1]}], q[{workspace[0]}];")
    for i in range(1, n_workspace):
        lines.append(f"ccx q[{controls[i + 1]}], q[{workspace[i - 1]}], q[{workspace[i]}];")
    # Apply to target using the last control and the accumulated AND.
    lines.append(f"ccx q[{controls[-1]}], q[{workspace[-1]}], q[{target}];")
    # Uncompute workspace (reverse order).
    for i in range(n_workspace - 1, 0, -1):
        lines.append(f"ccx q[{controls[i + 1]}], q[{workspace[i - 1]}], q[{workspace[i]}];")
    lines.append(f"ccx q[{controls[0]}], q[{controls[1]}], q[{workspace[0]}];")

    return "\n".join(lines)


def get_QASM2_from_opcode(
    opcode,
) -> Tuple[str, Union[int, List[int]], Union[int, List[int]], Union[float, List[float]]]:
    """
    Return the corresponding QASM2 operation by given OriginIR operation.

    Note: Only a subset of QASM2 operations are supported in QPanda-lite.
    """

    (operation, qubits, cbits, parameters, dagger_flag, control_qubits_set) = opcode

    # check if the operation is supported
    if operation not in OriginIR_QASM2_dict:
        raise NotImplementedError(f"The operation {operation} is not supported in QPanda-lite.")

    operation_qasm2 = OriginIR_QASM2_dict[operation]

    # Dagger flag is supported only when operation is S or T or SX
    # These gates will skip the dagger flag:
    # I(id), H(h), X(x), Y(y), Z(z), CNOT(cx), CZ(cz), SWAP(swap), TOFFOLI(ccx)
    # These gates will invert the angle parameter:
    # RX(rx), RY(ry), RZ(rz), U1(u1), XX(xx), YY(yy), ZZ(zz),

    if dagger_flag:
        if operation_qasm2 in ["s", "t", "sx"]:
            operation_qasm2 += "dg"
        elif operation_qasm2 in ["id", "h", "x", "y", "z", "cx", "cz", "swap", "ccx"]:
            pass
        elif operation_qasm2 in ["rx", "ry", "rz", "u1", "rxx", "ryy", "rzz"]:
            parameters = -parameters
        elif operation_qasm2 == "u3":
            # U3(θ,φ,λ)† = U3(-θ,-λ,-φ)
            if isinstance(parameters, list):
                theta, phi, lam = parameters[0], parameters[1], parameters[2]
            else:
                theta, phi, lam = parameters
            parameters = [-theta, -lam, -phi]
        else:
            raise NotImplementedError(f"The operation {operation} with dagger flag is not supported in QPanda-lite.")

    # When there is no control qubits, return
    if not control_qubits_set:
        return operation_qasm2, qubits, cbits, parameters

    # Work with a copy so we never mutate the original opcode's control list.
    ctrl_list = list(control_qubits_set)

    # When there are 1 control qubit, add the control keyword
    if len(ctrl_list) == 1:
        operation_qasm2 = "c" + operation_qasm2
        # check whether this operation is still supported
        if operation_qasm2 not in available_qasm_gates:
            raise NotImplementedError(
                f"The operation {operation_qasm2} with control qubit is not supported in QPanda-lite."
            )
        qubits_out = ctrl_list + (list(qubits) if isinstance(qubits, list) else [qubits])
        return operation_qasm2, qubits_out, cbits, parameters

    # When there are 2 control qubits, add the control keyword
    if len(ctrl_list) == 2:
        operation_qasm2 = "cc" + operation_qasm2
        # check whether this operation is still supported
        if operation_qasm2 not in available_qasm_gates:
            raise NotImplementedError(
                f"The operation {operation_qasm2} with control qubit is not supported in QPanda-lite."
            )
        qubits_out = ctrl_list + (list(qubits) if isinstance(qubits, list) else [qubits])
        return operation_qasm2, qubits_out, cbits, parameters

    # When there are 3 control qubits, add the control keyword
    if len(ctrl_list) == 3:
        operation_qasm2 = "c3" + operation_qasm2
        # check whether this operation is still supported
        if operation_qasm2 not in available_qasm_gates:
            raise NotImplementedError(
                f"The operation {operation_qasm2} with control qubit is not supported in QPanda-lite."
            )
        qubits_out = ctrl_list + (list(qubits) if isinstance(qubits, list) else [qubits])
        return operation_qasm2, qubits_out, cbits, parameters

    # n >= 4 controls: signal to opcode_to_line_qasm that decomposition is needed.
    # Supported single-qubit gates are decomposed via conjugation or ABC method.
    _mcu_supported_gates = {
        "x",
        "z",
        "y",
        "s",
        "sdg",
        "rz",
        "rx",
        "u1",
        "u3",
        "ry",
        "sx",
        "sxdg",
        "h",
    }
    if operation_qasm2 not in _mcu_supported_gates:
        raise NotImplementedError(
            f"QASM 2.0 export does not support the gate '{operation}' with "
            f"{len(ctrl_list)} control qubits. Use OriginIR export instead."
        )
    # Return a sentinel that opcode_to_line_qasm will intercept.
    # dagger_flag has already been applied to operation_qasm2/parameters above,
    # so we pass False here to avoid double-applying.
    target_qubit = qubits if not isinstance(qubits, list) else qubits[0]
    return "_MCU_DECOMP_", (ctrl_list, target_qubit, operation_qasm2, parameters, False), None, None


def _qasm_gate(name: str, qubit: int, param: Optional[float] = None) -> str:
    """Format a single QASM 2.0 gate line."""
    if param is not None:
        return f"{name}({param}) q[{qubit}];"
    return f"{name} q[{qubit}];"


def _scalar(params: Union[float, List[float]]) -> float:
    """Extract a scalar from a parameter that may be a float or a single-element list."""
    if isinstance(params, list):
        return float(params[0])
    return float(params)


def _abc_decompose(
    phi: float,
    theta: float,
    lam: float,
    controls: List[int],
    target: int,
    qubit_num: int,
) -> str:
    """Decompose a multi-controlled gate via the ABC method (Barenco et al.).

    Given a gate with SU(2) ZYZ decomposition V = RZ(phi)·RY(theta)·RZ(lam),
    compute A, B, C such that CBA = I and AXBXC = V, then emit:
        A → MCX → B → MCX → C  (on the target qubit).
    """
    mcx_lines = decompose_mcx_qasm_text(controls, target, qubit_num)

    # A = RZ(phi - lam)
    # B = RZ(pi - lam) · RY(theta/2) · RZ((lam - phi)/2 - pi)
    # C = RZ((lam - phi)/2) · RY(theta/2) · RZ(lam)

    a_phi_lam = phi - lam
    b_rz1 = math.pi - lam
    b_ry = theta / 2
    b_rz2 = (lam - phi) / 2 - math.pi
    c_rz1 = (lam - phi) / 2
    c_ry = theta / 2
    c_rz2 = lam

    lines: List[str] = []

    # A
    if abs(a_phi_lam) > 1e-15:
        lines.append(_qasm_gate("rz", target, a_phi_lam))

    # MCX
    lines.append(mcx_lines)

    # B
    if abs(b_rz1) > 1e-15:
        lines.append(_qasm_gate("rz", target, b_rz1))
    if abs(b_ry) > 1e-15:
        lines.append(_qasm_gate("ry", target, b_ry))
    if abs(b_rz2) > 1e-15:
        lines.append(_qasm_gate("rz", target, b_rz2))

    # MCX
    lines.append(mcx_lines)

    # C
    if abs(c_rz1) > 1e-15:
        lines.append(_qasm_gate("rz", target, c_rz1))
    if abs(c_ry) > 1e-15:
        lines.append(_qasm_gate("ry", target, c_ry))
    if abs(c_rz2) > 1e-15:
        lines.append(_qasm_gate("rz", target, c_rz2))

    return "\n".join(lines)


def decompose_mcu_qasm_text(
    controls: List[int],
    target: int,
    qubit_num: int,
    gate_qasm: str,
    params: Optional[Union[float, List[float]]],
) -> str:
    """Decompose an n-control single-qubit gate into QASM 2.0 statements.

    Uses two strategies:
    - **Tier 1 (conjugation, 1 MCX)**: For gates where G = U·X·U†.
      Supported: X, Z, Y, S, Sdg, RZ, RX, U1.
    - **Tier 2 (ABC method, 2 MCX)**: For gates requiring the general
      Barenco decomposition A·MCX·B·MCX·C.
      Supported: U3, RY, SX, H.

    Args:
        controls: Ordered list of n ≥ 4 control qubit indices.
        target: Target qubit index.
        qubit_num: Total number of qubits declared in the circuit.
        gate_qasm: QASM 2.0 gate name (already dagger-adjusted).
        params: Gate parameter(s), already dagger-adjusted if applicable.

    Returns:
        Multi-line QASM 2.0 string.

    Raises:
        NotImplementedError: Gate is not supported for decomposition.
    """
    n = len(controls)
    assert n >= 4, f"decompose_mcu_qasm_text requires n>=4, got {n}"

    mcx_lines = decompose_mcx_qasm_text(controls, target, qubit_num)

    # --- Tier 1: simple conjugation G = U · X · U† (1 MCX) ---

    if gate_qasm == "x":
        return mcx_lines

    if gate_qasm == "z":
        return f"h q[{target}];\n{mcx_lines}\nh q[{target}];"

    if gate_qasm == "y":
        return f"sdg q[{target}];\nh q[{target}];\n{mcx_lines}\nh q[{target}];\ns q[{target}];"

    if gate_qasm == "s":
        return f"h q[{target}];\nt q[{target}];\n{mcx_lines}\ntdg q[{target}];\nh q[{target}];"

    if gate_qasm == "sdg":
        return f"h q[{target}];\ntdg q[{target}];\n{mcx_lines}\nt q[{target}];\nh q[{target}];"

    if gate_qasm == "rz":
        half = _scalar(params) / 2
        return f"rz({half}) q[{target}];\nh q[{target}];\n{mcx_lines}\nh q[{target}];\nrz({half}) q[{target}];"

    if gate_qasm == "rx":
        half = _scalar(params) / 2
        return (
            f"h q[{target}];\nrz({half}) q[{target}];\nh q[{target}];\n"
            f"{mcx_lines}\n"
            f"h q[{target}];\nrz({half}) q[{target}];\nh q[{target}];"
        )

    if gate_qasm == "u1":
        half = _scalar(params) / 2
        return f"rz({half}) q[{target}];\nh q[{target}];\n{mcx_lines}\nh q[{target}];\nrz({half}) q[{target}];"

    # --- Tier 2: ABC decomposition (2 MCX) ---

    if gate_qasm == "u3":
        p = params if isinstance(params, list) else [params]
        theta, phi, lam = p[0], p[1], p[2]
        # U3(theta, phi, lam) — ZYZ decomposition: phi, theta, lam
        return _abc_decompose(phi, theta, lam, controls, target, qubit_num)

    if gate_qasm == "ry":
        theta = _scalar(params)
        # RY(theta) — ZYZ: phi=0, theta=theta, lam=0
        return _abc_decompose(0.0, theta, 0.0, controls, target, qubit_num)

    if gate_qasm == "sx":
        # SX — SU(2) part ZYZ: phi=-pi/2, theta=pi/2, lam=pi/2
        return _abc_decompose(
            -math.pi / 2,
            math.pi / 2,
            math.pi / 2,
            controls,
            target,
            qubit_num,
        )

    if gate_qasm == "sxdg":
        # SXdg — SU(2) part ZYZ: phi=-pi/2, theta=-pi/2, lam=pi/2
        return _abc_decompose(
            -math.pi / 2,
            -math.pi / 2,
            math.pi / 2,
            controls,
            target,
            qubit_num,
        )

    if gate_qasm == "h":
        # H — SU(2) part ZYZ: phi=0, theta=pi, lam=0
        return _abc_decompose(0.0, math.pi, 0.0, controls, target, qubit_num)

    raise NotImplementedError(
        f"QASM 2.0 export does not support decomposing '{gate_qasm}' with "
        f"{n} control qubits. Use OriginIR export instead."
    )
