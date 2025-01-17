import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
# from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.originir.originir_base_parser import OriginIR_BaseParser
from qpandalite.circuit_builder import Circuit
from qpandalite.test._utils import qpandalite_test

@qpandalite_test('OriginIR Parser')
def run_test_originir_parser():
    originir_parser_test1()    

# def barrier_test():
#     circ = QuantumCircuit(3)
#     circ.h(0)
#     circ.barrier(0)
#     circ.rx(-0.4, 0)
#     circ.barrier(1)
#     circ.x(0)
#     circ.barrier(2)
#     circ.ry(0.4, 0)
#     circ.barrier(0, 1)
#     circ.y(0)
#     circ.barrier(1, 2)
#     circ.rz(np.pi/3, 1)
#     circ.barrier(0, 1, 2)
#     circ.z(0)
#     circ.cz(0, 1)
#     circ.cx(0, 2)
#     meas = QuantumCircuit(3, 3)
#     meas.measure(range(3), range(3))
#     circ = meas.compose(circ, range(3), front=True)
#     qasm_string = circ.qasm()
#     # print("---Circuit created using Qiskit(QASM)---")
#     # print(qasm_string)
#     # Create a Circuit instance from the QASM string
#     circuit_origin = OpenQASM2_Parser.build_from_qasm_str(qasm_string)
#     # print("---OriginIR Circuit coverted from QASM---")
#     # print(circuit_origin.circuit)

#     origin_qc = QuantumCircuit.from_qasm_str(circuit_origin.qasm)
#     # print("---Back?---")

#     return origin_qc.qasm() == qasm_string

def originir_parser_test1():
    originir = '''
    QINIT 11
    CREG 5
    H q[6]
    H q[7]
    DAGGER
    Z q[2]
    DAGGER
    Z q[5]
    X q[10]
    ENDDAGGER
    ENDDAGGER
    DAGGER
    Z q[5]
    X q[10]
    CONTROL q[0], q[1]
    X q[3]
    ENDCONTROL q[0], q[1]
    ENDDAGGER
    H q[8]
    H q[9]
    MEASURE q[0], c[0]
    MEASURE q[1], c[1]
    MEASURE q[2], c[2]
    MEASURE q[3], c[3]
    MEASURE q[4], c[4]
    '''

    parser = OriginIR_BaseParser()
    parser.parse(originir)

    print(parser.program_body)
    print(parser.to_extended_originir())
    print(parser.raw_originir)
    print(parser.originir)


if __name__ == '__main__':
    run_test_originir_parser()