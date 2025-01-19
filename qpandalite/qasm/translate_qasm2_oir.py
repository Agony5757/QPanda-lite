

qasm2_oir_mapping = {
    ('id', 'I'),
    ('h', 'H'),
    ('x', 'X'),
    ('y', 'Y'),
    ('z', 'Z'),

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
        return ('CY', qubits, cbits, parameters, False, None)
    elif operation == 'cz':
        return ('CZ', qubits, cbits, parameters, False, None)
    elif operation == 'swap':
        return ('SWAP', qubits, cbits, parameters, False, None)
    elif operation == 'ch':
        return ('CH', qubits, cbits, parameters, False, None)
    # 3-qubit gates
    elif operation == 'ccx':
        return ('TOFFOLI', qubits, cbits, parameters, False, None)
    elif operation == 'cswap':
        return ('CSWAP', qubits, cbits, parameters, False, None)
    # 4-qubit gates
    elif operation == 'cccx':
        return ('X', qubits[0], cbits, parameters, False, qubits[1:4])
    elif operation == 'rx':
        return ('RX', qubits, cbits, parameters, False, None)