"""Origin Quantum Cloud (本源量子云) backend for task submission and querying.

This is the **primary production backend** used by QPanda-lite.  It
communicates with the Origin Quantum Cloud service over HTTP, supporting
circuit submission, status polling, and result retrieval.

Configuration is loaded from ``originq_cloud_config.json`` in the current
working directory.  The config file must contain the following keys:

- ``apitoken`` — API authentication token.
- ``submit_url`` — Task submission endpoint.
- ``query_url`` — Task query endpoint.
- ``task_group_size`` — Maximum number of circuits per submission group.
- ``available_qubits`` (optional) — List of physically available qubits.

Public API:
    - submit_task — Submit circuit(s) for execution on a real quantum chip.
    - query_by_taskid — Asynchronously query task status.
    - query_by_taskid_sync — Synchronously query task status (blocking).
    - query_all_tasks — Query all locally recorded tasks.
"""

import time
import traceback
from typing import List, Union
import requests
from pathlib import Path
import os
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings
from json.decoder import JSONDecodeError
import bz2

from qpandalite.task.task_utils import *

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Define default values for your configuration parameters
default_online_config = {
    'apitoken': 'default_api_token',
    'submit_url': 'default_submit_url',
    'query_url': 'default_query_url',
    'task_group_size': 'default_task_group_size'
}

TASK_STATUS_FAILED = 'failed'
TASK_STATUS_SUCCESS = 'success'
TASK_STATUS_RUNNING = 'running'

# Only attempt to read the config file if we're not generating docs
if os.getenv('SPHINX_DOC_GEN') != '1':
    try:
        with open('originq_cloud_config.json', 'r') as fp:
            default_online_config = json.load(fp)
    except FileNotFoundError as e:
        raise ImportError('Import origin qcloud backend failed.\n'
                          'originq_cloud_config.json is not found. '
                          'It should be always placed at current working directory (cwd).')
    except JSONDecodeError as e:
        raise ImportError('Import origin qcloud  backend failed.\n'
                          'Cannot load json from the originq_cloud_config.json. '
                          'Please check the content.')
    except Exception as e:
        raise ImportError('Import origin qcloud failed.\n'
                          'Unknown import error.'
                          '\n===== Original exception ======\n'
                          f'{traceback.format_exc()}')

    try:
        default_apitoken = default_online_config['apitoken']
        default_submit_url = default_online_config['submit_url']
        default_query_url = default_online_config['query_url']
        default_task_group_size = default_online_config['task_group_size']
        available_qubits = default_online_config.get('available_qubits', [])
    except KeyError as e:
        raise ImportError('Import origin qcloud  backend failed.\n'
                          'originq_cloud_config.json does not exist such a key.'
                          '\n===== Original exception ======\n'
                          f'{traceback.format_exc()}')

# Now you can safely use the configuration values:
default_token = default_online_config['apitoken']
default_submit_url = default_online_config['submit_url']
default_query_url = default_online_config['query_url']
default_task_group_size = default_online_config['task_group_size']


def parse_response_body(response_body):
    """Parse the raw response dict returned by the OriginQ Cloud query API.

    Extracts task ID, name, status, and result from the server response.
    Supports bz2-compressed responses.

    Args:
        response_body (dict): The JSON-decoded response from the server.

    Returns:
        dict: Parsed result containing:

            - ``taskid`` (str) — Task identifier.
            - ``taskname`` (str) — Task name.
            - ``status`` (str) — ``'success'``, ``'failed'``, or ``'running'``.
            - ``result`` (list, optional) — Execution results (when
              ``status='success'``).
            - ``result`` (dict, optional) — Error info with ``errcode`` and
              ``errinfo`` (when ``status='failed'``).

    Raises:
        Exception: If the server response indicates a failure at the API
            level.
    """

    ret = dict()
    recv_dict = response_body

    if not recv_dict["success"]:
        message = recv_dict["message"]
        code = recv_dict["code"]
        raise Exception(f"query task error : {message} (errcode: {code})")

    # print(recv_dict)
    result_list = recv_dict["obj"]

    ret['taskid'] = result_list['taskId']    

    task_status = result_list['taskStatus']
    if task_status == '3':
        # successfully finished !
        ret['status'] = TASK_STATUS_SUCCESS

        # task_result
        task_result = result_list['taskResult']
        try:
            # task_result is a list of json
            task_result = [json.loads(task_result_json) for task_result_json in task_result]
        except json.decoder.JSONDecodeError as e:
            raise RuntimeError('Error when parsing the response task_result. '
                               f'task_result = {result_list["taskResult"]}')
        
        ret['result'] = task_result
        return ret
    elif task_status == '4':
        ret['status'] = TASK_STATUS_FAILED
        ret['result'] = {'errcode': result_list['errorDetail'], 'errinfo': result_list['errorMessage']}

        return ret
    else:
        ret['status'] = TASK_STATUS_RUNNING
        return ret


def query_by_taskid_single(taskid: str, 
                           url=default_query_url, 
                           savepath=Path.cwd() / 'online_info', 
                           **kwargs):
    """Query a single task's status by its task ID (non-blocking).

    Checks the local cache first.  If no cached result exists, sends a
    request to the backend query endpoint.

    Args:
        taskid (str): The task ID to query.
        url (str, optional): Backend query endpoint URL.
        savepath (os.PathLike, optional): Directory for caching results.
        **kwargs: Additional platform-specific arguments (unused).

    Returns:
        dict: A dict with ``'status'`` (``'success'`` | ``'failed'`` |
        ``'running'``) and ``'result'`` (when the task has finished).

    Raises:
        ValueError: If *taskid* is empty or *url* is invalid.
        RuntimeError: If the server returns a non-200 status code.
    """

    if not taskid: raise ValueError('Task id ??')
    
    if savepath:
        filename = savepath / f'{taskid}.txt'
        if os.path.exists(filename):
            with open(filename, 'r') as fp:
                return json.load(fp)

    if not url: raise ValueError('URL invalid.')

    headers = dict()
    headers['origin-language'] = 'en'
    headers['Connection'] = 'keep-alive'
    headers['Content-Type'] = 'application/json;charset=UTF-8'
    headers['Authorization'] = 'oqcs_auth=' + default_token

    # construct request_body for task query
    request_body = dict()
    request_body['apiKey'] = default_token
    request_body['taskId'] = taskid

    response = requests.post(url=url,
                             headers=headers,
                             json=request_body,
                             verify=False,
                             timeout=10)

    status_code = response.status_code
    if status_code != 200:
        raise RuntimeError(f'Error in query_by_taskid. '
                           'The returned status code is not 200.'
                           f' Response: {response.text}')

    if response.content[:2] == b'BZ':
        text = bz2.decompress(response.content)
    else:
        text = response.text

    response_body = json.loads(text)
    taskinfo = parse_response_body(response_body)
    
    if savepath and (taskinfo['status'] == TASK_STATUS_SUCCESS or 
                     taskinfo['status'] == TASK_STATUS_FAILED):
        write_taskinfo(taskid, taskinfo, savepath)

    return taskinfo


def query_by_taskid(taskid: Union[List[str], str],
                    url=default_query_url,
                    savepath=Path.cwd() / 'online_info',
                    **kwargs):
    """Query task status by task ID (non-blocking).

    Supports querying a single task or a batch of tasks.  When a list is
    provided, results are merged; the overall status reflects the worst
    case (``failed`` > ``running`` > ``success``).

    Args:
        taskid (Union[List[str], str]): A single task ID or a list of task IDs.
        url (str, optional): Backend query endpoint URL.
        savepath (os.PathLike, optional): Directory for caching results.
        **kwargs: Additional platform-specific arguments (unused).

    Returns:
        dict: A dict with ``'status'`` and ``'result'``.

    Raises:
        ValueError: If *taskid* is empty or has an invalid type.
    """
    if not taskid: raise ValueError('Task id ??')

    if isinstance(taskid, list):
        taskinfo = dict()
        taskinfo['status'] = TASK_STATUS_SUCCESS
        taskinfo['result'] = []
        for taskid_i in taskid:
            taskinfo_i = query_by_taskid_single(taskid_i, url, savepath)
            if taskinfo_i['status'] == TASK_STATUS_FAILED:
                # if any task is failed, then this group is failed.
                taskinfo['status'] = TASK_STATUS_FAILED
                break
            elif taskinfo_i['status'] == TASK_STATUS_RUNNING:
                # if any task is running, then set to running
                taskinfo['status'] = TASK_STATUS_RUNNING
            if taskinfo_i['status'] == TASK_STATUS_SUCCESS:
                if taskinfo['status'] == TASK_STATUS_SUCCESS:
                    # update if task is successfully finished (so far)
                    taskinfo['result'].extend(taskinfo_i['result'])

    elif isinstance(taskid, str):
        taskinfo = query_by_taskid_single(taskid, url, savepath)
    else:
        raise ValueError('Invalid Taskid')
    
    return taskinfo


def query_by_taskid_sync(taskid,
                         interval=2.0,
                         timeout=60.0,
                         retry=5,
                         url=default_query_url,
                         savepath=None,
                         **kwargs):
    """Query task status by task ID (blocking) until completion or timeout.

    Polls the backend at *interval* seconds until the task finishes,
    times out, or retries are exhausted.

    Args:
        taskid (Union[List[str], str]): A single task ID or a list of task IDs.
        interval (float, optional): Polling interval in seconds.
        timeout (float, optional): Maximum total wait time in seconds.
        retry (int, optional): Number of retry attempts on transient errors.
        url (str, optional): Backend query endpoint URL.
        savepath (os.PathLike, optional): Directory for caching results.
        **kwargs: Additional platform-specific arguments (unused).

    Returns:
        list[dict]: Execution results once the task succeeds.

    Raises:
        TimeoutError: If *timeout* is exceeded.
        RuntimeError: If the task fails or retries are exhausted.
    """
    starttime = time.time()
    while True:
        try:
            now = time.time()
            if now - starttime > timeout:
                raise TimeoutError(f'Reach the maximum timeout.')

            time.sleep(interval)

            taskinfo = query_by_taskid(taskid, url, savepath)
            if taskinfo['status'] == TASK_STATUS_RUNNING:
                continue
            if taskinfo['status'] == TASK_STATUS_SUCCESS:
                result = taskinfo['result']
                return result
            if taskinfo['status'] == TASK_STATUS_FAILED:
                errorinfo = taskinfo['result']
                raise RuntimeError(f'Failed to execute, errorinfo = {errorinfo}')
        except Exception as e:
            if retry > 0:
                retry -= 1
                warnings.warn(f'Query failed. Retry remains {retry} times.')
            else:
                raise RuntimeError('Query failed. Retry count exhausted'
                                   f'Original exception is {e}')


def _submit_task_group(circuits=None,
                       task_name=None,
                       tasktype=None,
                       chip_id=72,
                       shots=1000,
                       circuit_optimize=True,
                       measurement_amend=False,
                       auto_mapping=False,
                       compile_only=False,
                       specified_block=None,
                       url=default_submit_url,
                       timeout=30,
                       retry=5,
                       savepath=Path.cwd() / 'online_info'
                       ):
    """Submit a group of circuits to the Origin Quantum Cloud.

    If the group size exceeds ``default_task_group_size``, the circuits
    are automatically split into sub-groups and submitted recursively.

    Args:
        circuits (list[str]): OriginIR circuit strings.
        task_name (str, optional): Task name.
        tasktype (int, optional): Task type identifier (reserved).
        chip_id (int, optional): Target quantum chip ID.
        shots (int, optional): Number of measurement shots.
        circuit_optimize (bool, optional): Enable circuit optimization.
        measurement_amend (bool, optional): Enable measurement error mitigation.
        auto_mapping (bool, optional): Enable automatic qubit mapping.
        compile_only (bool, optional): Compile only without execution.
        specified_block (int, optional): Reserved — target block on chip.
        url (str, optional): Submission endpoint URL.
        timeout (float, optional): HTTP request timeout in seconds.
        retry (int, optional): Number of retry attempts on failure.
        savepath (os.PathLike, optional): Directory for local task records.

    Returns:
        str or list[str]: Task ID(s) for the submitted group(s).

    Raises:
        ValueError: If *circuits* is empty.
        RuntimeError: If the server returns an error.
    """
    if not circuits: raise ValueError('circuit ??')
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

        return [_submit_task_group(circuits=group,
                                   task_name='{}_{}'.format(task_name, i),
                                   tasktype=tasktype,
                                   chip_id=chip_id,
                                   shots=shots,
                                   circuit_optimize=circuit_optimize,
                                   measurement_amend=measurement_amend,
                                   auto_mapping=auto_mapping,
                                   compile_only=compile_only,
                                   specified_block=specified_block,
                                   url=url,
                                   savepath=savepath) for i, group in enumerate(groups)]

        # raise RuntimeError(f'Circuit group size too large. '
        #                    f'(Expect: <= {default_task_group_size}, Get: {len(circuits)})')

    # construct request_body for task query
    headers = dict()
    headers['origin-language'] = 'en'
    headers['Connection'] = 'keep-alive'
    headers['Content-Type'] = 'application/json;charset=UTF-8'
    headers['Authorization'] = 'oqcs_auth=' + default_token

    request_body = dict()
    request_body['qmachineType'] = tasktype if tasktype is not None else 5
    request_body['qprogArr'] = circuits
    request_body['taskFrom'] = 4  # means it comes from QPanda
    request_body['chipId'] = chip_id
    request_body['shot'] = shots
    request_body['isAmend'] = 1 if measurement_amend else 0
    request_body['mappingFlag'] = 1 if auto_mapping else 0
    request_body['circuitOptimization'] = 1 if circuit_optimize else 0
    request_body['compileLevel'] = 3

    while True:
        try:
            response = requests.post(url=url,
                                    headers=headers,
                                    json=request_body,
                                    verify=False,
                                    timeout=timeout)
            status_code = response.status_code
            if status_code != 200:
                raise RuntimeError(f'Error in submit_task. The returned status code is not 200.'
                                f' Response: {response.text}')

            break
        except Exception as e:
            if retry > 0:
                retry -= 1
                warnings.warn(f'submit_task failed (possibly due to network issue). Retry remains {retry} times.')
                time.sleep(1)
            else:
                raise RuntimeError( 'submit_task failed. Retry count exhausted. '
                                   f'Original exception is {e}')

    try:
        text = response.text
        response_body = json.loads(text)
        # task_status = response_body['taskState']
        task_id = response_body['obj']['taskId']
    except Exception as e:
        raise RuntimeError(f'Error in submit_task. The response body is corrupted. '
                           f'Response body: {response_body}')

    return task_id


def submit_task(
        circuit,
        task_name=None,
        tasktype=None,
        chip_id=72,
        shots=1000,
        circuit_optimize=True,
        measurement_amend=False,
        auto_mapping=False,
        specified_block=None,
        url=default_submit_url,
        savepath=Path.cwd() / 'online_info',
        **kwargs
):
    """Submit one or more quantum circuits for execution on the Origin Quantum Cloud.

    This is the primary entry point for submitting quantum computing tasks.
    Accepts a single OriginIR string or a list of strings.  The actual
    submission is delegated to :func:`_submit_task_group`.

    Note:
        To submit a compile-only task, use ``_submit_task_group`` directly
        with ``compile_only=True``.

    Args:
        circuit (Union[str, List[str]]): OriginIR circuit string(s).
        task_name (str, optional): Human-readable task name.
        tasktype (int, optional): Task type identifier (reserved).
        chip_id (int, optional): Target chip ID (default ``72``).
        shots (int, optional): Number of measurement shots.
        circuit_optimize (bool, optional): Enable circuit optimization.
        measurement_amend (bool, optional): Enable measurement error mitigation.
        auto_mapping (bool, optional): Enable automatic qubit mapping.
        specified_block (int, optional): Reserved — target block on chip.
        url (str, optional): Submission endpoint URL.
        savepath (os.PathLike, optional): Directory for local task records.
        **kwargs: Additional keyword arguments forwarded to
            :func:`_submit_task_group`, including ``timeout`` and ``retry``.

    Returns:
        str: The task ID assigned by the backend.

    Raises:
        ValueError: If *circuit* is not a ``str`` or ``list`` of ``str``.
        RuntimeError: If the server returns an error.
    """

    if isinstance(circuit, list):
        for c in circuit:
            if not isinstance(c, str):
                raise ValueError('Input is not a valid circuit list (a.k.a List[str]).')

        taskid = _submit_task_group(
            circuits=circuit,
            task_name=task_name,
            tasktype=tasktype,
            chip_id=chip_id,
            shots=shots,
            circuit_optimize=circuit_optimize,
            measurement_amend=measurement_amend,
            auto_mapping=auto_mapping,
            compile_only=False,
            specified_block=specified_block,
            url=url,
            savepath=savepath,
            **kwargs
        )
    elif isinstance(circuit, str):
        taskid = _submit_task_group(
            circuits=[circuit],
            task_name=task_name,
            tasktype=tasktype,
            chip_id=chip_id,
            shots=shots,
            circuit_optimize=circuit_optimize,
            measurement_amend=measurement_amend,
            auto_mapping=auto_mapping,
            compile_only=False,
            specified_block=specified_block,
            url=url,
            savepath=savepath,            
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


def query_all_tasks(url=default_query_url, savepath=None, **kwargs):
    """Query the status of all locally recorded tasks.

    Iterates over tasks saved in *savepath*/``online_info.txt`` and queries
    each from the backend.  Finished results are cached locally.

    Args:
        url (str, optional): Backend query endpoint URL.
        savepath (os.PathLike, optional): Directory containing local task
            records.
        **kwargs: Additional platform-specific arguments (unused).

    Returns:
        tuple[int, int]: A ``(finished_count, total_count)`` pair.
    """
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
                    taskinfo = query_by_taskid(taskid_i, url)
                    if taskinfo['status'] == TASK_STATUS_SUCCESS or taskinfo['status'] == TASK_STATUS_FAILED:
                        write_taskinfo(taskid_i, taskinfo, savepath)
                    else:
                        status = 'unfinished'
            if status == 'finished':
                finished += 1

        elif isinstance(taskid, str):
            if not os.path.exists(savepath / '{}.txt'.format(taskid)):
                taskinfo = query_by_taskid(taskid, url)
                if taskinfo['status'] == TASK_STATUS_SUCCESS or taskinfo['status'] == TASK_STATUS_FAILED:
                    write_taskinfo(taskid, taskinfo, savepath)
                    finished += 1
            else:
                finished += 1
        else:
            raise RuntimeError('Invalid Taskid.')
    return finished, task_count

def query_all_task(url=default_query_url, savepath=None, **kwargs):
    """Deprecated — use :func:`query_all_tasks` instead."""
    warnings.warn(DeprecationWarning("Use query_all_tasks instead"))
    return query_all_tasks(url, savepath, **kwargs)

if __name__ == '__main__':
    result = query_by_taskid_single("55775D4858EF3D2C3813945703243A01")
    print(result)
#     ir = """QINIT 2
# CREG 2
# H q[0]
# H q[1]
# CZ q[0],q[1]
# H q[1]
# MEASURE q[0],c[0]
# MEASURE q[1],c[1]"""
#
#     taskid = submit_task([ir], task_name='test')
#     print(taskid)