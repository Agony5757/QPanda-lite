import json
import os
from pathlib import Path
from qpandalite.task.quafu import *
import matplotlib.pyplot as plt
import numpy as np


def calculate_final_probability(result, reverse=False):
    z = 0
    for key, value in result.items():
        if reverse:
            key = key[::-1]
        if key[-1] == '1':
            z += value
    return z/1000


def get_correct_answer(result, reverse=False):
    z = 0
    for key, value in result.items():
        if reverse:
            key = key[::-1]
        if key == '0'*(len(key)-1) + '1':
            z += value
    return z/1000


def calculate_pass(result):
    total_z = 0
    for key, value in result.items():
        if key.count('1') == 1:
            total_z += value
    return total_z/1000


if __name__ == '__main__':

    savepath = Path.cwd() / 'quafu_online_info_verify'
    # savepath = Path.cwd() / 'history' / ''

    online_info = load_all_online_info(savepath = savepath)
    query_all_task(savepath = savepath)

    not_finished = []

    for task in online_info:
        taskid = task['taskid']
        taskname = '' if 'taskname' not in task else task['taskname']
        if not os.path.exists(savepath / f'{taskid}.txt'):
            not_finished.append({'taskid':taskid, 'taskname':taskname})

    if not_finished:
        print('Unfinished task list')
        for task in not_finished:
            taskid = task['taskid']
            taskname = task['taskname'] if task['taskname'] else 'null'
            print(f'  taskid:{taskid}, taskname:{taskname}')
        print(f'Unfinished: {len(not_finished)}')
    else:
        z_prob = []
        total_z_prob = []
        correct_prob = []

        z_prob_theory = []
        total_z_prob_theory = []
        correct_prob_theory = []

        with open(savepath / 'theory result.json', 'r') as f:
            theory_result = json.load(f)

        for i, task in enumerate(online_info):
            taskid = task['taskid']
            print(f'Taskid: {taskid}')
            with open(savepath / f'{taskid}.txt') as fp:            
                taskinfo = json.load(fp)

            if taskinfo['status'] in [3, 4]:
                continue
            
            result_dict = taskinfo["res"]
            result_dict = json.loads(result_dict)
            theory_result_dict = theory_result[taskid]

            print(f'Task Result: {result_dict}')

            z_prob.append(calculate_final_probability(result_dict))
            total_z_prob.append(calculate_pass(result_dict))
            correct_prob.append(get_correct_answer(result_dict))

            z_prob_theory.append(calculate_final_probability(theory_result_dict, reverse=True))
            total_z_prob_theory.append(calculate_pass(theory_result_dict))
            correct_prob_theory.append(get_correct_answer(theory_result_dict, reverse=True))

        plt.scatter(correct_prob_theory, correct_prob, label='correct result')
        plt.scatter(z_prob_theory, z_prob, label='final z prob')
        plt.title('test for multiple RX gate')
        # plt.scatter(total_z_prob_theory, total_z_prob, label='total z prob')
        plt.legend()
        plt.show()
            