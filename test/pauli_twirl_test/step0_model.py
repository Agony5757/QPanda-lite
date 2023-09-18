import qiskit
from qiskit import QuantumCircuit
import numpy as np


def CNOT():
    cir = QuantumCircuit(2)
    cir.h(1)
    cir.cz(0, 1)
    cir.h(1)
    return cir


class XY_circuit:

    def __init__(self, num, layer, parallel_pattern=None):
        self.num = num
        self.layer = layer
        # self.initial_theta = inital_theta
        # self.time = time
        if parallel_pattern is None:
            parallel_pattern = [[[i, i + 1] for i in range(0, num, 2)], [[i, i+1] for i in range(1, num, 2)]]
        self.parallel_pattern = parallel_pattern
        self.J = np.array([np.sqrt(i * (num - i)) for i in range(1, num)])
        self.start = []

    def xxyy(self, angle, type='normal'):
        cnot = CNOT()
        if type == 'normal':
            xycir = QuantumCircuit(2)
            xycir.compose(cnot, qubits=[0, 1], inplace=True)
            xycir.rx(angle, 0)
            xycir.rz(angle, 1)
            xycir.compose(cnot, qubits=[0, 1], inplace=True)
        elif type == 'start':
            xycir = QuantumCircuit(2)
            xycir.rx(np.pi / 2, 0)
            xycir.rx(np.pi / 2, 1)
            xycir.cx(0, 1)
            xycir.rx(angle, 0)
            xycir.rz(angle, 1)
            xycir.cx(0, 1)
        else:
            xycir = QuantumCircuit(2)
            xycir.cx(0, 1)
            xycir.rx(angle, 0)
            xycir.rz(angle, 1)
            xycir.cx(0, 1)
            xycir.rx(-np.pi / 2, 0)
            xycir.rx(-np.pi / 2, 1)
        return xycir

    def xy_layer(self):
        cir = QuantumCircuit(self.num)
        for pattern in self.parallel_pattern:
            for cz in pattern:
                if cz[0] >= self.num or cz[1] >= self.num:
                    continue
                q1 = cz[0]
                q2 = cz[1]
                angle = self.J[cz[0]] * self.dt / 2
                xycir = self.xxyy(angle)
                cir.compose(xycir, qubits=[q1, q2], inplace=True)
        cir.barrier(range(self.num))
        return cir

    def ising_simulation_time(self, initial_theta, time,):

        prog = QuantumCircuit(self.num, self.num)
        prog.rx(initial_theta, 0)
        self.dt = time / self.layer
        # prog.barrier(range(self.num))
        for i in range(self.num):
            prog.rx(np.pi/2, i)
        for i in range(self.layer):
            single_layer = self.xy_layer()
            prog.compose(single_layer, inplace=True)
        for i in range(self.num):
            prog.rx(-np.pi/2, i)
        prog.measure_all(add_bits=False)

        return prog
