import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
from qpandalite.qasm import OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit
from qpandalite.test._utils import qpandalite_test

def iswap_test():
    sim = qsim.StatevectorSimulator()
    sim.init_n_qubit(3)   
    sim.sx(1)
    sim.xy(0, 1)
    
    print(sim.state)


@qpandalite_test('Test General')
def run_test_general():
    pass

if __name__ == '__main__':
    iswap_test()