import warnings
import requests
from pathlib import Path
import os
import json
import urllib
import quafu
import re

from ..task_utils import load_all_online_info, write_taskinfo

try:
    with open('quafu_online_config.json', 'r') as fp:
        default_online_config = json.load(fp)
    default_token = default_online_config['default_token']
except:
    default_token = ''
    warnings.warn('quafu_online_config.json is not found. '
                      'It should be always placed at current working directory (cwd).')

class Translation_OriginIR_to_QuafuCircuit:

    regexp_1q = re.compile(r'^([A-Z]+) *q\[(\d+)\]$')
    regexp_2q = re.compile(r'^([A-Z]+) *q\[(\d+)\], *q\[(\d+)\]$')
    regexp_1q1p = re.compile(r'^([A-Z]+) *q\[(\d+)\], *\((-?\d+(.\d*)?)\)$')
    regexp_meas = re.compile(r'^MEASURE q\[(\d+)\], *c\[(\d+)\]$')
    
    @staticmethod
    def handle_1q(line):
        matches = Translation_OriginIR_to_QuafuCircuit.regexp_1q.match(line)
        operation = matches.group(1)
        q = matches.group(2)
        return operation, q

    @staticmethod
    def handle_2q(line):
        matches = Translation_OriginIR_to_QuafuCircuit.regexp_2q.match(line)
        operation = matches.group(1)
        q1 = matches.group(2)
        q2 = matches.group(3)

        return operation, [q1, q2]

    @staticmethod
    def handle_1q1p(line):
        matches = Translation_OriginIR_to_QuafuCircuit.regexp_1q1p.match(line)
        operation = matches.group(1)
        q = matches.group(2)
        parameter = float(matches.group(3))
        return operation, q, parameter

    @staticmethod
    def handle_measure(line):
        matches = Translation_OriginIR_to_QuafuCircuit.regexp_meas.match(line)
        q = matches.group(1)
        c = matches.group(2)

        return q, c

    @staticmethod
    def parse_line(line):
        q = None
        c = None
        operation = None
        parameter = None
        if not line:
            pass 
        elif line.startswith('QINIT'):
            q = int(line.strip().split()[1])
            operation = 'QINIT'
        elif line.startswith('CREG'):
            c = int(line.strip().split()[1])
            operation = 'CREG'
        elif line.startswith('H'):
            operation, q = Translation_OriginIR_to_QuafuCircuit.handle_1q(line)
        elif line.startswith('X'):
            operation, q = Translation_OriginIR_to_QuafuCircuit.handle_1q(line)
        elif line.startswith('CZ'):
            operation, q = Translation_OriginIR_to_QuafuCircuit.handle_2q(line)
        elif line.startswith('RX'):
            operation, q, parameter = Translation_OriginIR_to_QuafuCircuit.handle_1q1p(line)
        elif line.startswith('MEASURE'):
            operation = 'MEASURE'
            q, c = Translation_OriginIR_to_QuafuCircuit.handle_measure(line)
        else:
            raise NotImplementedError(f'A invalid line: {line}.')      
        
        return operation, q, c, parameter

    @staticmethod
    def reconstruct_qasm(qc: quafu.QuantumCircuit, operation, qubit, cbit, parameter):
        if operation == 'RX':
            qc.rx(int(qubit), parameter)
        elif operation == 'H':
            qc.h(int(qubit))
        elif operation == 'X':
            qc.x(int(qubit))
        elif operation == 'CZ':
            qc.cz(int(qubit[0]), int(qubit[1]))
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
    def translate(originir) -> quafu.QuantumCircuit:
        lines = originir.splitlines()
        qc : quafu.QuantumCircuit = None
        for line in lines:
            operation, qubit, cbit, parameter = Translation_OriginIR_to_QuafuCircuit.parse_line(line)
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
        
    results = json.loads(res_dict['raw'])
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
                write_taskinfo(savepath, taskid, {})
            else:                
                write_taskinfo(savepath, taskid, ret)