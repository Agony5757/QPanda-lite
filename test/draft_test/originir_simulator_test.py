import qpandalite.simulator as qsim

sim = qsim.OriginIR_Simulator(reverse_key=False)

originir = '''
QINIT 72
CREG 2
RY q[45],(0.9424777960769379)
RY q[46],(0.9424777960769379)
CZ q[45],q[46]
RY q[45],(-0.25521154)
RY q[46],(0.26327053)
X q[46]
MEASURE q[45],c[0]
MEASURE q[46],c[2]
MEASURE q[52],c[1]
'''

res = sim.simulate(originir)
print(res)
print(sim.state)


originir = '''
QINIT 72
CREG 2
RY q[45],(0.9424777960769379)
RY q[46],(0.9424777960769379)
CZ q[45],q[46]
RY q[45],(-0.25521154)
RY q[46],(0.26327053)
X q[46]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
'''

res = sim.simulate(originir)
print(res)
print(sim.state)