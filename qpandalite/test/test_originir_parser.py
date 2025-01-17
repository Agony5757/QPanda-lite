import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
from qpandalite.qasm import OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit
from qpandalite.test._utils import qpandalite_test


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
#     circuit_origin = OpenQASM2_LineParser.build_from_qasm_str(qasm_string)
#     # print("---OriginIR Circuit coverted from QASM---")
#     # print(circuit_origin.circuit)

#     origin_qc = QuantumCircuit.from_qasm_str(circuit_origin.qasm)
#     # print("---Back?---")

#     return origin_qc.qasm() == qasm_string

@qpandalite_test('Test OriginIR Parser')
def run_test_originir_parser():
    pass

if __name__ == '__main__':
    run_test_originir_parser()