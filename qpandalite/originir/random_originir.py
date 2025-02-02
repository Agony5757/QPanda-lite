# random_originir.py is a python file that generates random OriginIR code.

import random

from qpandalite.circuit_builder.qcircuit import opcode_to_originir_line
from .originir_spec import available_originir_gates, angular_gates, available_originir_error_channels

def build_originir_gate(gate, qubits, params, dagger_flag = False, 
                        control_qubit_set = None):
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
    
    # qubit_str = ",".join([f"q[{qubit}]" for qubit in qubits])
    
    # dagger_str = " dagger" if dagger_flag else ""
    
    # if params:
    
    #     param_str = [f"{param}" for param in params]
    #     param_str = ",".join(param_str)

    #     return f"{gate} {qubit_str}, ({param_str})"
    
    # else:
    #     return f"{gate} {qubit_str}"

    opcode = (gate, qubits, None, params, dagger_flag, control_qubit_set)
    # print(opcode)
    return opcode_to_originir_line(opcode)


def build_originir_error_channel(channel, qubits, params):
    '''
    Build a line of OriginIR code for a given error channel, qubits, and parameters.
    
    Args:
        channel (str): The name of the error channel.
        qubits (list): A list of qubits the error channel acts on.
        
    Returns:
        str: A line of OriginIR code
    '''

    if not qubits:
        raise ValueError("No qubits specified for error channel")
    
    if channel not in available_originir_error_channels:
        raise ValueError(f"Error channel {channel} not available in OriginIR")
    
    if len(qubits)!= available_originir_error_channels[channel]['qubit']:
        raise ValueError(f"Error channel {channel} requires {available_originir_error_channels[channel]['qubit']} qubits")
    
    qubit_str = ",".join([f"q[{qubit}]" for qubit in qubits])
    
    param_str = [f"{param}" for param in params]
    param_str = ",".join(param_str)

    return f"{channel} {qubit_str}, ({param_str})"

def build_full_measurements(n_qubits):
    '''
    Build a line of OriginIR code for a full measurement on a set of qubits.
    
    Args:
        n_qubits (list): Number of qubits to measure.
        
    Returns:
        str: A line of OriginIR code
    '''

    measure_instructions = []
    for qubit in range(n_qubits):
        measure_instructions.append(f"MEASURE q[{qubit}], c[{qubit}]")

    return measure_instructions

def random_originir(n_qubits, n_gates, 
                    instruction_set = available_originir_gates,
                    channel_set = None,
                    allow_control = False,
                    allow_dagger = False):
    '''
    Generate a random OriginIR program with a given number of qubits and gates.
    
    Args:
        n_qubits (int): The number of qubits in the program.
        n_gates (int): The number of gates in the program.
        instruction_set (dict): A dictionary of available gates and their properties.
        
    Returns:
        str: A string of OriginIR code.
    '''

    program = [f'QINIT {n_qubits}',
               f'CREG {n_qubits}']
    
    instructions = list(instruction_set.keys())
    if channel_set is not None:
        instructions.extend(channel_set.keys())
    
    for i in range(n_gates):
        gate_name = random.choice(list(instructions))

        if gate_name in instruction_set:
            nqubit =instruction_set[gate_name]['qubit']
            nparam =instruction_set[gate_name]['param']
            qubits_to_act = random.sample(range(n_qubits), nqubit)
            params = []
            if gate_name in angular_gates:
                params = [random.uniform(0, 2*3.14159) for _ in range(nparam)]
            elif nparam > 0:
                raise NotImplementedError(f"Gate {gate_name} not implemented")
            
            if allow_control:
                remaining_qubits = set(range(n_qubits)) - set(qubits_to_act)
                #control_qubits = random.sample(remaining_qubits, random.randint(0, len(remaining_qubits)))
                control_qubits = random.sample(remaining_qubits, random.randint(0, 1))
            else:
                control_qubits = None

            if allow_dagger:
                dagger_flag = random.choice([True, False])
            else:
                dagger_flag = False

            program.append(build_originir_gate(gate_name, qubits_to_act, params, dagger_flag, control_qubits))

        elif gate_name in channel_set:
            nqubit = channel_set[gate_name]['qubit']
            nparam = channel_set[gate_name]['param']
            qubits_to_act = random.sample(range(n_qubits), nqubit)
            params = [random.uniform(0, 1/15) for _ in range(nparam)]
            program.append(build_originir_error_channel(gate_name, qubits_to_act, params))

        else:
            raise ValueError(f"Instruction {gate_name} not available in OriginIR")
            
    program.extend(build_full_measurements(n_qubits))

    originir = "\n".join(program)

    # print(originir)
    return originir

