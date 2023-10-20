import qiskit
from qpandalite.task.task_utils import *

import time
from typing import List, Union

from pathlib import Path
import os
import json
import warnings
import qiskit_ibm_provider

saved_account = qiskit_ibm_provider.IBMProvider.saved_accounts()
if saved_account is {}:
    try:
        with open('ibm_online_config.json', 'r') as fp:
            default_online_config = json.load(fp)
            default_token = default_online_config['default_token']
    except Exception as e:
        raise RuntimeError('ibm_online_config.json is not found. '
                           'It should be placed at current working directory (cwd) at the first time.')
    try:

        qiskit_ibm_provider.IBMProvider.save_account(default_token)
    except Exception as e:
        raise RuntimeError(f'failed to login, error information: {e}')

try:
    provider = qiskit_ibm_provider.IBMProvider(instance='ibm-q/open/main')
except Exception as e:
    raise RuntimeError(f'failed to login, error information: {e}')

backends = provider.backends()


def query_by_taskid_single(taskid: str, ):
    '''Query circuit status by taskid (Async). This function will return without waiting.

    Args:
        taskid (str): The taskid.

    Raises:
        ValueError: Taskid invalid.
        ValueError: URL invalid.
        RuntimeError: Error when querying.

    Returns:
        Dict[str, dict]: The status and the result
            status : success | failed | running
            result (when success): List[Dict[str,list]]
            result (when failed): {'errcode': str, 'errinfo': str}
            result (when running): N/A
    '''
    if not taskid: raise ValueError('Task id ??')

    # construct request_body for task query
    job = provider.retrieve_job(job_id=taskid)
    status = job.status().name
    if status != 'DONE':
        ret = {'status': status, 'value': job.status().value}
        warnings.warn(f'Error in query_by_taskid. '
                      'The job has not successfully run.'
                      f' Response: {job.status().value}')
        return ret

    ret = {}
    taskinfo = job.result().to_dict()
    ret['status'] = 'DONE'
    ret['time'] = taskinfo['date'].strftime('%a %d %b %Y, %I:%M%p')
    ret['backend_name'] = taskinfo['backend_name']
    ret['backend_version'] = taskinfo['backend_version']
    results = []

    for single_result in taskinfo['results']:
        results.append(single_result['data']['counts'])
    ret['result'] = results

    return ret


def query_by_taskid(taskid: Union[List[str], str]):
    if not taskid: raise ValueError('Task id ??')
    if isinstance(taskid, list):
        taskinfo = dict()
        taskinfo['status'] = 'success'
        taskinfo['result'] = []
        for taskid_i in taskid:
            taskinfo_i = query_by_taskid_single(taskid_i)
            if taskinfo_i['status'] in ['ERROR', 'CANCELLED']:
                # if any task is failed, then this group is failed.
                taskinfo['status'] = 'failed'
                break
            elif taskinfo_i['status'] in ['INITIALIZING', 'QUEUED', 'VALIDATING', 'RUNNING']:
                # if any task is running, then set to running
                taskinfo['status'] = 'running'
            if taskinfo_i['status'] == 'DONE':
                if taskinfo['status'] == 'success':
                    # update if task is successfully finished (so far)
                    taskinfo['result'].extend(taskinfo_i['result'])

    elif isinstance(taskid, str):
        taskinfo = query_by_taskid_single(taskid)
    else:
        raise ValueError('Invalid Taskid')

    return taskinfo


def query_by_taskid_sync(taskid,
                         interval=2.0,
                         timeout=60.0,
                         retry=5, ):
    starttime = time.time()
    while True:
        try:
            now = time.time()
            if now - starttime > timeout:
                raise TimeoutError(f'Reach the maximum timeout.')

            time.sleep(interval)

            taskinfo = query_by_taskid(taskid)
            if taskinfo['status'] == 'running':
                continue
            if taskinfo['status'] == 'success':
                result = taskinfo['result']
                return result
            if taskinfo['status'] == 'failed':
                errorinfo = taskinfo['result']
                raise RuntimeError(f'Failed to execute, errorinfo = {errorinfo}')
        except RuntimeError as e:
            if retry > 0:
                retry -= 1
                print(f'Query failed. Retry remains {retry} times.')
            else:
                print(f'Retry count exhausted.')
                raise e


def _submit_task_group(circuits=None,
                       task_name=None,
                       tasktype=None,
                       chip_id=None,
                       shots=1000,
                       circuit_optimize=True,
                       measurement_amend=False,
                       auto_mapping=False,
                       compile_only=False,
                       specified_block=None,
                       savepath=Path.cwd() / 'online_info'):
    backends_name = [i.name for i in backends]
    if chip_id not in backends_name:
        raise ValueError(f'no such chip, should be one of {backends_name}')
    backend = provider.get_backend(chip_id)
    max_group_size = backend.max_circuits
    max_shots = backend.max_shots
    if shots > max_shots:
        raise ValueError(f'maximum shots number exceeded, should less than {max_shots}')

    if len(circuits) > max_group_size:
        groups = []
        group = []
        for circuit in circuits:
            if len(group) >= max_group_size:
                groups.append(group)
                group = []
            group.append(circuit)
        if group:
            groups.append(group)

        return [_submit_task_group(group,
                                   '{}_{}'.format(task_name, i),
                                   tasktype,
                                   chip_id,
                                   shots,
                                   circuit_optimize,
                                   measurement_amend,
                                   auto_mapping,
                                   compile_only,
                                   specified_block,
                                   savepath) for i, group in enumerate(groups)]
    '''
    这里问题比较大，主要是线路编译和qubit map的问题。使用execute方法似乎不会自动分配，而是除非结构不合理，否则就按照程序的比特顺序进行。
    如果结构不合理，则会自动纠正到合理位置。
    这里我考虑一般程序都是从0~n-1的比特来写的，如果auto_mapping给定一个列表作为映射，则利用transpile进行映射。
    如果auto_mapping为True，则使用sabre的方法。
    
    '''
    if circuit_optimize:
        circuits = qiskit.compiler.transpile(circuits, backend=backend, optimization_level=3)

    if auto_mapping is True:
        circuits = qiskit.compiler.transpile(circuits, backend=backend, layout_method='sabre', optimization_level=0)
    elif isinstance(auto_mapping, list):
        circuits = qiskit.compiler.transpile(circuits, backend=backend, initial_layout=auto_mapping, 
                                             optimization_level=0)
    else:
        circuits = qiskit.compiler.transpile(circuits, backend=backend, optimization_level=0)
        
    try:
        job = qiskit.execute(
            experiments=circuits,
            backend=backend,
            shots=shots,
        )
    except Exception as e:
        raise RuntimeError(f'Error in submit_task. '
                           f'Error information: {e}')
    return job


def submit_task(circuit,
                task_name=None,
                tasktype=None,
                chip_id=72,
                shots=1000,
                circuit_optimize=True,
                measurement_amend=False,
                auto_mapping=False,
                specified_block=None,
                savepath=Path.cwd() / 'online_info'):
    if isinstance(circuit, qiskit.circuit.QuantumCircuit):
        circuit = [circuit]
    try:
        new_circuit = []
        for c in circuit:
            if isinstance(c, str):
                c = qiskit.QuantumCircuit.from_qasm_str(c)
                new_circuit.append(c)
    except:
        raise TypeError('str should in qasm')
    if not all(isinstance(i, qiskit.circuit.QuantumCircuit) for i in new_circuit):
        raise TypeError('all circuits should be qiskit.circuit.QuantumCircuit type or qasm')

    job = _submit_task_group(circuits=new_circuit,
                             task_name=task_name,
                             tasktype=tasktype,
                             chip_id=chip_id,
                             shots=shots,
                             circuit_optimize=circuit_optimize,
                             measurement_amend=measurement_amend,
                             auto_mapping=auto_mapping,
                             compile_only=False,
                             specified_block=specified_block,
                             savepath=savepath)
    task_id = job.job_id()

    ret = {'taskid': task_id, 'taskname': task_name}
    print('job')
    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')

    return task_id


def query_all_task(savepath=None):
    if not savepath:
        savepath = Path.cwd() / 'online_info'

    online_info = load_all_online_info(savepath)
    task_count = len(online_info)
    finished = 0

    for task in online_info:
        taskid = task['taskid']
        if not os.path.exists(savepath / '{}.txt'.format(taskid)):
            ret = query_by_taskid(taskid).copy()
            write_taskinfo(taskid, taskinfo=ret, savepath=savepath)
            finished += 1
        else:
            finished += 1
    return finished, task_count
