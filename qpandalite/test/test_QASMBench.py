import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
from qpandalite.qasm_origin import OpenQASM2_Parser
from qpandalite.circuit_builder import Circuit
from pathlib import Path
import pickle
from qpandalite.test._utils import qpandalite_test

def load_QASMBench(path):
    path = Path(path)
    filename = path / 'QASMBench.pkl'

    with open(filename, 'rb') as fp:
        dataset = pickle.load(fp)

    return dataset

def test_qasm(path = './qpandalite/test'):
    dataset = load_QASMBench(path)
    print(dataset)
    print(len(dataset))

    count = 0
    for circuit in dataset:
        if 'gate' not in circuit:
            count += 1
            print(circuit)
            
    print(count)

@qpandalite_test('Test QASMBench')
def run_test_qasm():
    test_qasm()

if __name__ == '__main__':
    test_qasm()