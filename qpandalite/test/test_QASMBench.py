import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit
from pathlib import Path
import pickle

def load_QASMBench(path):
    path = Path(path)
    filename = path / 'QASMBench.pkl'

    # with open(filename, 'rb') as fp:
    #     pickle.load(fp)

    sim = qsim.Simulator()
    sim.init_n_qubit(3)   
    sim.sx(1)
    sim.xy(0, 1, 0)
    
    print(sim.state)

def test_qasm(path = './qpandalite/test'):
    dataset = load_QASMBench(path)
    print(dataset)

def run_test_qasm():
    test_qasm()

if __name__ == '__main__':
    test_qasm()