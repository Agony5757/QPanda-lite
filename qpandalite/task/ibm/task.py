import json
import os
from pathlib import Path
import warnings
# from qiskit import IBMQ, QuantumCircuit, execute, transpile
import qiskit
# from qiskit_ibm_provider import IBMProvider
import qiskit_ibm_provider

from qpandalite.task.task_utils import write_taskinfo

provider = qiskit_ibm_provider.IBMProvider(instance='ibm-q/open/main')

try:
    with open('ibm_online_config.json', 'r') as fp:
        default_online_config = json.load(fp)
    default_token = default_online_config['default_token']
    qiskit.IBMQ.enable_account(default_token)
    qiskit_ibm_provider.IBMProvider.save_account(default_token)
    #IBMQ.enable_account('c3d3da0c74dc1a77d194557c2a0fa969b5f1b2fc000b2f75f7181dc05e3816aa5a85ad05f48ba1606a9ca8a17f61e7c2d8c5b8182910be719f29252e66b1045c')
    #IBMProvider.save_account('c3d3da0c74dc1a77d194557c2a0fa969b5f1b2fc000b2f75f7181dc05e3816aa5a85ad05f48ba1606a9ca8a17f61e7c2d8c5b8182910be719f29252e66b1045c')

except:
    default_token = ''
    default_submit_url = ''
    default_query_url = ''
    default_task_group_size = 0
    warnings.warn('ibm_online_config.json is not found. '
                  'It should be always placed at current working directory (cwd).')
    
def submit_task(circuit,
                task_name=None,
                backend_name=None,
                shots=1000,
                # mapping_map=None,
                savepath = Path.cwd() / 'ibm_online_info'):
    # if mapping_map is None:
    #     mapping_map = [[0, 1], [1, 0], [1, 2], [1, 3], [2, 1], [3, 1], [3, 5], [4, 5], [5, 3], [5, 4],
    #                    [5, 6], [6, 5]]
    qc = qiskit.QuantumCircuit.from_qasm_str(circuit)
    backend = provider.get_backend(backend_name)
    qc = qiskit.transpile(qc, 
                          #coupling_map=mapping_map, 
                          backend=backend, optimization_level=3)
    job = backend.run(qc, shots=shots)
    job_id = job.job_id()
    # job_backend = job.backend
    if task_name is None:
        task_name = 'default_ibm_task'
    if savepath:
        task_info = dict()
        task_info['taskid'] = job_id
        task_info['backend'] = backend_name
        task_info['name'] = task_name

        if not os.path.exists(savepath):
            os.makedirs(savepath)
        with open(savepath / 'ibm_online_info.txt', 'a') as fp:
            fp.write(json.dumps(task_info) + '\n')
    return job_id

def query_by_taskid(taskid):
    job = provider.retrieve_job(taskid)
    status = job.status()
    result = dict(job.result().get_counts())
    taskinfo = {'result': result}
    return taskinfo

def query_all_task(savepath = None):
    if not savepath:
        savepath = Path.cwd() / 'ibm_online_info'
            
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
