import json
import os
from pathlib import Path
from qpandalite.task.quafu import query_by_taskid, load_all_online_info, write_taskinfo
import matplotlib.pyplot as plt
import numpy as np
from qiskit_twirl import flip_result
import re


def get_no_twirl_circuit(platform, taskname):
    no_twirl_exp = re.compile(platform + r' no twirl-(\d+)$')
    matches = no_twirl_exp.match(taskname)
    return matches.group(1)


def get_twirl_circuit(platform, taskname):
    twirl_exp = re.compile(platform + r' circuit-(\d+), twirl-(\d+)')
    matches = twirl_exp.match(taskname)
    return matches.group(1), matches.group(2)


def query_by_ibm_taskid(taskid):
    from qiskit_ibm_provider import IBMProvider
    provider = IBMProvider(instance='ibm-q/open/main')
    job = provider.retrieve_job(taskid)
    status = job.status()
    result = dict(job.result().get_counts())
    taskinfo = {'result': result}
    return taskinfo


def query_all_task(platform='quafu', savepath = None):
    for task in online_info:
        if platform == 'quafu':
            taskname = task['taskname']
        else:
            taskname = task['name']
        taskid = task['taskid']
        if not os.path.exists(savepath / '{}.txt'.format(taskname)):
            if platform == 'quafu':
                ret = query_by_taskid(taskid)
            else:
                ret = query_by_ibm_taskid(taskid)
            if ret is None:
                continue
            elif ret == 'Failed':
                write_taskinfo(taskname, taskinfo={}, savepath=savepath)
            else:
                write_taskinfo(taskname, taskinfo=ret, savepath=savepath)


def calculate_twirled_result(twirled_result_of_one_circuit, calculate_function):
    r = 0
    for key, value in twirled_result_of_one_circuit.items():
        r += calculate_function(value)
    return r / len(twirled_result_of_one_circuit)


def calculate_final_probability(result, reverse=False):
    z = 0
    for key, value in result.items():
        if reverse:
            key = key[::-1]
        if key[-1] == '1':
            z += value
    shots = sum(list(result.values()))
    return z/shots


if __name__ == '__main__':
    platform = 'quafu'
    path = platform + '_online_info_verify'
    savepath = Path.cwd() / path

    online_info = load_all_online_info(savepath=savepath)
    query_all_task(platform=platform, savepath=savepath)

    with open(savepath / 'flip result.txt') as f:
        flip_information = json.load(f)

    without_twirl_result = {}
    twirl_result = {}
    theory_without_twirl_result = {}
    theory_twirl_result = {}
    for task in online_info:
        taskname = task['taskname']
        with open(savepath / f'{taskname}.txt') as fp:
            taskinfo = json.load(fp)

        result_dict = taskinfo["res"]
        result_dict = json.loads(result_dict)
        theory_dict = task['theory']
        theory_dict = dict(zip([np.binary_repr(i, 4) for i in range(16)][::-1], theory_dict))

        if 'no' in taskname:
            circuit_index = get_no_twirl_circuit(platform, taskname)
            without_twirl_result[circuit_index] = result_dict
            theory_without_twirl_result[circuit_index] = theory_dict
        else:
            circuit_index, twirl_index = get_twirl_circuit(platform, taskname)
            flip = flip_information[f'circuit {circuit_index}'][f'twirl {twirl_index}']
            result_dict = flip_result(result_dict, flip, True)
            theory_dict = flip_result(theory_dict, flip, True)
            if circuit_index not in twirl_result:
                twirl_result[circuit_index] = {}
                theory_twirl_result[circuit_index] = {}
            twirl_result[circuit_index][twirl_index] = result_dict
            theory_twirl_result[circuit_index][twirl_index] = theory_dict

    z_prob = []
    z_prob_theory = []
    for key, value in without_twirl_result.items():
        z_prob.append(calculate_final_probability(value, reverse=False))
    for key, value in theory_without_twirl_result.items():
        z_prob_theory.append(calculate_final_probability(value, reverse=False))

    z_prob_twirled = []
    for key, one_circuit in twirl_result.items():
        z_prob_twirled.append(calculate_twirled_result(one_circuit, lambda x: calculate_final_probability(x, True)))
    z_prob_twirled_theory = []
    for key, one_circuit in theory_twirl_result.items():
        z_prob_twirled_theory.append(calculate_twirled_result(one_circuit, lambda x: calculate_final_probability(x, False)))

    plt.scatter(z_prob_theory, z_prob)
    plt.show(block=True)
