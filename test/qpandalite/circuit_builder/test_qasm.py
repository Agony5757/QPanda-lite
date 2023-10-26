import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import TdgGate, RXGate
from qiskit import BasicAer
import qpandalite.simulator as sim
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit


circ = QuantumCircuit(3)
circ.h(0)
circ.rx(-0.4, 0)
circ.x(0)
circ.ry(0.4, 0)
circ.y(0)
circ.rz(math.pi/3, 1)
circ.z(0)
circ.cz(0, 1)
circ.cx(0, 2)
meas = QuantumCircuit(3, 3)
meas.measure(range(3), range(3))
circ = meas.compose(circ, range(3), front=True)
qasm_string = circ.qasm()
print("---Circuit created using Qiskit(QASM)---")
print(qasm_string)
# Create a Circuit instance from the QASM string
circuit_origin = OpenQASM2_Parser.build_from_qasm_str(qasm_string)
print("---OriginIR Circuit coverted from QASM---")
print(circuit_origin.circuit)

origin_qc = QuantumCircuit.from_qasm_str(circuit_origin.qasm)
print("---Back?---")
print(origin_qc.qasm())