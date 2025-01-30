# This file specifies the OriginIR language specification,
# including the grammar and the syntax of the language.

available_originir_1q_gates = ['H', 'X', 'Y', 'Z', 'S', 'SX', 'T']
available_originir_1q1p_gates = ['RX', 'RY', 'RZ', 'U1', 'RPHI90', 'RPHI180', ]
available_originir_2q_gates = ['CNOT', 'CZ', 'ISWAP', ] #TODO: SQISWAP
available_originir_2q1p_gates = ['XX', 'YY', 'ZZ', 'XY', ]
available_originir_2q3p_gates = ['PHASE2Q']
available_originir_2q15p_gates = ['UU15']
available_originir_3p_gates = ['TOFFOLI', 'CSWAP']

available_originir_gates = {
    gatename : {'qubit': 1, 'param': 0}
    for gatename in available_originir_1q_gates
}

available_originir_gates.update({
    gatename : {'qubit': 1, 'param': 1}
    for gatename in available_originir_1q1p_gates
})

available_originir_gates.update({
    gatename : {'qubit': 2, 'param': 0}
    for gatename in available_originir_2q_gates
})

available_originir_gates.update({
    gatename : {'qubit': 2, 'param': 1}
    for gatename in available_originir_2q1p_gates
})

available_originir_gates.update({
    gatename : {'qubit': 2, 'param': 3}
    for gatename in available_originir_2q3p_gates
})

available_originir_gates.update({
    gatename : {'qubit': 2, 'param': 15}
    for gatename in available_originir_2q15p_gates
})

available_originir_gates.update({
    gatename : {'qubit': 3, 'param': 0}
    for gatename in available_originir_3p_gates
})

def generate_sub_gateset_originir(gate_list):
    return {k : v for k, v in available_originir_gates.items() if k in gate_list}