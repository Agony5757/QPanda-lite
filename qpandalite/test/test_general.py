import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit

from . import common_gates 

def iswap_test():
    sim = qsim.Simulator()
    sim.init_n_qubit(2)
    # Create the vector
    vector = np.zeros(2**2)
    vector[0] = 1   
    sim.hadamard(0)
    sim.hadamard(1)
    # sim.xy(0, 1, np.pi/8)

    result = np.kron(common_gates.H_Gate, common_gates.H_Gate) @ vector
    if not np.allclose(result, np.array(sim.state)):
        print(result, np.array(sim.state))
        raise AssertionError("iswap_test failed")


def run_test_general():
    pass

if __name__ == '__main__':
    iswap_test()