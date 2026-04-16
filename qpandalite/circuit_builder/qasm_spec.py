"""OpenQASM 2.0 language specification for quantum gates.

This module defines the available gates in OpenQASM 2.0 format, including their
qubit requirements and parameter counts. It provides a utility function for
generating subsets of gates based on a given list.

Key exports:
    available_qasm_gates: Dictionary of all available OpenQASM 2.0 gates.
    generate_sub_gateset_qasm: Function to generate a subset of gates.
"""

__all__ = [
    "available_qasm_gates",
    "generate_sub_gateset_qasm",
]

available_qasm_1q_gates = ["id", "h", "x", "y", "z", "s", "sdg", "sx", "sxdg", "t", "tdg"]
available_qasm_1q1p_gates = ["rx", "ry", "rz", "u1"]
available_qasm_1q2p_gates = ["u2"]
available_qasm_1q3p_gates = ["u3", "u"]
available_qasm_2q_gates = ["cx", "cy", "cz", "swap"]
available_qasm_3q_gates = ["ccx", "cswap"]
available_qasm_4q_gates = ["c3x"]
available_qasm_2q1p_gates = ["crx", "cry", "crz", "cu1", "rxx", "rzz"]

available_qasm_gates = {gatename: {"qubit": 1, "params": 0} for gatename in available_qasm_1q_gates}

available_qasm_gates.update({gatename: {"qubit": 1, "params": 1} for gatename in available_qasm_1q1p_gates})

available_qasm_gates.update({gatename: {"qubit": 1, "params": 2} for gatename in available_qasm_1q2p_gates})

available_qasm_gates.update({gatename: {"qubit": 1, "params": 3} for gatename in available_qasm_1q3p_gates})

available_qasm_gates.update({gatename: {"qubit": 2, "params": 0} for gatename in available_qasm_2q_gates})

available_qasm_gates.update({gatename: {"qubit": 3, "params": 0} for gatename in available_qasm_3q_gates})

available_qasm_gates.update({gatename: {"qubit": 4, "params": 0} for gatename in available_qasm_4q_gates})

available_qasm_gates.update({gatename: {"qubit": 2, "params": 1} for gatename in available_qasm_2q1p_gates})


def generate_sub_gateset_qasm(gate_list):
    """Generate a subset of the OpenQASM gateset filtered by gate names.

    Args:
        gate_list (list[str]): List of gate names to include in the subset.

    Returns:
        dict[str, dict]: A dictionary containing only the gates specified in
            gate_list, with their qubit and parameter requirements.
    """
    return {k: v for k, v in available_qasm_gates.items() if k in gate_list}
