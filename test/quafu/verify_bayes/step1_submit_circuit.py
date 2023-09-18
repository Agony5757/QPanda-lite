# VERIFY THE BIT SEQUENCE !!!

from pathlib import Path

import numpy as np

from qpandalite.task.quafu import *
from step0_model import generate_circuit


def generate_bayes_circuit_different_theta(qubit_number, theta_list):
    circuits = []
    result_list = []
    for i, initial_theta in enumerate(theta_list):
        ir, result = generate_circuit(qubit_number, initial_theta)
        circuits.append(ir)
        result_list.append(result)
    return circuits, result_list


if __name__ == '__main__':
    # circuits = [circuit_1, circuit_2, circuit_3, circuit_4]
    angle_list = np.random.random(size=(100, 7)) * np.pi * 2
    angle_list[:, 0] = np.pi/2
    angle_list[:, 2:] = np.random.random(5) * np.pi * 2
    print(angle_list[:10])
    circuits, results = generate_bayes_circuit_different_theta(4, angle_list)
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

