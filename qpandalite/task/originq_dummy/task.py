import datetime
import time
from typing import List, Union
import warnings
from qpandalite.originir import OriginIR_LineParser, OriginIR_BaseParser
import qpandalite.simulator as sim
from qpandalite.simulator.error_model import ErrorLoader, ErrorLoader_GateSpecificError
from qpandalite.simulator.originir_simulator import OriginIR_NoisySimulator
try:
    from qpandalite.simulator.originir_simulator import OriginIR_Simulator
except ImportError as e:
    raise ImportError('You must install QPandaLiteCpp to enable the simulation.')

from pathlib import Path
import os
import random
import json
import hashlib
from json.decoder import JSONDecodeError

from ..task_utils import *

try:
    with open('originq_online_config.json', 'r') as fp:
        default_online_config = json.load(fp)
    available_qubits = default_online_config['available_qubits']
    available_topology = default_online_config['available_topology']
    default_task_group_size = default_online_config['task_group_size']
except FileNotFoundError as e:
    warnings.warn(ImportWarning('originq_online_config.json is not found. '
                'It is optional in dummy mode, '
                'but it is necessary for the real quantum device. '))
    
    available_qubits = []
    available_topology = []
    default_task_group_size = 200
except JSONDecodeError as e:
    raise ImportError('Import originq_dummy backend failed.\n'
                        'Cannot load json from the quafu_online_config.json. '
                        'Please check the content.')
except Exception as e:
    raise ImportError('Import originq_dummy backend failed.\n'
                      'Unknown import error. Original exception is:\n'
                      f'{str(e)}')
    
class DummyCacheContainer:
    def __init__(self) -> None:
        self.cached_results = dict()
        self.dummy_path = None

    def clear_dummy_cache(self):
        self.cached_results = dict()

    def save_dummy_cache(self, extra_savepath):
        if not os.path.exists(extra_savepath):
            os.makedirs(extra_savepath)

        extra_savepath = Path(extra_savepath)
        with open(extra_savepath / f'{timestr()}-dummycache.txt', 'a'):
            for result in self.cached_results:
                fp.write(json.dumps(result) + '\n')
        
    
    def write_dummy_cache(self, taskid, result_body):
        if taskid in self.cached_results:
            raise ValueError('Impossible to have same taskid in the same cache container.\n'
                             f'taskid (duplicated taskid) = {taskid}\n'
                             f'cached_result[taskid] (cached) = {self.cached_results[taskid]}\n'
                             f'result_body (input) = {result_body}')
    
        self.cached_results[taskid] = result_body
        
        if self.dummy_path:
            with open(self.dummy_path / 'dummy_result.jsonl', 'a') as fp:
                fp.write(json.dumps(result_body) + '\n')
    
    def load_dummy_cache(self, taskid):
        if taskid in self.cached_results:
            return self.cached_results[taskid]        
                
        if self.dummy_path:                
            with open(self.dummy_path / 'dummy_result.jsonl', 'r') as fp:
                lines = fp.read().strip().splitlines()
                for line in lines[::-1]:
                    result = json.loads(line)
                    if result['taskid'] == taskid:
                        return result

dummy_cache_container = DummyCacheContainer()

def set_dummy_path(dummy_path : os.PathLike):
    _create_dummy_cache(dummy_path)
    dummy_cache_container.dummy_path = Path(dummy_path)   

def save_dummy_cache(extra_savepath):
    dummy_cache_container.save_dummy_cache(extra_savepath)    

def clear_dummy():
    dummy_cache_container.clear_dummy_cache()    

def _create_dummy_cache(dummy_path = None):
    '''Create simulation storage for dummy simulation server.

    Args:
        dummy_path (str or Path, optional): Path for dummy storage. Defaults to None.
    '''
    if dummy_path:
        if not os.path.exists(dummy_path):
            os.makedirs(dummy_path)

        if isinstance(dummy_path, str):
            dummy_path = Path(dummy_path)

        if not os.path.exists(dummy_path / 'dummy_result.jsonl'):
            with open(dummy_path / 'dummy_result.jsonl', 'a') as fp:
                pass

def _write_dummy_cache(taskid, 
                       taskname, 
                       results):  
    '''Write simulation results to dummy server.

    Args:
        taskid (str): Taskid.
        taskname (str): Task name.
        results (List[Dict[str, List[float]]]): A list of simulation results. Example: [{'key':['001', '101'], 'value':[100, 100]}]
    '''
    result_body = {
        'taskid' : taskid,
        'taskname' : taskname,
        'status' : 'success',
        'result' : results
    }

    dummy_cache_container.write_dummy_cache(taskid, result_body)

def _load_dummy_cache(taskid):        
    '''Load simulation results by taskid.

    Args:
        taskid (str): Taskid.

    Returns:
        result (Dict): The result which emulates the results produced by query_by_taskid
    '''
    
    result = dummy_cache_container.load_dummy_cache(taskid)
    if result is not None:
        return result
                
    raise ValueError(f'Taskid {taskid} is not found. This is impossible in dummy server mode.') 

def _random_taskid() -> str:
    '''Create a dummy taskid for every task.

    Returns:
        str: Taskid.
    '''
    n = random.random()
    md5 = hashlib.md5()
    md5.update(f"{n:.14f}".encode('utf-8'))
    return md5.hexdigest()

def _submit_task_group_dummy_impl(
    circuits, 
    task_name,
    shots,
    auto_mapping,
    **kwargs
):
    # print("hi")
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
        return [_submit_task_group_dummy_impl(group, 
                '{}_{}'.format(task_name, i), 
                shots, 
                auto_mapping,
                **kwargs) for i, group in enumerate(groups)]
    
    # generate taskid
    taskid = _random_taskid()
    results = []

    generic_error = kwargs.get('generic_error', None)
    gatetype_error = kwargs.get('gatetype_error', None)
    gate_specific_error = kwargs.get('gate_specific_error', None)
    readout_error = kwargs.get('readout_error', [])

    for circuit in circuits:
        # If there is noise_description
        if generic_error or gatetype_error or gate_specific_error or readout_error:                  
            error_loader = ErrorLoader_GateSpecificError(
                generic_error = generic_error,
                gatetype_error = gatetype_error,
                gate_specific_error= gate_specific_error
            )          

            if auto_mapping:
                simulator = OriginIR_NoisySimulator(
                    backend_type='density_matrix',
                    error_loader=error_loader,
                    readout_error=readout_error)                
            else:
                simulator = OriginIR_NoisySimulator(
                    backend_type='density_matrix',
                    error_loader=error_loader,
                    readout_error=readout_error,
                    available_qubits=available_qubits, 
                    available_topology=available_topology)                
        else:
            if auto_mapping:
                simulator = sim.OriginIR_Simulator()
            else:
                simulator = sim.OriginIR_Simulator(available_qubits=available_qubits,
                                                   available_topology=available_topology)
        
        prob_result = simulator.simulate_pmeasure(circuit)
                
        n_qubits = simulator.qubit_num
        key = []
        value = []

        # get probs from probability list
        # Note: originq server will directly produce prob list instead of shots list.
        for i, meas_result in enumerate(prob_result):
            key.append(hex(i))
            value.append(meas_result)
        results.append({'key':key, 'value': value})
    
    # write cache, ready for loading results
    _write_dummy_cache(taskid, task_name, results)
    # print(results)
    return taskid

def submit_task(
    circuit, 
    task_name = None, 
    tasktype = None, # dummy parameter
    chip_id = None, # dummy parameter
    shots = 1000, # dummy parameter. Note: originq server will directly output prob instead of shots.
    circuit_optimize = True, # dummy parameter
    measurement_amend = False, # dummy parameter
    auto_mapping = False,
    specified_block = None, # dummy parameter
    savepath = Path.cwd() / 'online_info',
    url = None, # dummy parameter
    **kwargs
):   
    '''
    submit circuits or a single circuit (DUMMY)
    '''
    
    if isinstance(circuit, list):
        for c in circuit:
            if not isinstance(c, str):
                raise ValueError('Input is not a valid circuit list (a.k.a List[str]).')

        taskid = _submit_task_group_dummy_impl(
            circuits = circuit, 
            task_name = task_name, 
            shots = shots,
            auto_mapping = auto_mapping,
            **kwargs
        )
    elif isinstance(circuit, str):
        taskid = _submit_task_group_dummy_impl(
            circuits = [circuit], 
            task_name = task_name, 
            shots = shots,
            auto_mapping = auto_mapping,
            **kwargs
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
                    url = None, # dummy parameter
                    ):
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
    
    if isinstance(taskid, list):
        taskinfo = dict()
        taskinfo['status'] = 'success'
        taskinfo['result'] = []
        for taskid_i in taskid:
            taskinfo_i = _load_dummy_cache(taskid_i)
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
        taskinfo = _load_dummy_cache(taskid)
    else:
        raise ValueError('Invalid Taskid')
    
    return taskinfo

def query_by_taskid_sync(taskid : Union[str, List[str]], 
                         interval : float = 2.0, 
                         timeout : float  = 60.0, 
                         retry : int = 0,
                         url = None,  # dummy parameter
                         ):    
    '''Query circuit status by taskid (synchronous version), it will wait until the task finished.
  
    Args:
        taskid (str): The taskid.
        interval (float): Interval time between two queries. (in seconds)
        timeout (float): Interval time between two queries. (in seconds)

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
        
        taskinfo = query_by_taskid(taskid=taskid)
        if taskinfo['status'] == 'running':
            continue
        if taskinfo['status'] == 'success':
            result = taskinfo['result']
            return result
        if taskinfo['status'] == 'failed':
            errorinfo = taskinfo['result']
            raise RuntimeError(f'Failed to execute, errorinfo = {errorinfo}')
        
        time.sleep(interval)

def query_all_tasks(savepath = None, 
                   url = None, # dummy parameter
                   ): 
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
                    taskinfo = query_by_taskid(taskid=taskid_i)
                    if taskinfo['status'] == 'success' or taskinfo['status'] == 'failed':
                        write_taskinfo(taskid_i, taskinfo, savepath)
                    else:
                        status = 'unfinished'
            if status == 'finished':
                finished += 1

        elif isinstance(taskid, str):
            if not os.path.exists(savepath / '{}.txt'.format(taskid)):
                taskinfo = query_by_taskid(taskid=taskid)
                if taskinfo['status'] == 'success' or taskinfo['status'] == 'failed':
                    write_taskinfo(taskid, taskinfo, savepath)
                    finished += 1
            else:
                finished += 1
        else:
            raise RuntimeError('Invalid Taskid.')
    return finished, task_count

def query_all_task(savepath = None, 
                   url = None, # dummy parameter
                   ):
    '''Deprecated!! Use query_all_tasks instead
    '''
    warnings.warn(DeprecationWarning("Use query_all_tasks instead"))
    return query_all_tasks(savepath, url)

if __name__ == '__main__':
    _random_taskid()