import math
import qpandalite.simulator as qsim

sim = qsim.Simulator()

sim.init_n_qubit(2)
# print(len(sim.state))
# print(sim.state)
# print(sim.total_qubit)

sim.hadamard(0)
# sim.hadamard(1)
sim.iswap(0, 1)

print(len(sim.state))
print(sim.state)
print(sim.total_qubit)