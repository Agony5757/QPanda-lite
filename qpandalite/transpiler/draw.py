from pyqpanda3.core import draw_qprog, PIC_TYPE
from pyqpanda3.intermediate_compiler import convert_originir_string_to_qprog

def from_originir(originir_str):
    qprog = convert_originir_string_to_qprog(originir_str)
    return qprog

def draw(originir_str):
    qprog = from_originir(originir_str)
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
