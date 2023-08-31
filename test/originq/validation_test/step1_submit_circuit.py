import numpy as np
import qpandalite.task.originq as originq
from pathlib import Path

available_qubits = [45,46,52,53,54,48]

# simple circuits
def ghz(qubit_number, init=0):
    qv = available_qubits[:qubit_number]
    circuit = 'QINIT 72\n'
    circuit += f'CREG {qubit_number}\n'

    circuit += f'H q[{qv[init]}] \n'
    for i in range(init):
        circuit += f'CNOT q[{qv[init-i]}], q[{qv[init-i-1]}]\n'
    for i in range(qubit_number-1-init):
        circuit += f'CNOT q[{qv[init+i]}], q[{qv[init+i+1]}]\n'

    for i in range(qubit_number):
        circuit += f'MEASURE q[{qv[i]}], c[{i}]\n'
    return circuit

def W(qubit_number, positive_order=True):
    if positive_order:
        qv = available_qubits[:qubit_number]
    else:
        qv = available_qubits[:qubit_number][::-1]

    circuit = 'QINIT 72\n'
    circuit += f'CREG {qubit_number}\n'
    circuit += f'RY q[{qv[0]}],({-2 * np.arccos(np.sqrt(1/qubit_number))})\n'
    for i in range(qubit_number-2):
        circuit += f'CONTROL q[{qv[i]}]\n'
        circuit += f'RY q[{qv[i+1]}],({-2 * np.arccos(np.sqrt(1/(qubit_number-i-1)))})\n'
        circuit += 'ENDCONTROL\n'

    for i in range(qubit_number-1):
        circuit += f'CNOT q[{qv[qubit_number-i-2]}],q[{qv[qubit_number-i-1]}]\n'
    circuit += f'X q[{qv[0]}]\n'

    for i in range(qubit_number):
        circuit += f'MEASURE q[{qv[i]}], c[{i}]\n'
    return circuit

if __name__ == '__main__':
    test_circuits = []
    qubit_number = 5

    for i in range(qubit_number):
        test_circuits.append(ghz(qubit_number, i))

    test_circuits.append(W(qubit_number, True))
    test_circuits.append(W(qubit_number, False))

    taskid = originq.submit_task_group(test_circuits, 
                                       task_name='Validation', 
                                       shots=1000, 
                                       measurement_amend=False)
    print(f'Taskid = {taskid}')
    