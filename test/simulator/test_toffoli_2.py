from qpandalite.simulator import StatevectorSimulator, NoisySimulator
from qpandalite.simulator import seed
import numpy as np
import json

import time
current_time_seed = int(time.time())


noise_strength = 0
shots = 2**18

# Define the noise descriptions
noise_description = {
    # "depolarizing": 0.01
}

# Define the gate noise descriptions
gate_noise_description = {
    "X": {"depolarizing": 0.00},
    "HADAMARD": {"depolarizing": 0.00},
    "CNOT": {"depolarizing": 0.00},
    "IDENTITY": {"depolarizing": noise_strength},
    "Y": {"depolarizing": 0.00}
}

# Define the measurement errors
readout_error = [(0.01, 0.01), (0.02, 0.02)]


# Create an instance of the NoisySimulator
simulator = NoisySimulator(3, noise_description, gate_noise_description)
# simulator = Simulator()
# simulator.init_n_qubit(3)
simulator.hadamard(0)
# simulator.x(1)
# simulator.cnot(0, 1)
simulator.x(0)
simulator.cnot(2, 1)
simulator.cnot_cont(1, 2, [0])
simulator.cnot(2, 1)
simulator.x(0)

simulator.x(2)

simulator.x(0)
simulator.cnot(2, 1)
simulator.cnot_cont(1, 2, [0])
# simulator.cnot(2, 1)
# simulator.x(0)

# simulator.cnot(2, 1)
# simulator.cnot_cont(1, 2, [0])
# simulator.cnot(2, 1)

# simulator.cnot(2, 1)
# simulator.cnot_cont(1, 2, [0])
# simulator.cnot(2, 1)

# simulator.hadamard(0)


measurement_results = simulator.measure_shots(shots)

# single_exps_sup[noise_strength].append(measurement_results[0] / shots)
print(measurement_results)
