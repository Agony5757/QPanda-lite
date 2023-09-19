import numpy as np
import pyqpanda as pq
import os


def add_layer_opt(q_0, q_1, theta_0, theta_1):
    circuit = pq.QCircuit()
    circuit << pq.RY(q_1, -theta_0/2)
    circuit << pq.CZ(q_0, q_1)
    circuit << pq.X(q_0)
    circuit << pq.RY(q_1, theta_0/2 - theta_1/2)
    circuit << pq.CZ(q_0, q_1)
    circuit << pq.RY(q_1, theta_1/2)
    circuit << pq.X(q_0)
    return circuit


def generate_circuit(qubit_number, theta):
    machine = pq.CPUQVM()
    machine.init_qvm()
    qv = machine.qAlloc_many(qubit_number)
    # qv = [45,46,52,53,54,60,59][:qubit_number]
    cb = machine.cAlloc_many(qubit_number)
    circuit = pq.QCircuit()

    for qubit_layer in range(qubit_number):
        if qubit_layer == 0:
            circuit << pq.RY(qv[0], theta[0])
            # circuit += f'RY q[{qv[0]}], ({theta[0]})\n'
        else:
            circuit << add_layer_opt(qv[qubit_layer-1], qv[qubit_layer], theta[2 * qubit_layer - 1], theta[2 * qubit_layer]) # add_layer/add_layer_opt

    prog = pq.create_empty_qprog()
    prog << circuit

    prog << pq.measure_all(qv, cb)
    result = machine.run_with_configuration(prog, cb, 1000)
    vir_z_ir = pq.convert_qprog_to_originir(prog, machine)
    machine.finalize()

    return vir_z_ir, result




if __name__ == '__main__':
    qubit_number = 5
    theta = np.random.random(2*qubit_number-1) * np.pi * 2
    ir, result = generate_circuit(qubit_number, theta)
    print(ir)
    print(result)
