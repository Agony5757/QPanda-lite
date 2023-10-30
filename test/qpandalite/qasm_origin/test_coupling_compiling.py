import numpy as np
import math
from qiskit import QuantumCircuit, BasicAer
from qiskit.circuit.random import random_circuit
from qiskit.compiler import transpile
from qiskit.transpiler import CouplingMap
import qpandalite.simulator as sim
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit

"""
From QISKit docs: https://qiskit.org/documentation/apidoc/compiler.html#qiskit.compiler.transpile

Multiple formats are supported:
1. CouplingMap instance
2. List, must be given as an adjacency matrix, where each entry specifies all directed two-qubit interactions supported by backend, 
e.g: [[0, 1], [0, 3], [1, 2], [1, 5], [2, 5], [4, 1], [5, 3]]

Optimization level 0 is intended for device characterization experiments and, 
as such, only maps the input circuit to the constraints of the target backend, without performing any optimizations. 
Optimization level 3 spends the most effort to optimize the circuit. 
"""
qubit_number = 6
my_coupling = CouplingMap.from_line(qubit_number)
my_basis_gates = ['rx', 'ry', 'rz', 'cz', 'id']

for _ in range(100):
	# Insert your quantum circuit
	q = random_circuit(qubit_number, depth=3)
	meas = QuantumCircuit(qubit_number, qubit_number)
	meas.measure(range(qubit_number), range(qubit_number))
	q = meas.compose(q, range(qubit_number), front=True)

	# select a backend
	backend = BasicAer.get_backend('qasm_simulator')

	result = transpile(q, basis_gates=my_basis_gates, coupling_map=my_coupling, optimization_level=1)
	qasm_string = result.qasm()
	# print("---Circuit created using Qiskit(QASM)---")
	# print(qasm_string)
	# # Create a Circuit instance from the QASM string
	circuit_origin = OpenQASM2_Parser.build_from_qasm_str(qasm_string)
	# print("---OriginIR Circuit coverted from QASM---")
	# print(circuit_origin.circuit)

	origin_qc = QuantumCircuit.from_qasm_str(circuit_origin.qasm)
	# print("---Back?---")
	# print(origin_qc.qasm())
	if not origin_qc.qasm() == qasm_string:
		print("bug")