from qpandalite.simulator import StatevectorSimulator, NoisySimulator, NoisySimulator_GateDependent
from qpandalite.simulator import seed
import numpy as np
import json

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

single_exps_sup = {}
single_exps_normal = {}

for noise_strength in [1e-1, 5e-2, 1e-2, 5e-3, 1e-3, 5e-4, 1e-4]:
	print(noise_strength)
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
	    "Y": {"depolarizing": noise_strength},
	    "Z": {"depolarizing": noise_strength}
	}

	# Define the measurement errors
	readout_error = [(0.01, 0.01), (0.02, 0.02)]

	culmu = 0
	condition_prob = []

	single_exps_sup[noise_strength] = []
	single_exps_normal[noise_strength] = []

	for C in single_qubit_cliffords:
		# Create an instance of the NoisySimulator
		simulator = NoisySimulator_GateDependent(3, noise_description, gate_noise_description)

		simulator.hadamard(0)
		# apply_single_clifford(C, simulator, 1, inverse=False)

		simulator.x(0)
		simulator.cnot(2, 1)
		simulator.cnot_cont(1, 2, [0])
		simulator.cnot(2, 1)
		simulator.x(0)

		simulator.id(2)

		simulator.x(0)
		simulator.cnot(2, 1)
		simulator.cnot_cont(1, 2, [0])
		simulator.cnot(2, 1)
		simulator.x(0)

		simulator.cnot(2, 1)
		simulator.cnot_cont(1, 2, [0])
		simulator.cnot(2, 1)

		simulator.id(2)

		simulator.cnot(2, 1)
		simulator.cnot_cont(1, 2, [0])
		simulator.cnot(2, 1)

		simulator.hadamard(0)

		# apply_single_clifford(C, simulator, 1, inverse=True)
		
		measurement_results = simulator.measure_shots(shots)
		aa = 0
		culmu = 0
		for key in list(measurement_results.keys()):  # Use list to avoid RuntimeError for changing dict size during iteration
			if int(key) % 2 == 0:  # Check if the key is even
				culmu += measurement_results[key]
			if int(key) in [0,4]:
				aa += measurement_results[key]
		
		condition_prob.append(1 - aa / culmu)
	# single_exps_sup[noise_strength].append(measurement_results[0] / shots)
		# print(measurement_results)

	print('Suppression')
	print(np.array(condition_prob).mean())
	# single_exps_sup[noise_strength].append(culmu / shots / len(single_qubit_cliffords))
	# print((2 * noise_strength **2 - 9 * noise_strength + 9) / (4 * noise_strength **2 - 6 * noise_strength + 9))
	

	culmu = 0

	for C in single_qubit_cliffords:
		# print(C)
		simulator = NoisySimulator(1, noise_description, gate_noise_description)

		apply_single_clifford(C, simulator, 0, inverse=False)
		simulator.id(0)	
		apply_single_clifford(C, simulator, 0, inverse=True)
		
		# Measure the state multiple times
		measurement_results = simulator.measure_shots(shots)
		culmu += measurement_results[0]
		single_exps_normal[noise_strength].append(measurement_results[0] / shots)
		# print(measurement_results)

	print('Raw')
	print(1 - culmu / shots / len(single_qubit_cliffords))
	# single_exps_normal[noise_strength].append(measurement_results[0] / shots)
	# print(1 - 2 * noise_strength /3)
	print()

# print(single_exps)
# Save the dictionary to a JSON file
# with open('data_sup.json', 'w') as file:
#     json.dump(single_exps_sup_state0, file)

# with open('data_normal.json', 'w') as file:
#     json.dump(single_exps_normal, file)