import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import TdgGate, RXGate
from qiskit import BasicAer
import qpandalite.simulator as sim
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit

my_circ = Circuit()
my_circ.h(0)
my_circ.cnot(1, 0)
my_circ.cnot(0, 2)  
# # Single control(Correct)
with my_circ.control(0, 1, 2):
    my_circ.x(4)

# Single dagger(Correct)
with my_circ.dagger():
    my_circ.z(5)
    my_circ.x(10)

# Nested-dagger
with my_circ.dagger():
    my_circ.z(2)
    with my_circ.dagger():
        my_circ.z(5)
        my_circ.x(10)

# Nested-control(Correct)
with my_circ.control(0,1):
    my_circ.x(2)
    with my_circ.control(4,5):
        my_circ.x(3)

# Control-dagger-nested
with my_circ.control(2):
    my_circ.x(4)
    with my_circ.dagger():
        my_circ.z(5)
        my_circ.x(10)
        with my_circ.control(0,1):
            my_circ.x(3)

# Dagger-control-nested
with my_circ.dagger():
    my_circ.z(5)
    my_circ.x(10)
    with my_circ.control(0,1):
        my_circ.x(3)

my_circ.h(8)
my_circ.h(9)
my_circ.measure(0,1,2)

my_circ.analyze_circuit()
print(my_circ.unwrap())