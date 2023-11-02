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
	"depolarizing": 0.00,  # 5% depolarizing noise
	# "damping": 0.03,       # 3% damping noise
	# "bitflip": 0.02,       # 2% bitflip noise
	# "phaseflip": 0.04      # 4% phaseflip noise
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
simulator.hadamard(1, False)
# simulator.hadamard(2, False)
# simulator.insert_error([0, 1])

noise_desc = simulator.noise

print(noise_desc)

# Number of measurement shots
shots = 100000

# Measure the state multiple times
measurement_results = simulator.measure_shots(shots)

# Display the measurement results
print(f"Measurement Results over {shots} shots:")
for state, count in measurement_results.items():
    # Convert the state (integer) to binary representation
    binary_state = format(state, f'0{n_qubit}b')
    print(f"State |{binary_state}>: {count} occurrences")
