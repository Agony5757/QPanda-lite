import requests
from pathlib import Path
import os
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

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
    raise ImportError('originq_online_config.json is not found. '
                      'It should be always placed at current working directory (cwd).')


def parse_query_circuit(response_body):

    ret = dict()
    ret['taskid'] = response_body['taskId']
    ret['taskname'] = response_body['taskDescribe']

    task_status = response_body['taskState']
    if task_status == '3':
        # successfully finished !
        ret['status'] = 'success'

        # task_result
        task_result = response_body['taskResult']
        task_result = json.loads(task_result)
        ret['result'] = task_result

        return ret
    elif task_status == '4':
        ret['status'] = 'failed'
        ret['result'] = {'errcode' : response_body['errCode'], 'errinfo': response_body['errInfo']}

        return ret
    else:
        ret['status'] = 'running'
        return ret

def query_by_taskid(taskid = None, url = default_query_url):
    '''query_circuit_status

    Returns:
        - {'status': str, 'result': dict}
        status : success | failed | running
        result (when success): 
        result (when failed): {'errcode': str, 'errinfo': str}
        result (when running): N/A
    '''
    if not taskid: raise RuntimeError('Task id ??')
    
    # construct request_body for task query
    request_body = dict()
    request_body['token'] = default_token
    request_body['taskid'] = taskid

    request_body = json.dumps(request_body)
    response = requests.post(url=url, data=request_body, verify = False)
    status_code = response.status_code
    if status_code != 200:
        print(response)
        print(response.text)
        raise RuntimeError('Error in query_circuit_status')
    
    text = response.text
    response_body = json.loads(text)

    taskinfo = parse_query_circuit(response_body)

    return taskinfo

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
    '''submit_task

    Returns:
        - dict : {'status': task_status, 'taskid': task_id}
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
        print(response)
        print(response.text)
        raise RuntimeError('Error in submit_task')
    
    try:
        text = response.text
        response_body = json.loads(text)
        task_status = response_body['taskState']
        task_id = response_body['taskId']
        ret = {'taskid': task_id, 'taskname': task_name}
    except Exception as e:
        print(response_body)
        raise e

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
    '''submit_task

    Returns:
        - dict : {'status': task_status, 'taskid': task_id}
    '''
    if not circuits: raise RuntimeError('circuit ??')
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
        print(response)
        print(response.text)
        raise RuntimeError('Error in submit_task')
    
    try:
        text = response.text
        response_body = json.loads(text)
        task_status = response_body['taskState']
        task_id = response_body['taskId']
        ret = {'taskid': task_id, 'taskname': task_name}
    except Exception as e:
        print(response_body)
        raise e

    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')

    return task_id

def query_all_task(url = default_query_url, savepath = None): 
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
                write_taskinfo(savepath, taskid, taskinfo)
                finished += 1
        else:
            finished += 1
    return finished, task_count
        
if __name__ == '__main__':
    make_savepath()
