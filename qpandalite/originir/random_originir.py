# random_originir.py is a python file that generates random OriginIR code.

import random
from .originir_spec import available_originir_gates, angular_gates

def build_originir_gate(gate, qubits, params):
    '''
    Build a line of OriginIR code for a given gate, qubits, and parameters.
    
    Args:
        gate (str): The name of the gate.
        qubits (list): A list of qubits the gate acts on.
        params (list): A list of parameters for the gate.
        
    Returns:
        str: A line of OriginIR code
    '''

    if not qubits:
        raise ValueError("No qubits specified for gate")
    
    if gate not in available_originir_gates:
        raise ValueError(f"Gate {gate} not available in OriginIR")
    
    if len(qubits)!= available_originir_gates[gate]['qubit']:
        raise ValueError(f"Gate {gate} requires {available_originir_gates[gate]['qubit']} qubits")
    
    if len(params)!= available_originir_gates[gate]['param']:
        raise ValueError(f"Gate {gate} requires {available_originir_gates[gate]['param']} parameters")
    
    qubit_str = ",".join([f"q{qubit}" for qubit in qubits])
    gate_str = f"{gate}({qubit_str})"
    
    if params:
    
        param_str = [f"{param}" for param in params]
        param_str = ",".join(param_str)

        return f"{gate_str} {qubit_str}, {param_str}"
    
    else:
        return f"{gate_str} {qubit_str}"
    
def build_full_measurements(qubits):
    '''
    Build a line of OriginIR code for a full measurement on a set of qubits.
    
    Args:
        qubits (list): A list of qubits to measure.
        
    Returns:
        str: A line of OriginIR code
    '''

    measure_instructions = []
    for qubit in qubits:
        measure_instructions.append(f"MEASURE q[{qubit}], c[{qubit}]")

    return measure_instructions

def random_originir(n_qubits, n_gates, instruction_set = available_originir_gates):
    '''
    Generate a random OriginIR program with a given number of qubits and gates.
    
    Args:
        n_qubits (int): The number of qubits in the program.
        n_gates (int): The number of gates in the program.
        instruction_set (dict): A dictionary of available gates and their properties.
        
    Returns:
        str: A string of OriginIR code.
    '''

    program = ['QINIT {n_qubits}',
               'CREG {n_qubits}']
    
    instructions = list(instruction_set.keys())
    
    for i in range(n_gates):
        gate_name = random.choice(list(instructions))
        nqubit =instruction_set[gate_name]['qubit']
        nparam =instruction_set[gate_name]['param']
        qubits_to_act = random.sample(range(n_qubits), nqubit)

        if gate_name in angular_gates:
            params = [random.uniform(0, 2*3.14159) for _ in range(nparam)]
        else:
            raise NotImplementedError(f"Gate {gate_name} not implemented")
        program.append(build_originir_gate(gate_name, qubits_to_act, params))
    
    program.extend(build_full_measurements(qubits))