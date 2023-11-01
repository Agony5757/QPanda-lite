import numpy as np
import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import TdgGate, RXGate
from qiskit import BasicAer
from qpandalite.simulator import Simulator, NoisySimulator
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit


# Define the number of qubits
n_qubit = 2

# Noise description
noise_description = {
	"depolarizing": 0.05,  # 5% depolarizing noise
	"damping": 0.03,       # 3% damping noise
	"bitflip": 0.02,       # 2% bitflip noise
	"phaseflip": 0.04      # 4% phaseflip noise
}


# Measurement error matrices (placeholder values)
measurement_error = [
	[0.9, 0.1],
	[0.1, 0.9]
]

# Create an instance of the NoisySimulator
simulator = NoisySimulator(n_qubit, noise_description, measurement_error)

# Apply a Hadamard gate to the first qubit
simulator.hadamard(0, False)

simulator.insert_error([0, 1])

noise_desc = simulator.noise

print(noise_desc)
# ... and so on

# NOTE: Since I don't have the complete API for NoisySimulator, I'm only showing a basic usage example.
# Depending on what other methods you have in your NoisySimulator class, you might call them as well.

# Assume you have a method to run the simulation and get the result:
# result = simulator.run()
# print(result)
