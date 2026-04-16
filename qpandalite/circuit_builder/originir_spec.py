"""OriginIR language specification for quantum gates and error channels.

This module defines the available gates and error channels in OriginIR format,
including their qubit requirements and parameter counts. It also provides
utility functions for generating subsets of gates and error channels.

Key exports:
    available_originir_gates: Dictionary of all available OriginIR gates.
    angular_gates: List of gates that accept angular parameters.
    available_originir_error_channels: Dictionary of available error channels.
    available_originir_error_channels_without_kraus: Error channels excluding Kraus operators.
    generate_sub_gateset_originir: Function to generate a subset of gates.
    generate_sub_error_channel_originir: Function to generate a subset of error channels.
"""

__all__ = [
    "available_originir_gates",
    "angular_gates",
    "available_originir_error_channels",
    "available_originir_error_channels_without_kraus",
    "generate_sub_gateset_originir",
    "generate_sub_error_channel_originir",
]

available_originir_1q_gates = ["H", "X", "Y", "Z", "S", "SX", "T", "I"]
available_originir_1q1p_gates = [
    "RX",
    "RY",
    "RZ",
    "U1",
    "RPhi90",
    "RPhi180",
]
available_originir_1q2p_gates = ["RPhi", "U2"]
available_originir_1q3p_gates = ["U3"]
available_originir_2q_gates = [
    "CNOT",
    "CZ",
    "ISWAP",
]  # TODO: SQISWAP
available_originir_2q1p_gates = [
    "XX",
    "YY",
    "ZZ",
    "XY",
]
available_originir_2q3p_gates = ["PHASE2Q"]
available_originir_2q15p_gates = ["UU15"]
available_originir_3p_gates = ["TOFFOLI", "CSWAP"]

available_barrier_gates = ["BARRIER"]

angular_gates = (
    available_originir_1q1p_gates
    + available_originir_2q1p_gates
    + available_originir_1q2p_gates
    + available_originir_1q3p_gates
    + available_originir_2q1p_gates
    + available_originir_2q3p_gates
    + available_originir_2q15p_gates
)

available_originir_gates = {gatename: {"qubit": 1, "param": 0} for gatename in available_originir_1q_gates}

available_originir_gates.update({gatename: {"qubit": 1, "param": 1} for gatename in available_originir_1q1p_gates})

available_originir_gates.update({gatename: {"qubit": 1, "param": 2} for gatename in available_originir_1q2p_gates})

available_originir_gates.update({gatename: {"qubit": 2, "param": 0} for gatename in available_originir_2q_gates})

available_originir_gates.update({gatename: {"qubit": 2, "param": 1} for gatename in available_originir_2q1p_gates})

available_originir_gates.update({gatename: {"qubit": 2, "param": 3} for gatename in available_originir_2q3p_gates})

available_originir_gates.update({gatename: {"qubit": 2, "param": 15} for gatename in available_originir_2q15p_gates})

available_originir_gates.update({gatename: {"qubit": 3, "param": 0} for gatename in available_originir_3p_gates})

available_originir_gates.update({gatename: {"qubit": -1, "param": 0} for gatename in available_barrier_gates})


def generate_sub_gateset_originir(gate_list):
    """Generate a subset of the OriginIR gateset filtered by gate names.

    Args:
        gate_list (list[str]): List of gate names to include in the subset.

    Returns:
        dict[str, dict]: A dictionary containing only the gates specified in
            gate_list, with their qubit and parameter requirements.
    """
    return {k: v for k, v in available_originir_gates.items() if k in gate_list}


available_originir_error_channel_1q1p = ["Depolarizing", "BitFlip", "PhaseFlip", "AmplitudeDamping"]

available_originir_error_channel_1q3p = ["PauliError1Q"]

available_originir_error_channel_1qnp = ["Kraus1Q"]

available_originir_error_channel_2q1p = [
    "TwoQubitDepolarizing",
]

available_originir_error_channel_2q15p = [
    "PauliError2Q",
]

available_originir_error_channels = {
    gatename: {"qubit": 1, "param": 1} for gatename in available_originir_error_channel_1q1p
}

available_originir_error_channels.update(
    {gatename: {"qubit": 1, "param": 3} for gatename in available_originir_error_channel_1q3p}
)

available_originir_error_channels.update(
    {
        # There will raise an error if it is used in the random_originir
        # TODO: add the random generation of Kraus1Q channel
        gatename: {"qubit": 1, "param": -1}
        for gatename in available_originir_error_channel_1qnp
    }
)

available_originir_error_channels.update(
    {gatename: {"qubit": 2, "param": 1} for gatename in available_originir_error_channel_2q1p}
)

available_originir_error_channels.update(
    {gatename: {"qubit": 2, "param": 15} for gatename in available_originir_error_channel_2q15p}
)


def generate_sub_error_channel_originir(channel_list):
    """Generate a subset of the OriginIR error channels filtered by channel names.

    Args:
        channel_list (list[str]): List of error channel names to include in the subset.

    Returns:
        dict[str, dict]: A dictionary containing only the error channels specified
            in channel_list, with their qubit and parameter requirements.
    """
    return {k: v for k, v in available_originir_error_channels.items() if k in channel_list}


# TODO: This is a temporary workaround. When Kraus1Q random generation
# is implemented, remove this wrapper and use available_originir_error_channels
# directly. Also revert the corresponding change in test_random_OriginIR.py.
available_originir_error_channels_without_kraus = {
    k: v for k, v in available_originir_error_channels.items() if k not in available_originir_error_channel_1qnp
}
