from pyqpanda3.core import draw_qprog, PIC_TYPE
from pyqpanda3.intermediate_compiler import convert_originir_string_to_qprog
from .converter import convert_qasm_to_oir, convert_oir_to_qasm

def _from_originir(originir_str):
    qprog = convert_originir_string_to_qprog(originir_str)
    return qprog

def _from_qasm(qasm_str):
    oir_str = convert_qasm_to_oir(qasm_str)
    qprog = _from_originir(oir_str)
    return qprog

def draw(ir_str, language='OriginIR'):
    ''' 
    Draw the circuit in text format.

    Args:
        ir_str (str): The input circuit in OriginIR or QASM format.
        language (str): The language of the input circuit. Default is 'OriginIR'.

    Returns:
        qprog (QProg): The QProg object of the input circuit.
    
    '''

    if language == 'OriginIR':
        qprog = _from_originir(ir_str)
    elif language == 'QASM':
        qprog = _from_qasm(ir_str)
    else:
        raise ValueError(f"Unsupported language: {language}. \n")

    print(draw_qprog(qprog, PIC_TYPE.TEXT, {}, param_show=True))
    return qprog


if __name__ == '__main__':
    from qpandalite.circuit_builder import random_originir, generate_sub_gateset_originir

    # small set
    gate_set = ['H', 'X', 'Y', 'Z',
                'RX', 'RY', 'RZ', 'RPhi', 'U3'
                ]
    
    gate_set = generate_sub_gateset_originir(gate_set)

    originir_str = random_originir(n_qubits=5, n_gates=10, instruction_set=gate_set)

    qprog = draw(originir_str)
