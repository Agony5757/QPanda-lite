import time
import requests
from pathlib import Path
import os
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings

from ..task_utils import *
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    with open('originq_online_config.json', 'r') as fp:
        default_online_config = json.load(fp)
    default_token = default_online_config['default_token']
    default_submit_url = default_online_config['default_submit_url']
    default_query_url = default_online_config['default_query_url']
    default_task_group_size = default_online_config['default_task_group_size']
except:
    default_token = ''
    default_submit_url = ''
    default_query_url = ''
    default_task_group_size = 0
    warnings.warn('originq_online_config.json is not found. '
                  'It should be always placed at current working directory (cwd).')


def parse_response_body(response_body):
    '''Parse response body (in query_by_taskid)

    Args:
        response_body (Dict): The response body returned by the server.

    Returns:
        Dict: The parsed dict containing these fields:
            - taskid
            - taskname
            - status 
            - result (not always)
    '''

    ret = dict()
    ret['taskid'] = response_body['taskId']
    ret['taskname'] = response_body['taskDescribe']

    task_status = response_body['taskState']
    if task_status == '3':
        # successfully finished !
        ret['status'] = 'success'

        # task_result
        task_result = response_body['taskResult']
        try:
            task_result = json.loads(task_result)
        except json.decoder.JSONDecodeError as e:
            raise RuntimeError('Error when parsing the response task_result. '
                               f'task_result = {task_result}')
        ret['result'] = task_result

        return ret
    elif task_status == '4':
        ret['status'] = 'failed'
        ret['result'] = {'errcode' : response_body['errCode'], 'errinfo': response_body['errInfo']}

        return ret
    else:
        ret['status'] = 'running'
        return ret

def query_by_taskid(taskid, url = default_query_url):
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
    if not url: raise ValueError('URL invalid.')
    
    # construct request_body for task query
    request_body = dict()
    request_body['token'] = default_token
    request_body['taskid'] = taskid

    request_body = json.dumps(request_body)
    response = requests.post(url=url, data=request_body, verify = False)
    status_code = response.status_code
    if status_code != 200:
        raise RuntimeError(f'Error in query_by_taskid. '
                           'The returned status code is not 200.'
                           f' Response: {response.text}')
    
    text = response.text
    response_body = json.loads(text)

    taskinfo = parse_response_body(response_body)

    return taskinfo

def query_by_taskid_sync(taskid, 
                         interval = 2.0, 
                         timeout = 60.0, 
                         url = default_query_url):    
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

        taskinfo = query_by_taskid(taskid, url)
        if taskinfo['status'] == 'running':
            continue
        if taskinfo['status'] == 'success':
            result = taskinfo['result']
            return result
        if taskinfo['status'] == 'failed':
            errorinfo = taskinfo['result']
            raise RuntimeError(f'Failed to execute, errorinfo = {errorinfo}')
        

def submit_task(circuit = None, 
                task_name = None, 
                tasktype = None, 
                chip_id = 72,
                shots = 1000,
                circuit_optimize = True,
                measurement_amend = True,
                auto_mapping = False,
                specified_block = None,
                url = default_submit_url,
                savepath = Path.cwd() / 'online_info'
):
    '''submit taskgroup

    Args:
        circuits (str): A quantum circuit to be submitted. 
        task_name (str, optional): The name of the task. Defaults to None.
        tasktype (int): The tasktype. Defaults to None. (Note: reserved field.)
        chip_id (int, optional): The chip id used to identify the quantum chip. Defaults to 72.
        shots (int, optional): Number of shots for every circuit. Defaults to 1000.
        circuit_optimize (bool, optional): Automatically optimize and transpile the circuit. Defaults to True.
        measurement_amend (bool, optional): Amend the measurement result using an internal algorithm. Defaults to True.
        auto_mapping (bool, optional): Automatically select the mapping. Defaults to False.
        specified_block (int, optional): The specified block on chip. Defaults to None. (Note: reserved field.)
        url (str, optional): The URL for submitting the task. Defaults to default_submit_url.
        savepath (str, optional): str. Defaults to Path.cwd()/'online_info'. If None, it will not save the task info.

    Raises:
        RuntimeError: Circuit not input
        RuntimeError: Error when submitting the task

    Returns:
        int: The taskid of this taskgroup
    '''
    if not circuit: raise RuntimeError('circuit ??')

    # construct request_body for task query
    request_body = dict()
    request_body['token'] = default_token
    request_body['ChipID'] = chip_id
    request_body['taskDescribe'] = task_name if task_name is not None else 'qpandalite' # 'Default info'
    request_body['QMachineType'] = tasktype if tasktype is not None else "5"
    request_body['TaskType'] = 0
    request_body['QProg'] = [circuit]
    
    configuration = dict()
    configuration['shot'] = shots
    configuration['circuitOptimization'] = circuit_optimize
    configuration['amendFlag'] = measurement_amend
    configuration['mappingFlag'] = auto_mapping
    configuration['specified_block'] = specified_block if specified_block is not None else []

    request_body['Configuration'] = configuration

    request_body = json.dumps(request_body)  

    response = requests.post(url=url, data=request_body, verify = False)
    status_code = response.status_code
    if status_code != 200:
        raise RuntimeError(f'Error in submit_task. The returned status code is not 200.'
                           f' Response: {response.text}')
    
    try:
        text = response.text
        response_body = json.loads(text)
        task_status = response_body['taskState']
        task_id = response_body['taskId']
        ret = {'taskid': task_id, 'taskname': task_name}
    except Exception as e:
        print(response_body)
        raise RuntimeError(f'Error in submit_task. The response body is corrupted. '
                           f'Response body: {response_body}')

    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')
    return task_id

def submit_task_group(circuits = None, 
                task_name = None, 
                tasktype = None, 
                chip_id = 72,
                shots = 1000,
                circuit_optimize = True,
                measurement_amend = True,
                auto_mapping = False,
                specified_block = None,
                url = default_submit_url,
                savepath = Path.cwd() / 'online_info'
):
    '''submit taskgroup

    Args:
        circuits (List[str]): A list of quantum circuits to be submitted. 
        task_name (str, optional): The name of the task. Defaults to None.
        tasktype (int): The tasktype. Defaults to None. (Note: reserved field.)
        chip_id (int, optional): The chip id used to identify the quantum chip. Defaults to 72.
        shots (int, optional): Number of shots for every circuit. Defaults to 1000.
        circuit_optimize (bool, optional): Automatically optimize and transpile the circuit. Defaults to True.
        measurement_amend (bool, optional): Amend the measurement result using an internal algorithm. Defaults to True.
        auto_mapping (bool, optional): Automatically select the mapping. Defaults to False.
        specified_block (int, optional): The specified block on chip. Defaults to None. (Note: reserved field.)
        url (str, optional): The URL for submitting the task. Defaults to default_submit_url.
        savepath (str, optional): str. Defaults to Path.cwd()/'online_info'. If None, it will not save the task info.

    Raises:
        ValueError: Circuit not input
        RuntimeError: Circuit number exceeds the default_task_group_size
        RuntimeError: Error when submitting the task

    Returns:
        int: The taskid of this taskgroup
    '''
    if not circuits: raise ValueError('circuit ??')
    if len(circuits) > default_task_group_size:
        raise RuntimeError(f'Circuit group size too large. '
                           f'(Expect: <= {default_task_group_size}, Get: {len(circuits)})')

    # construct request_body for task query
    request_body = dict()
    request_body['token'] = default_token
    request_body['ChipID'] = chip_id
    request_body['taskDescribe'] = task_name if task_name is not None else 'qpandalite' # 'Default info'
    request_body['QMachineType'] = tasktype if tasktype is not None else "5"
    request_body['TaskType'] = 0
    request_body['QProg'] = circuits
    
    configuration = dict()
    configuration['shot'] = shots
    configuration['circuitOptimization'] = circuit_optimize
    configuration['amendFlag'] = measurement_amend
    configuration['mappingFlag'] = auto_mapping
    configuration['specified_block'] = specified_block if specified_block is not None else []

    request_body['Configuration'] = configuration

    request_body = json.dumps(request_body)  
    
    response = requests.post(url=url, data=request_body, verify = False)
    status_code = response.status_code
    if status_code != 200:
        raise RuntimeError(f'Error in submit_task. The returned status code is not 200.'
                           f' Response: {response.text}')
    
    try:
        text = response.text
        response_body = json.loads(text)
        task_status = response_body['taskState']
        task_id = response_body['taskId']
        ret = {'taskid': task_id, 'taskname': task_name}
    except Exception as e:
        raise RuntimeError(f'Error in submit_task. The response body is corrupted. '
                           f'Response body: {response_body}')

    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')

    return task_id

def query_all_task(url = default_query_url, savepath = None): 
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
        if not os.path.exists(savepath / '{}.txt'.format(taskid)):
            taskinfo = query_by_taskid(taskid=taskid, url=url)
            if taskinfo['status'] == 'success' or taskinfo['status'] == 'failed':
                write_taskinfo(taskid, taskinfo, savepath)
                finished += 1
        else:
            finished += 1
    return finished, task_count
        
if __name__ == '__main__':
    make_savepath()
