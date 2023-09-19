# VERIFY THE BIT SEQUENCE !!!

from pathlib import Path

import numpy as np

from qpandalite.task.quafu import *
from step0_model import ising_simulation_time, simple_rx_model


def generate_xy_circuit_different_start(qubit_number, layer, initial_angle):
    t = np.pi
    J = np.array([np.sqrt(i * (qubit_number - i)) for i in range(1, qubit_number)])
    circuits = []
    result_list = []
    for initial_theta in initial_angle:
        ir, result = ising_simulation_time(qubit_number, J, layer, t, initial_theta)
        circuits.append(ir)
        result_list.append(result)
    return circuits, result_list


def generate_xy_circuit_different_time(qubit_number, layer, evolve_time_list):
    initial_theta = np.pi
    J = np.array([np.sqrt(i * (qubit_number - i)) for i in range(1, qubit_number)])
    circuits = []
    result_list = []
    for time in evolve_time_list:
        ir, result = ising_simulation_time(qubit_number, J, layer, time, initial_theta)
        circuits.append(ir)
        result_list.append(result)
    return circuits, result_list


def generate_simple_rotation_gate(n, theta_list):
    circuits = []
    result_list = []
    for theta in theta_list:
        ir, result = simple_rx_model(n, theta)
        circuits.append(ir)
        result_list.append(result)
    return circuits, result_list


if __name__ == '__main__':
    # circuits = [circuit_1, circuit_2, circuit_3, circuit_4]
    angle_list = np.random.random(100) * np.pi * 2
    # circuits, results = generate_simple_rotation_gate(4, angle_list)
    circuits, results = generate_xy_circuit_different_start(3, 2, angle_list)
    result_dict = {}
    savepath = Path.cwd() / 'quafu_online_info_verify'
    for i, circuit in enumerate(circuits):
        taskid = submit_task(circuit, 
                             task_name=f'Verify-{i}',
                             chip_id='ScQ-P136',
                             shots=1000,
                             savepath=Path.cwd() / 'quafu_online_info_verify')
        result_dict[taskid] = results[i]
        print(taskid)

    savepath = Path.cwd() / 'quafu_online_info_verify'
    with open(savepath / 'theory result.json', 'w') as f:
        json.dump(result_dict, f)

