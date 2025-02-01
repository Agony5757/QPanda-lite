# Translation between QASM2 and OriginIR.

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
    ('rzz', 'ZZ'),
}

QASM2_OriginIR_dict = {
    qasm : oir for (qasm, oir) in qasm2_oir_mapping
}

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