import numpy as np
from qpandalite.qasm import OpenQASM2_BaseParser, OpenQASM2_LineParser
from pathlib import Path
import pickle
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.test._utils import qpandalite_test
from qpandalite.qasm import NotSupportedGateError
from qpandalite.qasm.random_qasm import random_qasm
from qpandalite.qasm.qasm_spec import available_qasm_gates

import qiskit
import qiskit.qasm2 as qasm
from qiskit_aer import AerSimulator
from qiskit import transpile

def simulate_by_qiskit(qasm_str):
    
    print(qasm_str)
    qc = qiskit.QuantumCircuit.from_qasm_str(qasm_str)

    backend = AerSimulator()
    
    # get probabilites of all states from AerSimulator
    result = backend.run(qc).result()
    counts = result.get_counts()
    # print(counts)
    return counts

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

    qasm_simulator = QASM_Simulator(backend_type)
    my_result = qasm_simulator.simulate(transpiled_circuit)

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

def test_random_qasm(circuit, backend_type):
    # simulate via qiskit
    qiskit_result = simulate_by_qiskit(circuit)

    # check result
    try:
        _check_result(circuit, qiskit_result, backend_type)
        return None
    except NotMatchError as e:
        return e
    except Exception as e:
        # other unexpected error
        raise e

def test_random_qasm_batch(
    random_batchsize = 100, 
    n_qubit = 5,
    n_gates = 20,
    instruction_set = available_qasm_gates, 
    backend_type = 'statevector'):

    err_list = []    
    good_circuit_list = []
    bad_circuit_list = []

    for i in range(random_batchsize):

        qasm_code = random_qasm(n_qubits=n_qubit,
                                n_gates=n_gates,
                                instruction_set=instruction_set)
        err = test_random_qasm(qasm_code, backend_type)
        if err:
            err_list.append(err)
            bad_circuit_list.append((qasm_code, err))
        else:
            good_circuit_list.append((qasm_code, None))


    print(len(err_list), 'circuits failed')
    print(random_batchsize - len(err_list), 'circuits passed')

    # log good and bad circuits
    with open('good_circuits.txt', 'w') as f:
        for circuit, result in good_circuit_list:
            f.write(circuit + '\n----Result----\n' + str(result) + '\n-----------------\n\n')

    with open('bad_circuits.txt', 'w') as f:
        for circuit, result in bad_circuit_list:
            f.write(circuit + '\n----Result----\n' + str(result) + '\n-----------------\n\n')

        for e in err_list:
            f.write(str(e) + '\n')

    raise ValueError('Some circuits failed!')


@qpandalite_test('Test Random QASM')
def random_test_random():
    test_random_qasm_batch(random_batchsize=100, 
                           n_qubit=5, n_gates=20, 
                           instruction_set=available_qasm_gates,
                           backend_type='statevector')
    
    test_random_qasm_batch(random_batchsize=100, 
                           n_qubit=5, n_gates=20, 
                           instruction_set=available_qasm_gates,
                           backend_type='density_operator')


if __name__ == '__main__':
    random_test_random()