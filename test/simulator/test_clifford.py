from qpandalite.simulator import StatevectorSimulator, NoisySimulator
from qpandalite.simulator import seed
import numpy as np
import time
current_time_seed = int(time.time())

# Use the current time as a seed
seed(current_time_seed)

single_qubit_cliffords = [
 '',
 'H', 'S',
 'HS', 'SH', 'SS',
 'HSH', 'HSS', 'SHS', 'SSH', 'SSS',
 'HSHS', 'HSSH', 'HSSS', 'SHSS', 'SSHS',
 'HSHSS', 'HSSHS', 'SHSSH', 'SHSSS', 'SSHSS',
 'HSHSSH', 'HSHSSS', 'HSSHSS'
]

def apply_single_clifford(clifford_string, qsim, target_qbit, inverse=False):
	if inverse:
		clifford_string_actual_order = clifford_string[::-1]
	else:
		clifford_string_actual_order = clifford_string

	for gate in clifford_string_actual_order:
		if gate == 'H':
			qsim.hadamard(target_qbit)
		else:
			sign = -1 if inverse else 1
			qsim.rz(target_qbit, sign * np.pi/2)


# Define the noise descriptions
noise_description = {
    # "depolarizing": 0.01
}

# Define the gate noise descriptions
gate_noise_description = {
    "X": {"depolarizing": 0.00},
    "HADAMARD": {"depolarizing": 0.00},
    "CNOT": {"depolarizing": 0.00},
    "Y": {"depolarizing": 0.1}
}

# Define the measurement errors
readout_error = [(0.01, 0.01), (0.02, 0.02)]
culmu = 0
shots = 2**16
for C in single_qubit_cliffords:
	# print(C)
	simulator = NoisySimulator(1, noise_description, gate_noise_description)
	# simulator = Simulator()

	# simulator.init_n_qubit(1)
	apply_single_clifford(C, simulator, 0, inverse=False)
	simulator.y(0)
	simulator.y(0)
	apply_single_clifford(C, simulator, 0, inverse=True)
	
	# Measure the state multiple times
	measurement_results = simulator.measure_shots(shots)
	# print(simulator.state)
	# culmu += measurement_results[0]
	# print(measurement_results[0] / shots)

	# print( / shots)

print(culmu / shots / len(single_qubit_cliffords))
