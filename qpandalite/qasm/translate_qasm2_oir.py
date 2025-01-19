

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
    if operation == 'id':
        return ('I', qubits, cbits, parameters, None, None)
    elif operation == 'h':
        return ('H', qubits,)
    elif operation == 'rx':
        return ('RX', qubits, cbits, parameters, None, None)