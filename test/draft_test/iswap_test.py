import math
import qpandalite.simulator as qsim

sim = qsim.Simulator()

sim.init_n_qubit(3)

# print(len(sim.state))
# print(sim.state)
# print(sim.total_qubit)
# sim.hadamard(0)
# sim.y(0)
# sim.z(0)

# sim.hadamard(1)

sim.sx(1)

# sim.xy(0, 1)

print(len(sim.state))
print(sim.state)
print(sim.total_qubit)