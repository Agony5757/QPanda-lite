from qpandalite.task.originq_dummy.task import submit_task, _submit_task_group_dummy_impl

from qpandalite.simulator import NoisySimulator
from qpandalite.qasm_origin import OpenQASM2_Parser
import numpy as np
import qpandalite.simulator as qsim
from qpandalite.circuit_builder import Circuit
from qpandalite.originir import OriginIR_LineParser, OriginIR_BaseParser

c = Circuit()

c.h(0)
c.cz(0, 2)
c.x(0)
c.h(1)
c.z(1)
c.cnot(0, 1)
# c.iswap(0, 1)
c.rx(0, np.pi/8)
c.ry(0, np.pi/4)
c.rz(0, np.pi/2)
# c.rphi90(1, np.pi/8)
# c.rphi180(1, np.pi/4)
# c.rphi(1, np.pi/2, np.pi/4)

c.measure(0, 1, 2)

print(submit_task(c.circuit))

print(submit_task(c.circuit, noise_description = {"damping": 0.01}, gate_noise_description={}))
