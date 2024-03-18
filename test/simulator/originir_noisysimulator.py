from qpandalite.simulator import OriginIR_Simulator, OriginIR_NoisySimulator
import numpy as np
from qpandalite import Circuit

from qpandalite.simulator import seed
import time

current_time_seed = int(time.time())
seed(current_time_seed)
print(current_time_seed)

n_q = 5
available_qubits = [13, 15, 17, 18, 19, 21]
remapping = dict(zip(range(n_q), available_qubits[0:n_q]))
qc = Circuit()
qc.h(0)
qc.h(1)
qc.x(2)
qc.h(3)
qc.h(4)
qc.measure(0,1,2,3)
qc.remapping(remapping)

# Noise description
noise_description = {
	"depolarizing": 0.0,  # 5% depolarizing noise
	"damping": 0.,       # 3% damping noise
	"bitflip": 0.,       # 2% bitflip noise
	"phaseflip": 0.      # 4% phaseflip noise
}

gate_noise_description = {
    "X": {"depolarizing": 0.0},
    "HADAMARD": {"depolarizing": 0.0},
    "ISWAP": {"depolarizing": 0.0}
}
sim = OriginIR_Simulator()
sim.simulate(qc.originir)
result0 = np.abs(sim.state)**2
print(f'ideal result: {result0}')


nsim = OriginIR_NoisySimulator(noise_description=noise_description,
                               gate_noise_description=gate_noise_description)
# print(qc.originir)
print(qc.measure_list)
print(qc.used_qubit_list)
# print(qc.circuit_str)
# print(f'remapping:{remapping}')
result = nsim.simulate(qc.originir, shots=10000)

_sum = 0
for key, value in result.items():
    _sum += value
print(f'noisy result: {result}')
print(_sum)







