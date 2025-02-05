# This file specifies the QASM language specification, 
# including the grammar and the syntax of the language.

available_qasm_1q_gates = ['id', 'h', 'x', 'y', 'z', 's', 'sdg', 'sx', 'sxdg', 't', 'tdg']
available_qasm_1q1p_gates = ['rx', 'ry', 'rz', 'u1']
available_qasm_1q2p_gates = ['u2']
available_qasm_1q3p_gates = ['u3', 'u']
available_qasm_2q_gates = ['cx', 'cy', 'cz', 'swap']
available_qasm_3q_gates = ['ccx', 'cswap']
available_qasm_4q_gates = ['c3x']
available_qasm_2q1p_gates = ['crx', 'cry', 'crz', 'cu1', 'rxx', 'rzz']

available_qasm_gates = {
    gatename : {'qubit': 1, 'params': 0}
    for gatename in available_qasm_1q_gates
}

available_qasm_gates.update({
    gatename : {'qubit': 1, 'params': 1}
    for gatename in available_qasm_1q1p_gates
})

available_qasm_gates.update({
    gatename : {'qubit': 1, 'params': 2}
    for gatename in available_qasm_1q2p_gates
})

available_qasm_gates.update({
    gatename : {'qubit': 1, 'params': 3}
    for gatename in available_qasm_1q3p_gates
})

available_qasm_gates.update({
    gatename : {'qubit': 2, 'params': 0}
    for gatename in available_qasm_2q_gates
})

available_qasm_gates.update({
    gatename : {'qubit': 3, 'params': 0}
    for gatename in available_qasm_3q_gates
})

available_qasm_gates.update({
    gatename : {'qubit': 4, 'params': 0}
    for gatename in available_qasm_4q_gates
})

available_qasm_gates.update({
    gatename : {'qubit': 2, 'params': 1}
    for gatename in available_qasm_2q1p_gates
})

def generate_sub_gateset_qasm(gate_list):
    return {k : v for k, v in available_qasm_gates.items() if k in gate_list}
    