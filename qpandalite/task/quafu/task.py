import traceback
import warnings
import requests
from pathlib import Path
import os
import json
import urllib
import quafu
import re
from json.decoder import JSONDecodeError

from qpandalite.originir.originir_line_parser import OriginIR_Parser
from ..task_utils import load_all_online_info, write_taskinfo

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

class Translation_OriginIR_to_QuafuCircuit(OriginIR_Parser):
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
            operation, qubit, cbit, parameter = OriginIR_Parser.parse_line(line)
            if operation == 'QINIT':
                qc = quafu.QuantumCircuit(qubit)
                continue
            qc = Translation_OriginIR_to_QuafuCircuit.reconstruct_qasm(qc, operation, qubit, cbit, parameter)
        
        return qc
    
def submit_task(circuit = None, 
                task_name = None, 
                chip_id = None,
                shots = 10000,
                auto_mapping = True,
                savepath = Path.cwd() / 'quafu_online_info'
    ):

    qc = Translation_OriginIR_to_QuafuCircuit.translate(circuit)
    
    user = quafu.User()
    user.save_apitoken(default_token)
    task = quafu.Task()

    # validate chip_id
    if chip_id not in ['ScQ-P10','ScQ-P18','ScQ-P136']:
        raise RuntimeError(r"Invalid chip_id. "
                           r"Current quafu chip_id list: ['ScQ-P10','ScQ-P18','ScQ-P136']")

    task.config(backend=chip_id, shots=shots,compile=auto_mapping)

    n_retries = 5
    for i in range(n_retries):
        try:
            '''
            Quafu send throws
            if res.json()["status"] in [201, 205]:
                raise UserError(res_dict["message"])
            elif res.json()["status"] == 5001:
                raise CircuitError(res_dict["message"])
            elif res.json()["status"] == 5003:
                raise ServerError(res_dict["message"])
            elif res.json()["status"] == 5004:
                raise CompileError(res_dict["message"])
            '''
            result = task.send(qc, wait=False, name=task_name)            
            break
        except Exception as e:
            if i != n_retries - 1:
                print('Retry {} / {}'.format(i+1, n_retries))

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
    
    return taskid

def query_by_taskid(taskid):
    data = {"task_id": taskid}
    url = "https://quafu.baqis.ac.cn/qbackend/scq_task_recall/"

    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'api_token': default_token}
    res = requests.post(url, headers=headers, data=data)

    res_dict = json.loads(res.text)
    # status {0: "In Queue", 1: "Running", 2: "Completed", "Canceled": 3, 4: "Failed"}
        
    if res_dict["status"] in [0,1]:
        return None
    elif res_dict["status"] in [3,4]:
        return 'Failed'
        
    # results = json.loads(res_dict['raw'])
    results = res_dict
    return results

def query_all_task(savepath = None): 
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