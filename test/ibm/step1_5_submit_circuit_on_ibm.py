import os.path

import pyqpanda as pq
import numpy as np
from qiskit import IBMQ, QuantumCircuit, execute, transpile
from qiskit_ibm_provider import IBMProvider
import json
from pathlib import Path


# IBMQ.enable_account('c3d3da0c74dc1a77d194557c2a0fa969b5f1b2fc000b2f75f7181dc05e3816aa5a85ad05f48ba1606a9ca8a17f61e7c2d8c5b8182910be719f29252e66b1045c')
# IBMProvider.save_account('c3d3da0c74dc1a77d194557c2a0fa969b5f1b2fc000b2f75f7181dc05e3816aa5a85ad05f48ba1606a9ca8a17f61e7c2d8c5b8182910be719f29252e66b1045c')
# provider = IBMProvider()
provider = IBMProvider(instance='ibm-q/open/main')

def CNOT(q1, q2):
    cir = pq.QCircuit()
    cir << pq.H(q2) << pq.CZ(q1, q2) << pq.H(q2)
    return cir


def xxyy(q1, q2, J, dt):
    '''
    generate exp(-i*angle*(s_x s_x+s_y s_y))
    :param q1: the first qubit
    :param q2: the second qubit
    :param angle: angle
    :return: iSWAP(q1, q2, angle)
    '''
    xycir = pq.QCircuit()
    angle = J * dt / 2
    xycir << pq.RX(q1, np.pi / 2) << pq.RX(q2, np.pi / 2) << pq.CNOT(q1, q2) << pq.RX(q1, angle) << pq.RZ(q2, angle) \
        << pq.CNOT(q1, q2) << pq.RX(q1, -np.pi / 2) << pq.RX(q2, -np.pi / 2)
    return xycir


def xy_layer(qlist, J, dt, parallel_patterns):
    cir = pq.QCircuit()
    num = len(qlist)
    for pattern in parallel_patterns:
        for cz in pattern:
            if cz[0] >= num or cz[1] >= num:
                continue
            cir << xxyy(qlist[cz[0]], qlist[cz[1]], J[cz[0]], dt)
        # cir << pq.BARRIER(qlist)
    return cir


def ising_simulation_time(num, J, n, t, theta=np.pi/2, noise=0, save='', parallel_pattern=None):
    """

    :param num: qubit number
    :param J: coupling strength
    :param n: trotter steps
    :param t: evolution time
    :param theta: initial state RX(theta)|0>, default by pi/2, |10...0>
    :param noise: 0 means use CPUQVM, other float use depolarizing noise simulator
    :param save: if '', then only simulate. if give a string, then make a dictionary and save the origin ir files.
    :return:
    result: measurement result
    """
    if parallel_pattern is None:
        parallel_pattern = [[[0, 1], [2, 3]], [[1, 2], [4, 5]],
                            [[3, 4]], [[5, 6]]]
    if noise == 0:
        qvm = pq.CPUQVM()
        qvm.init_qvm()
    else:
        qvm = pq.NoiseQVM()
        qvm.init_qvm()
        qvm.set_noise_model(pq.NoiseModel.DEPOLARIZING_KRAUS_OPERATOR, pq.GateType.CNOT_GATE, noise)

    q = qvm.qAlloc_many(num)
    c = qvm.cAlloc_many(num)
    prog = pq.QProg()
    prog << pq.RX(q[0], theta)
    for i in range(n):
        prog << xy_layer(q, J, t/n, parallel_patterns=parallel_pattern)
    bit_flip = np.random.random(n) < 0.5
    for i in range(n):
        if bit_flip[i]:
            prog << pq.X(q[i])
    prog << pq.measure_all(q, c)
    ir = pq.convert_qprog_to_qasm(prog, qvm)
    result = qvm.run_with_configuration(prog, c, 4000)
    return ir, result


def submit_single_circuit(qasm):
    qc = QuantumCircuit.from_qasm_str(qasm)
    backend = provider.get_backend('ibm_nairobi')
    qc = transpile(qc, coupling_map=[[0, 1], [1, 0], [1, 2], [1, 3], [2, 1], [3, 1], [3, 5], [4, 5], [5, 3], [5, 4],
                                     [5, 6], [6, 5]], backend=backend, optimization_level=3)
    job = backend.run(qc)
    jobid = job.job_id()
    result = job.result()
    result = dict(result.get_counts())
    return result, jobid


def generate_xy_circuit_different_time(qubit_number, layer, evolve_time_list):
    initial_theta = np.pi
    J = np.array([np.sqrt(i * (qubit_number - i)) for i in range(1, qubit_number)])
    circuits = []
    result_list = []
    for time in evolve_time_list:
        qasm, result = ising_simulation_time(qubit_number, J, layer, time, initial_theta)
        circuits.append(qasm)
        result_list.append(result)
    return circuits, result_list


def submit_task(circuit,
                task_name=None,
                backend_name=None,
                shots=1000,
                mapping_map=None,
                savepath = Path.cwd() / 'ibm_online_info'):
    if mapping_map is None:
        mapping_map = [[0, 1], [1, 0], [1, 2], [1, 3], [2, 1], [3, 1], [3, 5], [4, 5], [5, 3], [5, 4],
                       [5, 6], [6, 5]]
    qc = QuantumCircuit.from_qasm_str(circuit)
    backend = provider.get_backend(backend_name)
    qc = transpile(qc, coupling_map=mapping_map, backend=backend, optimization_level=3)
    job = backend.run(qc, shots=shots)
    job_id = job.job_id()
    # job_backend = job.backend
    if task_name is None:
        task_name = 'default_ibm_task'
    if savepath:
        task_info = dict()
        task_info['taskid'] = job_id
        task_info['backend'] = backend_name
        task_info['name'] = task_name

        if not os.path.exists(savepath):
            os.makedirs(savepath)
        with open(savepath / 'ibm online_info.txt', 'a') as fp:
            fp.write(json.dumps(task_info) + '\n')
    return job_id



if __name__ == '__main__':

    theta_list = np.random.random(200) * np.pi * 2
    circuits, results = generate_xy_circuit_different_time(4, 2, theta_list)
    result_dict = {}
    savepath = Path.cwd() / 'ibm_online_info_verify'
    for i, circuit in enumerate(circuits):
        taskid = submit_task(circuit,
                             task_name=f'Verify-{i}',
                             backend_name='ibm_lagos',
                             shots=4000,
                             savepath=savepath
                             )
        result_dict[taskid] = results[i]

    with open(savepath / 'simulation result.json', 'w') as f:
        json.dump(result_dict, f)
