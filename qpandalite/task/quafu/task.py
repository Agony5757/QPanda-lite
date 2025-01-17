import traceback
import warnings
import requests
from pathlib import Path
import os
import json
import quafu

import time

from json.decoder import JSONDecodeError


from qpandalite.originir.originir_line_parser import OriginIR_LineParser
from ..task_utils import load_all_online_info, write_taskinfo

# Initialize default_online_config with a default or dummy value
default_online_config = {'default_token': 'dummy_token'}

# Only attempt to read the config file if we're not generating docs
if os.getenv('SPHINX_DOC_GEN') != '1':
    try:
        fp = open('quafu_online_config.json', 'r')
    except FileNotFoundError as e:
        raise ImportError('Import quafu backend failed.\n'
                        'quafu_online_config.json is not found. '
                        'It should be always placed at current working directory (cwd).')
    except Exception as e:
        raise ImportError('Import quafu backend failed.\n'
                          'Unknown import error.'
                          '\n===== Original exception ======\n'
                          f'{traceback.format_exc()}')

    try:          
        default_online_config = json.load(fp)
        fp.close()
    except JSONDecodeError as e:
        raise ImportError('Import quafu backend failed.\n'
                            'Cannot load json from the quafu_online_config.json. '
                            'Please check the content.')
    except Exception as e:
        raise ImportError('Import quafu backend failed.\n'
                          'Unknown import error.'
                          '\n===== Original exception ======\n'
                          f'{traceback.format_exc()}')

    try:
        default_token = default_online_config['default_token']
    except KeyError as e:
        raise ImportError('Import quafu backend failed.\n'
                        'default_online_config.json should have the "default_token" key.')
    except Exception as e:
        raise ImportError('Import quafu backend failed.\n'
                          'Unknown import error. Original exception is:\n'
                          f'{str(e)}')

class Translation_OriginIR_to_QuafuCircuit(OriginIR_LineParser):
    @staticmethod
    def reconstruct_qasm(qc: quafu.QuantumCircuit, operation, qubit, cbit, parameter):
        if operation == 'RX':
            qc.rx(int(qubit), parameter)
        elif operation == 'RY':
            qc.ry(int(qubit), parameter)
        elif operation == 'RZ':
            qc.rz(int(qubit), parameter)
        elif operation == 'H':
            qc.h(int(qubit))
        elif operation == 'X':
            qc.x(int(qubit))
        elif operation == 'CZ':
            qc.cz(int(qubit[0]), int(qubit[1]))
        elif operation == 'CNOT':
            qc.cnot(int(qubit[0]), int(qubit[1]))
        elif operation == 'MEASURE':
            qc.measure([int(qubit)], [int(cbit)])
        elif operation == None:
            pass
        elif operation == 'CREG':
            pass
        else:
            raise RuntimeError('Unknown OriginIR operation. '
                               f'Operation: {operation}.')
        
        return qc

    @staticmethod
    def translate(originir):
        lines = originir.splitlines()
        qc : quafu.QuantumCircuit = None
        for line in lines:
            operation, qubit, cbit, parameter = OriginIR_LineParser.parse_line(line)
            if operation == 'QINIT':
                qc = quafu.QuantumCircuit(qubit)
                continue
            qc = Translation_OriginIR_to_QuafuCircuit.reconstruct_qasm(qc, operation, qubit, cbit, parameter)
        
        return qc


def _submit_task_group(circuits = None,
                task_name = None,
                chip_id = None,
                shots = 10000,
                auto_mapping = True,
                savepath = Path.cwd() / 'quafu_online_info',
                group_name = None):
    if not circuits: raise ValueError('circuit ??')
    if isinstance(circuits, list):
        user = quafu.User()
        user.save_apitoken(default_token)
        task = quafu.Task()
        taskid_list = []
        for index, c in enumerate(circuits):
            if not isinstance(c, str):
                raise ValueError('Input is not a valid circuit list (a.k.a List[str]).')
            qc = Translation_OriginIR_to_QuafuCircuit.translate(c)
            task.config(backend=chip_id,
                        shots=shots,
                        compile=auto_mapping)

            n_retries = 5
            for i in range(n_retries):
                try:
                    result = task.send(qc, wait=False, name=f'{task_name}-{index}', group=group_name)
                    break
                except Exception as e:
                    if i != n_retries - 1:
                        print('Retry {} / {}'.format(i + 1, n_retries))
                    raise e
            taskid = result.taskid
            taskid_list.append(taskid)
    return group_name, taskid_list


def submit_task(circuit = None,
                task_name = None,
                chip_id = None,
                shots = 10000,
                auto_mapping = True,
                savepath = Path.cwd() / 'quafu_online_info',
                group_name = None
    ):


    if chip_id not in ['ScQ-P10','ScQ-P18','ScQ-P136', 'ScQ-P10C']:
        raise RuntimeError(r"Invalid chip_id. "
                           r"Current quafu chip_id list: "
                           r"['ScQ-P10','ScQ-P18','ScQ-P136', 'ScQ-P10C']")

    if isinstance(circuit, str):
        qc = Translation_OriginIR_to_QuafuCircuit.translate(circuit)

        user = quafu.User()
        user.save_apitoken(default_token)
        task = quafu.Task()

        # validate chip_id
        task.config(backend=chip_id, shots=shots, compile=auto_mapping)

        n_retries = 5
        for i in range(n_retries):
            try:
                result = task.send(qc, wait=False, name=task_name)
                break
            except Exception as e:
                if i != n_retries - 1:
                    print('Retry {} / {}'.format(i + 1, n_retries))

                raise e

        taskid = result.taskid

        if savepath:
            task_info = dict()
            task_info['taskid'] = taskid
            task_info['taskname'] = task_name
            task_info['backend'] = chip_id
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            with open(savepath / 'online_info.txt', 'a') as fp:
                fp.write(json.dumps(task_info) + '\n')

    elif isinstance(circuit, list):
        group_name, taskid_list = _submit_task_group(circuits=circuit,
                                                     task_name=task_name,
                                                     chip_id=chip_id,
                                                     shots=shots,
                                                     auto_mapping=auto_mapping,
                                                     savepath=savepath,
                                                     group_name=group_name)

        if savepath:
            all_task_info = []
            for task_id in taskid_list:
                task_info = dict()
                task_info['groupname'] = group_name
                task_info['taskid'] = task_id
                task_info['taskname'] = task_name
                task_info['backend'] = chip_id
                all_task_info.append(task_info)
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            with open(savepath / 'online_info.txt', 'a') as fp:
                for task_info in all_task_info:
                    fp.write(json.dumps(task_info) + '\n')
            taskid = taskid_list
    else:
        raise ValueError('Input is not a valid originir string.')

    return taskid

def query_by_taskid_single(taskid, savepath):
    data = {"task_id": taskid}
    url = "https://quafu.baqis.ac.cn/qbackend/scq_task_recall/"

    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'api_token': default_token}
    res = requests.post(url, headers=headers, data=data)

    res_dict = json.loads(res.text)
    # status {0: "In Queue", 1: "Running", 2: "Completed", "Canceled": 3, 4: "Failed"}

    if res_dict["status"] in [0,1]:
        return 'Running'
    elif res_dict["status"] in [3,4]:
        return 'Failed'

    # results = json.loads(res_dict['raw'])
    results = res_dict
    if not os.path.exists(savepath / '{}.txt'.format(taskid)):
        write_taskinfo(taskid, results, savepath)

    return results

def query_by_taskid(taskid, savepath=None):
    if not savepath:
        savepath = Path.cwd() / 'quafu_online_info'
    if not taskid: raise ValueError('Task id ??')
    if isinstance(taskid, list):
        taskinfo = dict()
        taskinfo['status'] = 'success'
        taskinfo['result'] = []
        for taskid_i in taskid:
            taskinfo_i = query_by_taskid_single(taskid_i, savepath)
            if taskinfo_i == 'Failed':
                # if any task is failed, then this group is failed.
                taskinfo['status'] = 'failed'
                break
            elif taskinfo_i == 'Running':
                taskinfo['status'] = 'running'
            if taskinfo['status'] == 'success':
                taskinfo['result'].append(taskinfo_i)

    elif isinstance(taskid, str):
        taskinfo = query_by_taskid_single(taskid, savepath)
    else:
        raise ValueError('Invalid Taskid')

    return taskinfo


def query_by_taskid_sync(taskid,
                         interval=2.0,
                         timeout=60.0,
                         retry=5):

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

def query_task_by_group(group_name, history=None, verbose=True, savepath=None):
    if not group_name: raise ValueError('Task id ??')
    if not isinstance(group_name, str):
        raise ValueError('Invalid group name')
    if not savepath:
        savepath = Path.cwd() / 'quafu_online_info'

    if not history:
        online_info = load_all_online_info(savepath)
        history = dict()
        for task in online_info:
            if 'groupname' in task:
                group = task['groupname']
                if task['groupname'] not in history:
                    history[group] = [task['taskid']]
                else:
                    history[group].append(task['taskid'])
    user = quafu.User()
    user.save_apitoken(default_token)
    task = quafu.Task()
    group_result = task.retrieve_group(group_name, history, verbose)
    for result in group_result:
        result_dict = dict(result.__dict__)
        del result_dict['transpiled_circuit']
        write_taskinfo(result.taskid, result_dict, savepath=savepath)
    return group_result


def query_task_by_group_sync(group_name, verbose=True, savepath=Path.cwd() / 'quafu_online_info',
                             interval=2.0,
                             timeout=60.0,
                             retry=5
                             ):
    starttime = time.time()
    online_info = load_all_online_info(savepath)
    history = dict()
    for task in online_info:
        if 'groupname' in task:
            group = task['groupname']
            if task['groupname'] not in history:
                history[group] = [task['taskid']]
            else:
                history[group].append(task['taskid'])
    while True:
        try:
            now = time.time()
            if now - starttime > timeout:
                raise TimeoutError(f'Reach the maximum timeout.')
            time.sleep(interval)
            group_taskinfo = query_task_by_group(group_name, history, verbose, savepath)
            status = [task.task_status for task in group_taskinfo]
            if len(status) != len(history[group_name]):
                continue
            else:
                return group_taskinfo
        except RuntimeError as e:
            if retry > 0:
                retry -= 1
                print(f'Query failed. Retry remains {retry} times.')
            else:
                print(f'Retry count exhausted.')
                raise e


def query_all_tasks(savepath = None):
    if not savepath:
        savepath = Path.cwd() / 'quafu_online_info'
    
    online_info = load_all_online_info(savepath)
    for task in online_info:
        taskid = task['taskid']
        if not os.path.exists(savepath / '{}.txt'.format(taskid)):
            ret = query_by_taskid(taskid)
            if ret is None:
                continue
            elif ret == 'Failed':
                # write_taskinfo(savepath, taskid, {})
                write_taskinfo(taskid, taskinfo={}, savepath=savepath)
            else:                
                # write_taskinfo(savepath, taskid, ret)
                write_taskinfo(taskid, taskinfo=ret, savepath=savepath)

def query_all_task(savepath = None):
    '''Deprecated!! Use query_all_tasks instead
    '''
    warnings.warn(DeprecationWarning("Use query_all_tasks instead"))
    return query_all_task(savepath)