import qpandalite.simulator as qsim

sim = qsim.Simulator()
sim.init_n_qubit(1)
# sim.x(0)
sim.rx(0, -1.57)
sim.rz(0, 1.57)
sim.hadamard(0)

print(sim.state)
print(sim.pmeasure(0))