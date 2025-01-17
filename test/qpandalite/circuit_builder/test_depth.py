import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import TdgGate, RXGate
from qiskit import BasicAer
from qiskit.transpiler import CouplingMap
from qiskit.compiler import transpile
from qiskit.circuit.random import random_circuit
import qpandalite.simulator as sim
from qpandalite.qasm import OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit

c = Circuit()
c.h(0)
c.cnot(1, 0)
c.cnot(0, 2)  
# Single control(Correct)
with c.control(0, 1, 2):
    c.x(4)

# Single dagger(Correct)
with c.dagger():
    c.z(5)
    c.x(10)

# Nested-dagger
with c.dagger():
    c.z(2)
    with c.dagger():
        c.z(5)
        c.x(10)

# Nested-control(Correct)
with c.control(0,1):
    c.x(2)
    with c.control(4,5):
        c.x(3)

# Control-dagger-nested
with c.control(2):
    c.x(4)
    with c.dagger():
        c.z(5)
        c.x(10)
        with c.control(0,1):
            c.x(3)

# Dagger-control-nested
with c.dagger():
    c.z(5)
    c.x(10)
    with c.control(0,1):
        c.x(3)

c.h(8)
c.h(9)

print(c.depth)


qubit_number = 6
my_coupling = CouplingMap.from_line(qubit_number)
my_basis_gates = ['h', 'x', 'y', 'z', 'rx', 'ry', 'rz', 'cz', 'id']

for _ in range(100):
	# Insert your quantum circuit
	q = random_circuit(qubit_number, depth=3)
	meas = QuantumCircuit(qubit_number, qubit_number)
	meas.measure(range(qubit_number), range(qubit_number))
	# q = meas.compose(q, range(qubit_number), front=True)
	q.data = [(op, qubits, clbits) for op, qubits, clbits in q.data if q.name != "id"]

	# select a backend
	backend = BasicAer.get_backend('qasm_simulator')

	result = transpile(q, basis_gates=my_basis_gates, coupling_map=my_coupling, optimization_level=1)

	# This is to exclude the "id" operation, which is not supported in the OriginIR
	for index in reversed(range(len(result.data))):
	    if result.data[index][0].name == "id":
	        del result.data[index]
	
	qasm_string = result.qasm()
	

	circuit_origin = OpenQASM2_LineParser.build_from_qasm_str(qasm_string)
	origin_qc = QuantumCircuit.from_qasm_str(circuit_origin.qasm)

	if not circuit_origin.depth == origin_qc.depth():
		print(f"depth is not the same, OrginIR:{circuit_origin.depth}, Qiskit:{origin_qc.depth()}")