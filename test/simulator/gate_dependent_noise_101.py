import numpy as np
import math

from qpandalite.simulator import Simulator, NoisySimulator
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit


# Define the noise descriptions
noise_description = {
    "damping": 0.01
}

# Define the gate noise descriptions
gate_noise_description = {
    "X": {"depolarizing": 0.03},
    "HADAMARD": {"depolarizing": 0.02}
}

# Define the measurement errors
measurement_error = [(0.01, 0.01), (0.02, 0.02)]

# Create an instance of the NoisySimulator
simulator = NoisySimulator(2,noise_description, gate_noise_description)

# noise_desc = simulator.noise
# gate_noise_desc = simulator.gate_dependent_noise

# print(noise_desc)
# print(gate_noise_desc)


simulator.hadamard(0)
simulator.x(0)
simulator.hadamard(1)
simulator.z(1)
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

sim = qsim.Simulator()

sim.init_n_qubit(2)
sim.hadamard(0, False)
sim.x(0, False)
sim.hadamard(1, False)
sim.z(1, False)
sim.iswap(0, 1, False)
sim.rx(0, np.pi/8, False)
sim.ry(0, np.pi/4, False)
sim.rz(0, np.pi/2, False)
sim.rphi90(1, np.pi/8, False)
sim.rphi180(1, np.pi/4, False)
sim.rphi(1, np.pi/2, np.pi/4, False)
print(sim.state)