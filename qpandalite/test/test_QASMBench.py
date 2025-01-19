import numpy as np
from qpandalite.qasm import OpenQASM2_BaseParser, OpenQASM2_LineParser
from pathlib import Path
import pickle
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.test._utils import qpandalite_test
from qpandalite.qasm import NotSupportedGateError

import qiskit
import qiskit.qasm2 as qasm
from qiskit_aer import AerSimulator
from qiskit import transpile


def _load_QASMBench(path):
    path = Path(path)
    filename = path / 'QASMBench.pkl'

    with open(filename, 'rb') as fp:
        dataset = pickle.load(fp)

    return dataset


def _transpile_circuit(qc):
    # Use the Aer simulator
    backend = AerSimulator()
    quantum_circuit = qasm.loads(qc)
    # Transpile the circuit for the backend
    transpiled_qc = transpile(quantum_circuit, backend=backend, optimization_level=0)
    
    return qasm.dumps(transpiled_qc)

def _reference_result_to_array(result):
    for key in result:
        n_qubit = len(key)
        break

    result_list = np.zeros(2**n_qubit)
    for key in result:
        index = int(key, base=2)
        result_list[index] = result[key]

    return result_list



def test_qasm(path = './qpandalite/test'):
    dataset = _load_QASMBench(path)
    # print(dataset)
    # print(len(dataset))

    count_passed = 0
    passed_list = []
    count_not_supported = 0
    not_supported_list = []
    for circuit in dataset:
        transpiled_circuit = _transpile_circuit(circuit)

        parser = OpenQASM2_BaseParser()
        try:
            print('-- Parse --')
            print(transpiled_circuit)
            parser.parse(transpiled_circuit)   
            print('-- Parse OK --')     
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

    for circuit in passed_list:
        print('---------------')
        transpiled_circuit = _transpile_circuit(circuit)
        print(transpiled_circuit)
        print(dataset[circuit])
        print('---------------')

        reference_result = _reference_result_to_array(dataset[circuit])

        qasm_simulator = QASM_Simulator()


@qpandalite_test('Test QASMBench')
def run_test_qasm():
    test_qasm()

if __name__ == '__main__':
    test_qasm()