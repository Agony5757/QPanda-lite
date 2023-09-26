import time
from typing import List, Union
import qpandalite.simulator as sim
from pathlib import Path
import os
import random
import json
import hashlib

from ..task_utils import *

default_task_group_size = 200

def _create_dummy_cache(dummy_path = Path.cwd() / 'dummy_server'):
    if not os.path.exists(dummy_path):
        os.makedirs(dummy_path)

    if not os.path.exists(dummy_path / 'dummy_result.jsonl'):
        with open(dummy_path / 'dummy_result.jsonl', 'a') as fp:
            pass

def _write_dummy_cache(taskid, 
                       taskname, 
                       results, 
                       dummy_path = Path.cwd() / 'dummy_server'):
    with open(dummy_path / 'dummy_result.jsonl', 'a') as fp:
        result_body = {
            'taskid' : taskid,
            'taskname' : taskname,
            'status' : 'success',
            'result' : results
        }

        fp.write(json.dumps(result_body) + '\n')

def _load_dummy_cache(taskid, dummy_path = Path.cwd() / 'dummy_server'):
    with open(dummy_path / 'dummy_result.jsonl', 'r') as fp:
        lines = fp.read().strip().splitlines()
        for line in lines[::-1]:
            result = json.loads(line)
            if result['taskid'] == taskid:
                return result
            
    raise ValueError(f'Taskid {taskid} is not found. This is impossible in dummy server mode.') 

def _random_taskid():
    n = random.random()
    md5 = hashlib.md5()
    md5.update(f"{n:.7f}".encode('utf-8'))
    # print(md5.hexdigest())
    return md5.hexdigest()

def _submit_task_group(
    circuits, 
    task_name, 
    shots,
    savepath,
    dummy_path
):
    # make dummy cache
    _create_dummy_cache(dummy_path)
    if len(circuits) > default_task_group_size:
        groups = []
        group = []
        for circuit in circuits:
            if len(group) >= default_task_group_size:
                groups.append(group)
                group = []
            group.append(circuit)
        if group:
            groups.append(group)

        return [_submit_task_group(group, 
                '{}_{}'.format(task_name, i), 
                shots, savepath, dummy_path) for i, group in enumerate(groups)]
    # generate taskid
    taskid = _random_taskid()
    results = []
    for circuit in circuits:
        simulator = sim.OriginIR_Simulator()
        prob_result = simulator.simulate(circuit)
        n_qubits = simulator.qubit_num
        key = []
        value = []
        # get shots
        for i, meas_result in enumerate(prob_result):
            key.append(bin(i)[2:].zfill(n_qubits))
            value.append(meas_result * shots)
        results.append({'key':key, 'value': value})
    
    _write_dummy_cache(taskid, task_name, results, dummy_path)

    return taskid

def submit_task(
    circuit, 
    task_name = None, 
    shots = 1000,
    savepath = Path.cwd() / 'online_info',
    dummy_path = Path.cwd() / 'dummy_server'
):   
    '''submit circuits or a single circuit'
    '''
    
    if isinstance(circuit, list):
        for c in circuit:
            if not isinstance(c, str):
                raise ValueError('Input is not a valid circuit list (a.k.a List[str]).')

        taskid = _submit_task_group(
            circuits = circuit, 
            task_name = task_name, 
            shots = shots,
            savepath = savepath,
            dummy_path = dummy_path
        )
    elif isinstance(circuit, str):
        taskid = _submit_task_group(
            circuits = [circuit], 
            task_name = task_name, 
            shots = shots,
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
        url (str, optional): The querying URL. Defaults to default_query_url.

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

def query_by_taskid_sync(taskid, 
                         interval = 2.0, 
                         timeout = 60.0, 
                         dummy_path = Path.cwd() / 'dummy_server'):    
    '''Query circuit status by taskid (synchronous version), it will wait until the task finished.
  
    Args:
        taskid (str): The taskid.
        interval (float): Interval time between two queries. (in seconds)
        url (str, optional): The querying URL. Defaults to default_query_url.

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
        
        time.sleep(interval)

        taskinfo = query_by_taskid(taskid, dummy_path=dummy_path)
        if taskinfo['status'] == 'running':
            continue
        if taskinfo['status'] == 'success':
            result = taskinfo['result']
            return result
        if taskinfo['status'] == 'failed':
            errorinfo = taskinfo['result']
            raise RuntimeError(f'Failed to execute, errorinfo = {errorinfo}')
        

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