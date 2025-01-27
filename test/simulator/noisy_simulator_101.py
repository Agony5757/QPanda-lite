import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import TdgGate, RXGate
from qiskit import BasicAer
from qpandalite.simulator import StatevectorSimulator, NoisySimulator
from qpandalite.qasm import OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit


# Define the number of qubits
n_qubit = 2

# Noise description
noise_description = {
	"depolarizing": 0,  # 5% depolarizing noise
	"damping": 0,       # 3% damping noise
	"bitflip": 0,       # 2% bitflip noise
	"phaseflip": 0      # 4% phaseflip noise
}


# Measurement error matrices (placeholder values)
measurement_error = [
	[0.9, 0.1],
	[0.1, 0.9]
]

# Create an instance of the NoisySimulator
simulator = NoisySimulator(n_qubit, noise_description, measurement_error)

# Apply a Hadamard gate to the first qubit
simulator.x(0)
simulator.insert_error([0, 1])
simulator.hadamard(0)
simulator.insert_error([3, 4])
simulator.insert_error([0])
simulator.x(1)
simulator.hadamard(1)
simulator.insert_error([0, 1])

# BUG: CNOT?
simulator.cnot(0, 1)
simulator.insert_error([0])
simulator.cz(0, 1)
simulator.insert_error([2])
simulator.y(0)
simulator.hadamard(0)
simulator.z(1)
simulator.hadamard(1)

# Adding a layer of error right after the two-gates will induce the bug
simulator.insert_error([0, 1])
simulator.insert_error([2, 3])
# noise_desc = simulator.noise

# print(noise_desc)


# Create an instance of the NoisySimulator
simulator = NoisySimulator(n_qubit, noise_description, measurement_error)

# Apply a Hadamard gate to the first qubit
simulator.hadamard(0)
simulator.hadamard(1)
simulator.iswap(0, 1)
simulator.rx(0, np.pi/8)
simulator.ry(0, np.pi/4)
simulator.rz(0, np.pi/2)
simulator.rphi90(1, np.pi/8)
simulator.rphi180(1, np.pi/4)
simulator.rphi(1, np.pi/2, np.pi/4)
# Number of measurement shots
shots = 1

# # Measure the state multiple times
measurement_results = simulator.measure_shots(shots)


import qpandalite.simulator as qsim

sim = qsim.StatevectorSimulator()

sim.init_n_qubit(2)
sim.hadamard(0, False)
sim.hadamard(1, False)
sim.iswap(0, 1, False)
sim.rx(0, np.pi/8, False)
sim.ry(0, np.pi/4, False)
sim.rz(0, np.pi/2, False)
sim.rphi90(1, np.pi/8, False)
sim.rphi180(1, np.pi/4, False)
sim.rphi(1, np.pi/2, np.pi/4, False)
print(sim.state)

# # Display the measurement results
# print(f"Measurement Results over {shots} shots:")
# for state, count in measurement_results.items():
#     # Convert the state (integer) to binary representation
#     binary_state = format(state, f'0{n_qubit}b')
#     print(f"State |{binary_state}>: {count} occurrences")
