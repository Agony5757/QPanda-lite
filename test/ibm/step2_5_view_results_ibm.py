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
    return z / 4000


def get_correct_answer(result, reverse=False):
    z = 0
    for key, value in result.items():
        if reverse:
            key = key[::-1]
        if key == '0' * (len(key) - 1) + '1':
            z += value
    return z / 4000


def calculate_pass(result):
    total_z = 0
    for key, value in result.items():
        if key.count('1') == 1:
            total_z += value
    return total_z / 4000


if __name__ == '__main__':

    savepath = Path.cwd() / 'ibm_online_info_verify'
    not_finished = []

    z_prob = []
    total_z_prob = []
    correct_prob = []

    z_prob_theory = []
    total_z_prob_theory = []
    correct_prob_theory = []

    query_all_task()

    with open(Path.cwd() / 'simulation result.json', 'r') as f:
        theory_result = json.load(f)
    # with open(savepath / 'ibm_result.json', 'r') as f:
    #     ibm_result = json.load(f)

    for taskid, task_result in theory_result.items():
        print(f'Taskid: {taskid}')

        theory_result_dict = theory_result[taskid]
        with open(savepath / f'{taskid}.txt', 'r') as f:
            ibm_result = json.load(f)
        result_dict = ibm_result['result']

        print(f'Task Result: {theory_result_dict}')
        print(f'Task ibm Result: {result_dict}')

        z_prob.append(calculate_final_probability(result_dict,  reverse=True))
        total_z_prob.append(calculate_pass(result_dict))
        correct_prob.append(get_correct_answer(result_dict, reverse=True))

        z_prob_theory.append(calculate_final_probability(theory_result_dict, reverse=True))
        total_z_prob_theory.append(calculate_pass(theory_result_dict))
        correct_prob_theory.append(get_correct_answer(theory_result_dict, reverse=True))

    plt.scatter(correct_prob_theory, correct_prob, label='correct result')
    plt.scatter(z_prob_theory, z_prob, label='final z prob')
    plt.title('test in IBM result')
    # plt.scatter(total_z_prob_theory, total_z_prob, label='total z prob')
    plt.legend()
    plt.show()
