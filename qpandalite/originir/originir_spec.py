# This file specifies the OriginIR language specification,
# including the grammar and the syntax of the language.

available_originir_1q_gates = ['H', 'X', 'Y', 'Z', 'S', 'SX', 'T']
available_originir_1q1p_gates = ['RX', 'RY', 'RZ', 'U1', 'RPhi90', 'RPhi180', ]
available_originir_1q2p_gates = ['RPhi', 'U2']
available_originir_1q3p_gates = ['U3']
available_originir_2q_gates = ['CNOT', 'CZ', 'ISWAP', ] #TODO: SQISWAP
available_originir_2q1p_gates = ['XX', 'YY', 'ZZ', 'XY', ]
available_originir_2q3p_gates = ['PHASE2Q']
available_originir_2q15p_gates = ['UU15']
available_originir_3p_gates = ['TOFFOLI', 'CSWAP']

angular_gates = (available_originir_1q1p_gates + 
                 available_originir_2q1p_gates +
                 available_originir_1q2p_gates +
                 available_originir_1q3p_gates + 
                 available_originir_2q1p_gates +
                 available_originir_2q3p_gates +
                 available_originir_2q15p_gates)

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


available_originir_error_channel_1q1p = ['Depolarizing', 
                                         'BitFlip', 
                                         'PhaseFlip', 
                                         'AmplitudeDamping']

available_originir_error_channel_1q3p = ['PauliError1Q']

available_originir_error_channel_1qnp = ['Kraus1Q']

available_originir_error_channel_2q1p = ['TwoQubitDepolarizing', ]

available_originir_error_channel_2q15p = ['PauliError2Q', ]

available_originir_error_channels = {
    gatename : {'qubit': 1, 'param': 1}
    for gatename in available_originir_error_channel_1q1p
}

available_originir_error_channels.update({
    gatename : {'qubit': 1, 'param': 3}
    for gatename in available_originir_error_channel_1q3p
})

available_originir_error_channels.update({
    # There will raise an error if it is used in the random_originir
    # TODO: add the random generation of Kraus1Q channel
    gatename : {'qubit': 1, 'param': -1}
    for gatename in available_originir_error_channel_1qnp
})

available_originir_error_channels.update({
    gatename : {'qubit': 2, 'param': 1}
    for gatename in available_originir_error_channel_2q1p
})

available_originir_error_channels.update({
    gatename : {'qubit': 2, 'param': 15}
    for gatename in available_originir_error_channel_2q15p
})

def generate_sub_error_channel_originir(channel_list):
    return {k : v for k, v in available_originir_error_channels.items() if k in channel_list}