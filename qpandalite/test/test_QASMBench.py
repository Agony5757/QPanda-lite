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

class NotMatchError(Exception):
    pass

def _check_result(transpiled_circuit, reference_result, backend_type):

    reference_array = _reference_result_to_array(reference_result)

    #print('Testing circuit: ', transpiled_circuit)
    #print('Reference Result: ', reference_result)
    qasm_simulator = QASM_Simulator(backend_type)
    my_result = qasm_simulator.simulate_stateprob(transpiled_circuit)

    if len(reference_array) != len(my_result):
        print('---------------')
        print(transpiled_circuit)
        print(reference_result)
        print('---------------')
        raise NotMatchError('Size not match!\n'
                        'Reference = {}\n'
                        'My Result = {}\n'.format(reference_array, my_result))
    try:
        v = np.allclose(reference_array, my_result)
    except Exception as e:       
        error_message = (
            '---------------\n'
            'Unexpected error occurred!!!\n'
            f'Transpiled Circuit: {transpiled_circuit}\n'
            f'Reference Result: {reference_result}\n'
            '---------------\n'
            f'The exception is: {str(e)}\n'
        )
        e.args = (error_message,) + e.args
        raise e
        
    if not np.allclose(reference_array, my_result):            
        raise NotMatchError(
            '---------------\n'
            f'{transpiled_circuit}\n'
            f'{reference_result}\n'
            '---------------\n'
            'Result not match!\n'
            f'Reference = {reference_array}\n'
            f'My Result = {my_result}\n'
        )

    print('Test passed!')

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
            # print('-- Parse --')
            # print(transpiled_circuit)
            parser.parse(transpiled_circuit)   
            print('-- Parse OK --')     
            # print(parser.formatted_qasm)
            count_passed += 1
            passed_list.append(circuit)
        except NotSupportedGateError as e:
            count_not_supported += 1
            not_supported_list.append(circuit)
        except Exception as e:
            raise e
    
    print(count_passed, 'circuits passed')
    print(count_not_supported, 'circuits not supported')
    # print(passed_list)
    # print(not_supported_list)

    err_list = []
    bad_circuit_list = []
    good_circuit_list = []
    for circuit in passed_list:
        try:
            transpiled_circuit = _transpile_circuit(circuit)
            _check_result(transpiled_circuit, dataset[circuit], 'statevector')
            _check_result(transpiled_circuit, dataset[circuit], 'density_operator')
            good_circuit_list.append((transpiled_circuit, dataset[circuit]))
        except NotMatchError as e:
            print('Test Failed!')
            err_list.append(e)
            bad_circuit_list.append((transpiled_circuit, dataset[circuit]))
    
    if not err_list:
        print('All circuits passed!')
        return
    
    for i, e in enumerate(err_list):
        print('Circuit', i, 'failed:', e)

    print(len(err_list), 'circuits failed')
    print(len(passed_list) - len(err_list), 'circuits passed')

    # # log good and bad circuits
    # with open('good_circuits.txt', 'w') as f:
    #     for circuit, result in good_circuit_list:
    #         f.write(circuit + '\n----Result----\n' + str(result) + '\n-----------------\n\n')

    # with open('bad_circuits.txt', 'w') as f:
    #     for circuit, result in bad_circuit_list:
    #         f.write(circuit + '\n----Result----\n' + str(result) + '\n-----------------\n\n')

    #     for e in err_list:
    #         f.write(str(e) + '\n')

    raise ValueError('Some circuits failed!')


@qpandalite_test('Test QASMBench')
def run_test_qasm():
    test_qasm()

if __name__ == '__main__':
    test_qasm()