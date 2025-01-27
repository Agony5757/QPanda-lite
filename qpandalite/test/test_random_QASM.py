import numpy as np
from qpandalite.qasm import OpenQASM2_BaseParser, OpenQASM2_LineParser
from pathlib import Path
import pickle
from qpandalite.simulator.qasm_simulator import QASM_Simulator
from qpandalite.test._utils import qpandalite_test
from qpandalite.qasm import NotSupportedGateError
from qpandalite.qasm.random_qasm import random_qasm
from qpandalite.qasm.qasm_spec import available_qasm_gates, generate_sub_gateset

import qiskit
import qiskit.qasm2 as qasm
from qiskit_aer import AerSimulator
from qiskit import transpile
from qiskit_aer import Aer

def simulate_by_qiskit(qasm_str):
    qc = qasm.loads(qasm_str)
    for op in qc.data[:]:
        if op.operation.name == 'measure':
            qc.data.remove(op)

    backend = Aer.get_backend("statevector_simulator")
    # qc = transpile(qc, backend)
    # get probabilites of all states from AerSimulator
    result = backend.run(qc).result()
    statevector = result.get_statevector(qc).data

    problist = np.abs(statevector)**2
    return problist

class NotMatchError(Exception):
    pass

def _check_result(transpiled_circuit, reference_array, backend_type):

    qasm_simulator = QASM_Simulator(backend_type)
    my_result = qasm_simulator.simulate_pmeasure(transpiled_circuit)

    if len(reference_array) != len(my_result):
        print('---------------')
        print(transpiled_circuit)
        print(reference_array)
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
            f'Reference Result: {reference_array}\n'
            '---------------\n'
            f'The exception is: {str(e)}\n'
        )
        e.args = (error_message,) + e.args
        raise e
        
    if not np.allclose(reference_array, my_result):            
        raise NotMatchError(
            '---------------\n'
            f'{transpiled_circuit}\n'
            f'{reference_array}\n'
            '---------------\n'
            'Result not match!\n'
            f'Reference = {reference_array}\n'
            f'My Result = {my_result}\n'
        )


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
            print('Test failed!')
            err_list.append(err)
            bad_circuit_list.append((qasm_code, err))
        else:
            print('Test passed!')
            good_circuit_list.append((qasm_code, None))


    print(len(err_list), 'circuits failed')
    print(random_batchsize - len(err_list), 'circuits passed')

    # log good and bad circuits
    with open('good_circuits.txt', 'w') as f:
        for circuit, result in good_circuit_list:
            f.write(circuit + '\n----Result----\n' + str(result) + '\n-----------------\n\n')

    with open('bad_circuits.txt', 'w') as f:
        # for circuit, result in bad_circuit_list:
        #     f.write(circuit + '\n----Result----\n' + str(result) + '\n-----------------\n\n')

        for e in err_list:
            f.write(str(e) + '\n')

    if len(err_list) > 0:
        raise ValueError('Some circuits failed!')


@qpandalite_test('Test Random QASM Statevector')
def test_random_qasm_statevector():

    gate_set = ['h', 'cx', 'rx', 'ry', 'rz', 
                'u1', 'u2', 'u3', 'id', 'x', 'y', 'z', 
                's', 'sdg', 't', 'tdg', 
                'ccx', 'cu1', ]
    gate_set = generate_sub_gateset(gate_set)

    test_random_qasm_batch(random_batchsize=100, 
                           n_qubit=5, n_gates=50, 
                           instruction_set=gate_set,
                           backend_type='statevector')


@qpandalite_test('Test Random QASM Density Operator')
def test_random_qasm_density_operator():
    
    gate_set = ['h', 'cx', 'rx', 'ry', 'rz', 
                'u1', 'u2', 'u3', 'id', 'x', 'y', 'z', 
                's', 'sdg', 't', 'tdg',  
                'ccx', 'cu1', ]

    # gate_set = ['h', 'cx', 'rx', 'ry', 'rz', 
    #             'u1', 'u2', 'u3', 'id', 'x', 'y', 'z', 
    #             's', 'sdg', 't', 'tdg', 
    #             'ccx', 'cu1', ]
    gate_set = generate_sub_gateset(gate_set)

    test_random_qasm_batch(random_batchsize=100, 
                           n_qubit=5, n_gates=50, 
                           instruction_set=gate_set,
                           backend_type='density_operator')


if __name__ == '__main__':
    test_random_qasm_statevector()
    test_random_qasm_density_operator()