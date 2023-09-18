import warnings
import os
from qiskit import QuantumCircuit, transpile, execute
from qiskit_aer import AerSimulator
from qiskit_ibm_provider import IBMProvider
import quafu
from pathlib import Path
import json
from qpandalite.task.quafu import *



def login(platform):
    if platform == 'ibm':
        try:
            provider = IBMProvider(instance='ibm-q/open/main')
        except:
            warnings.warn('ibm log in failed. check account or connection.')
        return provider

    if platform == 'quafu':
        try:
            with open('quafu_online_config.json', 'r') as fp:
                default_online_config = json.load(fp)
            default_token = default_online_config['default_token']
        except:
            default_token = ''
            warnings.warn('quafu_online_config.json is not found. '
                          'It should be always placed at current working directory (cwd).')
        global user
        user = quafu.User()
        user.save_apitoken(default_token)
        return user


def submit_single_circuit_ibm(circuit,
                              task_name=None,
                              backend_name=None,
                              shots=1000,
                              mapping_map=None,
                              savepath=Path.cwd() / 'ibm online info',
                              provider=None
                              ):
    qc = QuantumCircuit.from_qasm_str(circuit)
    backend = provider.get_backend(backend_name)
    if mapping_map is None:
        mapping_map = backend.coupling_map
    qc = transpile(qc, coupling_map=mapping_map, backend=backend, optimization_level=3)
    job = backend.run(qc, shots=shots)
    job_id = job.job_id()
    if task_name is None:
        task_name = 'default_ibm_task'
    if savepath:
        task_info = dict()
        task_info['taskid'] = job_id
        task_info['backend'] = backend_name
        task_info['name'] = task_name

        if not os.path.exists(savepath):
            os.makedirs(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(task_info) + '\n')
    return job_id, task_name


def submit_single_circuit_quafu(circuit,
                              task_name=None,
                              chip_id=None,
                              shots=1000,
                              auto_mapping=True,
                              savepath=Path.cwd() / 'quafu online info',
                                user=None):
    if chip_id not in ['ScQ-P10', 'ScQ-P18', 'ScQ-P136']:
        raise RuntimeError(r"Invalid chip_id. "
                           r"Current quafu chip_id list: ['ScQ-P10','ScQ-P18','ScQ-P136']")

    task = quafu.Task()
    task.config(backend=chip_id, shots=shots, compile=auto_mapping)
    qc_qiskit = QuantumCircuit.from_qasm_str(circuit)
    qc = quafu.QuantumCircuit(qc_qiskit.num_qubits)
    qc.from_openqasm(circuit)
    theory_result = quafu.simulate(qc, output='probabilities').probabilities.tolist()
    print(theory_result)

    result = task.send(qc, wait=False, name=task_name)
    taskid = result.taskid
    if savepath:
        task_info = dict()
        task_info['taskid'] = taskid
        task_info['taskname'] = task_name
        task_info['backend'] = chip_id
        task_info['theory'] = theory_result
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(task_info) + '\n')

    return taskid, task_name


def submit_all_circuits(circuits, platform, backend_name=None, shots=1000, name_start='verify-'):
    login(platform)
    savepath = Path.cwd() / platform + ' online info'
    name_start = name_start + platform + '-'
    for index, circuit in enumerate(circuits):
        if platform == 'ibm':
            if backend_name is None:
                backend_name = 'ibm_lagos'
            taskid = submit_single_circuit_ibm(circuit,
                                               task_name=name_start+str(index),
                                               backend_name=backend_name,
                                               shots=shots,
                                               savepath=savepath),
        if platform == 'quafu':
            if backend_name is None:
                backend_name = 'ScQ-P136'
            taskid = submit_single_circuit_quafu(circuit,
                                                 task_name=name_start+str(index),
                                                 shots=shots,
                                                 chip_id=backend_name,
                                                 auto_mapping=True,
                                                 savepath=savepath
                                                 )
        return taskid
