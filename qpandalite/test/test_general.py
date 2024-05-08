import qpandalite
import qpandalite.simulator as qsim

import numpy

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