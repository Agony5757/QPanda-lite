# Translation between QASM2 and OriginIR.

from typing import List, Tuple, Union
from .qasm_spec import available_qasm_gates

__all__ = [
    'OriginIR_QASM2_dict',
    'QASM2_OriginIR_dict',
    'direct_mapping_qasm2_to_oir',
    'get_opcode_from_QASM2',
    'get_QASM2_from_opcode',
    'decompose_mcx_qasm_text',
]

qasm2_oir_mapping = {
    ('id', 'I'),
    ('h', 'H'),
    ('x', 'X'),
    ('y', 'Y'),
    ('z', 'Z'),
    ('s', 'S'),
    ('sx', 'SX'),
    ('t', 'T'),
    ('cx', 'CNOT'),
    ('cz', 'CZ'),
    ('swap', 'SWAP'),
    ('ccx', 'TOFFOLI'),
    ('cswap', 'CSWAP'),
    ('rx', 'RX'),
    ('ry', 'RY'),
    ('rz', 'RZ'),
    ('u1', 'U1'),
    ('u2', 'U2'),
    ('u3', 'U3'),
    ('rxx', 'XX'),
    ('ryy', 'YY'),
    ('rzz', 'ZZ'),
}

# direct mapping from OriginIR opcode to QASM2 operation
QASM2_OriginIR_dict = {
    qasm : oir for (qasm, oir) in qasm2_oir_mapping
} 

# direct mapping from QASM2 operation to OriginIR
OriginIR_QASM2_dict = {
    oir : qasm for (qasm, oir) in qasm2_oir_mapping
}

def direct_mapping_qasm2_to_oir(qasm2_operation):
    '''
    Return the corresponding OriginIR by given QASM2 operation.
    Return None when there is no direct-mapping. 

    Note: There are also operations that do not sastify "direct mapping"
    from QASM -> OIR or OIR -> QASM.
    '''
    return QASM2_OriginIR_dict.get(qasm2_operation, None)


def get_opcode_from_QASM2(operation, qubits, cbits, parameters):
    '''Here list all supported operations of OpenQASM2.0 and its corresponding operation 
       in OriginIR in QPanda-lite.

       Opcode Definition:
       opcodes = (operation,qubits,cbit,parameter,dagger_flag,control_qubits_set)    
    '''

    # 1-qubit gates
    if operation == 'id':
        return ('I', qubits, cbits, parameters, False, None)
    elif operation == 'h':
        return ('H', qubits, cbits, parameters, False, None)
    elif operation == 'x':
        return ('X', qubits, cbits, parameters, False, None)
    elif operation == 'y':
        return ('Y', qubits, cbits, parameters, False, None)
    elif operation == 'z':
        return ('Z', qubits, cbits, parameters, False, None)
    elif operation == 's':
        return ('S', qubits, cbits, parameters, False, None)
    elif operation == 'sdg':
        return ('S', qubits, cbits, parameters, True, None)
    elif operation == 'sx':
        return ('SX', qubits, cbits, parameters, False, None)
    elif operation == 'sxdg':
        return ('SX', qubits, cbits, parameters, True, None)
    elif operation == 't':
        return ('T', qubits, cbits, parameters, False, None)
    elif operation == 'tdg':
        return ('T', qubits, cbits, parameters, True, None)
    # 2-qubit gates
    elif operation == 'cx':
        return ('CNOT', qubits, cbits, parameters, False, None)
    elif operation == 'cy':
        return ('Y', qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == 'cz':
        return ('CZ', qubits, cbits, parameters, False, None)
    elif operation == 'swap':
        return ('SWAP', qubits, cbits, parameters, False, None)
    elif operation == 'ch':
        return ('H', qubits, cbits, parameters, False, [qubits[0]])
    # 3-qubit gates
    elif operation == 'ccx':
        return ('TOFFOLI', qubits, cbits, parameters, False, None)
    elif operation == 'cswap':
        return ('CSWAP', qubits, cbits, parameters, False, None)
    # 4-qubit gates
    elif operation == 'c3x':
        return ('X', qubits[3], cbits, parameters, False, qubits[0:3])
    # 1-qubit 1-parameter gates
    elif operation == 'rx':
        return ('RX', qubits, cbits, parameters, False, None)
    elif operation == 'ry':
        return ('RY', qubits, cbits, parameters, False, None)
    elif operation == 'rz':
        return ('RZ', qubits, cbits, parameters, False, None)
    elif operation == 'u1':
        return ('U1', qubits, cbits, parameters, False, None)      
    # 1-qubit 2-parameter gates
    elif operation == 'u2':
        return ('U2', qubits, cbits, parameters, False, None) 
    elif operation == 'u0':
        return ('U0', qubits, cbits, parameters, False, None)
    # 1-qubit 3-parameter gates
    elif operation == 'u' or operation == 'u3':
        return ('U3', qubits, cbits, parameters, False, None)
    # 2-qubit 1-parameter gates
    elif operation == 'rxx':
        return ('XX', qubits, cbits, parameters, False, None)
    elif operation == 'ryy':
        return ('YY', qubits, cbits, parameters, False, None)
    elif operation == 'rzz':
        return ('ZZ', qubits, cbits, parameters, False, None)
    elif operation == 'cu1':
        return ('U1', qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == 'crx':
        return ('RX', qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == 'cry':
        return ('RY', qubits[1], cbits, parameters, False, [qubits[0]])
    elif operation == 'crz':
        return ('RZ', qubits[1], cbits, parameters, False, [qubits[0]])
    # 2-qubit 3-parameter gates
    elif operation == 'cu3':
        return ('U3', qubits[1], cbits, parameters, False, [qubits[0]])
    
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


def get_QASM2_from_opcode(opcode) -> Tuple[str, Union[int, List[int]], Union[int, List[int]], Union[float, List[float]]]:
    '''
    Return the corresponding QASM2 operation by given OriginIR operation.

    Note: Only a subset of QASM2 operations are supported in QPanda-lite.
    '''

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
        if operation_qasm2 in ['s', 't', 'sx']:
            operation_qasm2 += 'dg'
        elif operation_qasm2 in ['id', 'h', 'x', 'y', 'z', 'cx', 'cz', 'swap', 'ccx']:
            pass
        elif operation_qasm2 in ['rx', 'ry', 'rz', 'u1', 'rxx', 'ryy', 'rzz']:
            parameters = -parameters
        else:
            raise NotImplementedError(f"The operation {operation} with dagger flag is not supported in QPanda-lite.")

    # When there is no control qubits, return
    if not control_qubits_set:
        return operation_qasm2, qubits, cbits, parameters

    # Work with a copy so we never mutate the original opcode's control list.
    ctrl_list = list(control_qubits_set)

    # When there are 1 control qubit, add the control keyword
    if len(ctrl_list) == 1:
        operation_qasm2 = 'c' + operation_qasm2
        # check whether this operation is still supported
        if operation_qasm2 not in available_qasm_gates:
            raise NotImplementedError(f"The operation {operation_qasm2} with control qubit is not supported in QPanda-lite.")
        qubits_out = ctrl_list + (list(qubits) if isinstance(qubits, list) else [qubits])
        return operation_qasm2, qubits_out, cbits, parameters

    # When there are 2 control qubits, add the control keyword
    if len(ctrl_list) == 2:
        operation_qasm2 = 'cc' + operation_qasm2
        # check whether this operation is still supported
        if operation_qasm2 not in available_qasm_gates:
            raise NotImplementedError(f"The operation {operation_qasm2} with control qubit is not supported in QPanda-lite.")
        qubits_out = ctrl_list + (list(qubits) if isinstance(qubits, list) else [qubits])
        return operation_qasm2, qubits_out, cbits, parameters

    # When there are 3 control qubits, add the control keyword
    if len(ctrl_list) == 3:
        operation_qasm2 = 'c3' + operation_qasm2
        # check whether this operation is still supported
        if operation_qasm2 not in available_qasm_gates:
            raise NotImplementedError(f"The operation {operation_qasm2} with control qubit is not supported in QPanda-lite.")
        qubits_out = ctrl_list + (list(qubits) if isinstance(qubits, list) else [qubits])
        return operation_qasm2, qubits_out, cbits, parameters

    # n >= 4 controls: signal to opcode_to_line_qasm that decomposition is needed.
    # Only X is handled; other gates raise NotImplementedError (see 已知问题.md).
    if operation_qasm2 != 'x':
        raise NotImplementedError(
            f"QASM 2.0 export does not support the gate '{operation}' with "
            f"{len(ctrl_list)} control qubits. Use OriginIR export instead."
        )
    # Return a sentinel that opcode_to_line_qasm will intercept.
    target_qubit = qubits if not isinstance(qubits, list) else qubits[0]
    return '_MCX_DECOMP_', (ctrl_list, target_qubit), None, None

