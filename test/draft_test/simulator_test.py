import math
import qpandalite.simulator as qsim

sim = qsim.Simulator()

sim.init_n_qubit(6)
print(len(sim.state))
print(sim.state)

print(sim.total_qubit)

sim.hadamard(0)
sim.cnot(0,1)
sim.cnot(1,3)
sim.cnot(0,2)
sim.cnot(1,4)
sim.cnot(3,5)
sim.z(0)
print(sim.state)
print(sim.get_prob(1, 0))
sim.z(1)
print(sim.state)
print(sim.get_prob(1, 0))

sim.init_n_qubit(6)
sim.rphi(0, 0, math.pi)
sim.rphi(1, 0, math.pi)
sim.rphi180(2, 0)
sim.rphi(3, 0, math.pi / 2)
sim.rphi90(4, 0)
print(sim.state)
print(sim.pmeasure(0))
print(sim.pmeasure(1))
print(sim.pmeasure(2))
print(sim.pmeasure(3))
print(sim.pmeasure(4))