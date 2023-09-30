import time
from typing import List, Union
import warnings
import qpandalite.simulator as sim
try:
    from qpandalite.simulator import OriginIR_Simulator
except ImportError as e:
    raise ImportError('You must install QPandaLiteCpp to enable the simulation.')
from pathlib import Path
import os
import random
import json
import hashlib

from ..task_utils import *

try:
    with open('originq_online_config.json', 'r') as fp:
        default_online_config = json.load(fp)
    available_qubits = default_online_config['available_qubits']
    available_topology = default_online_config['available_topology']
    default_task_group_size = default_online_config['task_group_size']
except Exception as e:
    warnings.warn(ImportWarning('originq_online_config.json is not found. '
                'It should be always placed at current working directory (cwd).'))
    available_qubits = []
    available_topology = []
    default_task_group_size = 200

def _create_dummy_cache(dummy_path = Path.cwd() / 'dummy_server'):
    '''Create simulation storage for dummy simulation server.

    Args:
        dummy_path (str or Path, optional): Path for dummy storage. Defaults to Path.cwd()/'dummy_server'.
    '''
    if not os.path.exists(dummy_path):
        os.makedirs(dummy_path)

    if not os.path.exists(dummy_path / 'dummy_result.jsonl'):
        with open(dummy_path / 'dummy_result.jsonl', 'a') as fp:
            pass

def _write_dummy_cache(taskid, 
                       taskname, 
                       results, 
                       dummy_path = Path.cwd() / 'dummy_server'):  
    '''Write simulation results to dummy server.

    Args:
        taskid (str): Taskid.
        taskname (str): Task name.
        results (List[Dict[str, List[float]]]): A list of simulation results. Example: [{'key':['001', '101'], 'value':[100, 100]}]
        dummy_path (str or Path, optional): Path for dummy storage. Defaults to Path.cwd()/'dummy_server'.
    '''

    if not os.path.exists(dummy_path):
        os.makedirs(dummy_path)

    with open(dummy_path / 'dummy_result.jsonl', 'a') as fp:
        result_body = {
            'taskid' : taskid,
            'taskname' : taskname,
            'status' : 'success',
            'result' : results
        }

        fp.write(json.dumps(result_body) + '\n')

def _load_dummy_cache(taskid, dummy_path = Path.cwd() / 'dummy_server'):        
    '''Write simulation results to dummy server.

    Args:
        taskid (str): Taskid.
        dummy_path (str or Path, optional): Path for dummy storage. Defaults to Path.cwd()/'dummy_server'.

    Returns:
    '''

    if not os.path.exists(dummy_path):
        os.makedirs(dummy_path)

    with open(dummy_path / 'dummy_result.jsonl', 'r') as fp:
        lines = fp.read().strip().splitlines()
        for line in lines[::-1]:
            result = json.loads(line)
            if result['taskid'] == taskid:
                return result
            
    raise ValueError(f'Taskid {taskid} is not found. This is impossible in dummy server mode.') 

def _random_taskid() -> str:
    '''Create a dummy taskid for every task.

    Returns:
        str: Taskid.
    '''
    n = random.random()
    md5 = hashlib.md5()
    md5.update(f"{n:.7f}".encode('utf-8'))
    return md5.hexdigest()

def _submit_task_group(
    circuits, 
    task_name,
    shots,
    auto_mapping,
    savepath,
    dummy_path
):
    # make dummy cache
    _create_dummy_cache(dummy_path)
    if len(circuits) > default_task_group_size:
        # list of circuits
        groups = []
        group = []
        for circuit in circuits:
            if len(group) >= default_task_group_size:
                groups.append(group)
                group = []
            group.append(circuit)
        if group:
            groups.append(group)

        # recursively call, and return a list of taskid
        return [_submit_task_group(group, 
                '{}_{}'.format(task_name, i), 
                shots, 
                auto_mapping,
                savepath, 
                dummy_path) for i, group in enumerate(groups)]
    
    # generate taskid
    taskid = _random_taskid()
    results = []
    for circuit in circuits:
        simulator = sim.OriginIR_Simulator()
        if auto_mapping:
            prob_result = simulator.simulate(circuit)
        else:
            prob_result = simulator.simulate(circuit, 
                                            available_qubits=available_qubits,
                                            available_topology=available_topology)
        n_qubits = simulator.qubit_num
        key = []
        value = []

        # get shots from probability list
        for i, meas_result in enumerate(prob_result):
            key.append(bin(i)[2:].zfill(n_qubits))
            value.append(meas_result * shots)
        results.append({'key':key, 'value': value})
    
    # write cache, ready for loading results
    _write_dummy_cache(taskid, task_name, results, dummy_path)

    return taskid

def submit_task(
    circuit, 
    task_name = None, 
    tasktype = None, # dummy parameter
    chip_id = None, # dummy parameter
    shots = 1000,
    circuit_optimize = True, # dummy parameter
    measurement_amend = False, # dummy parameter
    auto_mapping = False,
    specified_block = None, # dummy parameter
    savepath = Path.cwd() / 'online_info',
    url = None, # dummy parameter
    dummy_path = Path.cwd() / 'dummy_server'
):   
    '''submit circuits or a single circuit (DUMMY)
    '''
    
    if isinstance(circuit, list):
        for c in circuit:
            if not isinstance(c, str):
                raise ValueError('Input is not a valid circuit list (a.k.a List[str]).')

        taskid = _submit_task_group(
            circuits = circuit, 
            task_name = task_name, 
            shots = shots,
            auto_mapping = auto_mapping,
            savepath = savepath,
            dummy_path = dummy_path
        )
    elif isinstance(circuit, str):
        taskid = _submit_task_group(
            circuits = [circuit], 
            task_name = task_name, 
            shots = shots,
            auto_mapping = auto_mapping,
            savepath = savepath,
            dummy_path = dummy_path
        )
    else:
        raise ValueError('Input must be a str or List[str], where each str is a valid originir string.')
        
    ret = {'taskid': taskid, 'taskname': task_name}
    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')

    return taskid

def query_by_taskid(taskid : Union[List[str],str], 
                    dummy_path = Path.cwd() / 'dummy_server'):
    '''Query circuit status by taskid (Async). This function will return without waiting.
  
    Args:
        taskid (str): The taskid.
        dummy_path (str or Path, optional): Path for dummy storage. Defaults to Path.cwd()/'dummy_server'.

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
    
    if isinstance(taskid, list):
        taskinfo = dict()
        taskinfo['status'] = 'success'
        taskinfo['result'] = []
        for taskid_i in taskid:
            taskinfo_i = _load_dummy_cache(taskid_i, dummy_path)
            if taskinfo_i['status'] == 'failed':
                # if any task is failed, then this group is failed.
                taskinfo['status'] = 'failed'
                break
            elif taskinfo_i['status'] == 'running':
                # if any task is running, then set to running
                taskinfo['status'] = 'running'
            if taskinfo_i['status'] == 'success':                
                if taskinfo['status'] == 'success':
                    # update if task is successfully finished (so far)
                    taskinfo['result'].extend(taskinfo_i['result'])
            
    elif isinstance(taskid, str):
        taskinfo = _load_dummy_cache(taskid, dummy_path)
    else:
        raise ValueError('Invalid Taskid')
    
    return taskinfo

def query_by_taskid_sync(taskid : Union[str, List[str]], 
                         interval : float = 2.0, 
                         timeout : float  = 60.0, 
                         retry : int = 0,
                         dummy_path = Path.cwd() / 'dummy_server'):    
    '''Query circuit status by taskid (synchronous version), it will wait until the task finished.
  
    Args:
        taskid (str): The taskid.
        interval (float): Interval time between two queries. (in seconds)
        timeout (float): Interval time between two queries. (in seconds)
        dummy_path (str or Path, optional): Path for dummy storage. Defaults to Path.cwd()/'dummy_server'.

    Raises:
        RuntimeError: Taskid invalid.
        RuntimeError: URL invalid.
        TimeoutError: Timeout reached

    Returns:
        Dict[str, dict]: The status and the result
            status : success | failed | running
            result (when success): List[Dict[str,list]]
            result (when failed): {'errcode': str, 'errinfo': str}
            result (when running): N/A
    '''    
    starttime = time.time()
    while True:
        now = time.time()
        if now - starttime > timeout:
            raise TimeoutError(f'Reach the maximum timeout.')
        
        taskinfo = query_by_taskid(taskid, dummy_path=dummy_path)
        if taskinfo['status'] == 'running':
            continue
        if taskinfo['status'] == 'success':
            result = taskinfo['result']
            return result
        if taskinfo['status'] == 'failed':
            errorinfo = taskinfo['result']
            raise RuntimeError(f'Failed to execute, errorinfo = {errorinfo}')
        
        time.sleep(interval)

def query_all_task(dummy_path = Path.cwd() / 'dummy_server', 
                   savepath = None): 
    '''Query all task info in the savepath. If you only want to query from taskid, then you can use query_by_taskid instead.

    Args:
        url (str, optional): The url for querying. Defaults to default_query_url.
        savepath (PathLikeObject(str, pathlib.Path, etc...), optional): The savepath for loading the online info. Defaults to None.

    Returns:
        tuple[int,int]: Two integers (finished task count, all task count)
    '''
    if not savepath:
        savepath = Path.cwd() / 'online_info'
    
    online_info = load_all_online_info(savepath)
    task_count = len(online_info)
    finished = 0
    for task in online_info:
        taskid = task['taskid']

        if isinstance(taskid, list):
            status = 'finished'
            for taskid_i in taskid:
                if not os.path.exists(savepath / '{}.txt'.format(taskid)):
                    taskinfo = query_by_taskid(taskid_i, dummy_path)
                    if taskinfo['status'] == 'success' or taskinfo['status'] == 'failed':
                        write_taskinfo(taskid_i, taskinfo, savepath)
                    else:
                        status = 'unfinished'
            if status == 'finished':
                finished += 1

        elif isinstance(taskid, str):
            if not os.path.exists(savepath / '{}.txt'.format(taskid)):
                taskinfo = query_by_taskid(taskid, dummy_path)
                if taskinfo['status'] == 'success' or taskinfo['status'] == 'failed':
                    write_taskinfo(taskid, taskinfo, savepath)
                    finished += 1
            else:
                finished += 1
        else:
            raise RuntimeError('Invalid Taskid.')
    return finished, task_count

if __name__ == '__main__':
    _random_taskid()