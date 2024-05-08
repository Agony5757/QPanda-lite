import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit


def iswap_test():
    sim = qsim.Simulator()
    sim.init_n_qubit(3)   
    sim.sx(1)
    sim.xy(0, 1)
    
    print(sim.state)

def run_test_general():
    pass

if __name__ == '__main__':
    iswap_test()