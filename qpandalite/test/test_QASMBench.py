import qpandalite
import qpandalite.simulator as qsim
import numpy as np

import qpandalite.simulator as sim
from qpandalite.qasm import OpenQASM2_BaseParser, OpenQASM2_LineParser
from qpandalite.circuit_builder import Circuit
from pathlib import Path
import pickle
from qpandalite.test._utils import qpandalite_test
from qpandalite.qasm import NotSupportedGateError

import qiskit
import qiskit.qasm2 as qasm
from qiskit_aer import AerSimulator
from qiskit import transpile


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

    count_passed = 0
    passed_list = []
    count_not_supported = 0
    not_supported_list = []
    for circuit in dataset:
        transpiled_circuit = transpile_circuit(circuit)

        parser = OpenQASM2_BaseParser()
        try:
            parser.parse(transpiled_circuit)        
            print(parser.formatted_qasm)
            count_passed += 1
            passed_list.append(circuit)
        except NotSupportedGateError as e:
            count_not_supported += 1
            not_supported_list.append(circuit)
    
    print(count_passed, 'circuits passed')
    print(count_not_supported, 'circuits not supported')
    # print(passed_list)
    print(not_supported_list)


def transpile_circuit(qc):
    # Use the Aer simulator
    backend = AerSimulator()
    quantum_circuit = qasm.loads(qc)
    # Transpile the circuit for the backend
    transpiled_qc = transpile(quantum_circuit, backend=backend, optimization_level=0)
    
    return qasm.dumps(transpiled_qc)


@qpandalite_test('Test QASMBench')
def run_test_qasm():
    test_qasm()

if __name__ == '__main__':
    test_qasm()