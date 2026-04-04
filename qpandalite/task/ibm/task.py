"""IBM Quantum backend for task submission and querying via Qiskit.

Submits quantum circuits (in OpenQASM 2.0 or Qiskit ``QuantumCircuit``
format) to IBM Quantum devices using the ``qiskit_ibm_provider``
package.  Results are retrieved as measurement counts.

Configuration is loaded from ``ibm_online_config.json`` in the current
working directory.  The config file must contain a ``default_token`` key
with the IBM Quantum API token.  On first import the token is saved via
``IBMProvider.save_account``.

Requires ``qiskit`` and ``qiskit_ibm_provider``.

Public API:
    - submit_task — Submit circuit(s) for execution on IBM Quantum.
    - query_by_taskid — Query task status by job ID.
    - query_by_taskid_sync — Blocking query with polling.
    - query_all_tasks — Query all locally recorded tasks.
"""

import traceback
import qiskit
from qpandalite.task.task_utils import *

import time
from typing import List, Union

from pathlib import Path
import os
import json
from json.decoder import JSONDecodeError
import warnings

import qiskit_ibm_provider

saved_account = qiskit_ibm_provider.IBMProvider.saved_accounts()
if saved_account is {}:
    try:
        with open('ibm_online_config.json', 'r') as fp:
            default_online_config = json.load(fp)
            default_token = default_online_config['default_token']
    except FileNotFoundError as e:
        raise ImportError('Import IBM backend failed.\n'
                        'originq_online_config.json is not found. '
                        'It should be always placed at current working directory (cwd).')
    except JSONDecodeError as e:
        raise ImportError('Import IBM backend failed.\n'
                            'Cannot load json from the originq_online_config.json. '
                            'Please check the content.')
    except Exception as e:
        raise ImportError('Import IBM backend failed.\n'
                        'Unknown import error.'                      
                        '\n===== Original exception ======\n'
                        f'{traceback.format_exc()}')
    try:

        qiskit_ibm_provider.IBMProvider.save_account(default_token)
    except Exception as e:
        raise ImportError('Import IBM backend failed.\n'
                           'Failed to login.'
                           '\n===== Original exception ======\n'
                           f'{traceback.format_exc()}')

try:
    provider = qiskit_ibm_provider.IBMProvider(instance='ibm-q/open/main')
except Exception as e:
    raise ImportError('Import IBM backend failed.\n'
                        'Failed to login.'
                        '\n===== Original exception ======\n'
                        f'{traceback.format_exc()}')

backends = provider.backends()

def query_by_taskid_single(taskid: str, ):
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

    # construct request_body for task query
    job = provider.retrieve_job(job_id=taskid)
    status = job.status().name
    if status != 'DONE':
        ret = {'status': status, 'value': job.status().value}
        warnings.warn(f'Error in query_by_taskid. '
                      'The job has not successfully run.'
                      f' Response: {job.status().value}')
        return ret

    ret = {}
    taskinfo = job.result().to_dict()
    ret['status'] = 'DONE'
    ret['time'] = taskinfo['date'].strftime('%a %d %b %Y, %I:%M%p')
    ret['backend_name'] = taskinfo['backend_name']
    ret['backend_version'] = taskinfo['backend_version']
    results = []

    for single_result in taskinfo['results']:
        results.append(single_result['data']['counts'])
    ret['result'] = results

    return ret


def query_by_taskid(taskid: Union[List[str], str]):
    """Query task status by job ID (non-blocking).

    Supports a single job ID or a list.  When querying a list, results
    are aggregated; the overall status reflects the worst case.

    Args:
        taskid (Union[List[str], str]): IBM Quantum job ID(s).

    Returns:
        dict: Aggregated status and results.

    Raises:
        ValueError: If *taskid* is empty or has an invalid type.
    """
    if not taskid: raise ValueError('Task id ??')
    if isinstance(taskid, list):
        taskinfo = dict()
        taskinfo['status'] = 'success'
        taskinfo['result'] = []
        for taskid_i in taskid:
            taskinfo_i = query_by_taskid_single(taskid_i)
            if taskinfo_i['status'] in ['ERROR', 'CANCELLED']:
                # if any task is failed, then this group is failed.
                taskinfo['status'] = 'failed'
                break
            elif taskinfo_i['status'] in ['INITIALIZING', 'QUEUED', 'VALIDATING', 'RUNNING']:
                # if any task is running, then set to running
                taskinfo['status'] = 'running'
            if taskinfo_i['status'] == 'DONE':
                if taskinfo['status'] == 'success':
                    # update if task is successfully finished (so far)
                    taskinfo['result'].extend(taskinfo_i['result'])

    elif isinstance(taskid, str):
        taskinfo = query_by_taskid_single(taskid)
    else:
        raise ValueError('Invalid Taskid')

    return taskinfo


def query_by_taskid_sync(taskid,
                         interval=2.0,
                         timeout=60.0,
                         retry=5, ):
    """Query task status by job ID (blocking) until completion or timeout.

    Args:
        taskid (Union[List[str], str]): IBM Quantum job ID(s).
        interval (float, optional): Polling interval in seconds.
        timeout (float, optional): Maximum total wait time in seconds.
        retry (int, optional): Number of retry attempts on transient errors.

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


def _submit_task_group(circuits=None,
                       task_name=None,
                       tasktype=None,
                       chip_id=None,
                       shots=1000,
                       circuit_optimize=True,
                       measurement_amend=False,
                       auto_mapping=False,
                       compile_only=False,
                       specified_block=None,
                       savepath=Path.cwd() / 'online_info'):
    """Submit a group of Qiskit circuits to an IBM Quantum backend.

    If the group exceeds the backend's ``max_circuits`` limit, it is
    automatically split into sub-groups.

    Args:
        circuits (list): Qiskit ``QuantumCircuit`` objects.
        task_name (str, optional): Task name.
        tasktype: Reserved (unused).
        chip_id (str, optional): IBM backend name.
        shots (int, optional): Number of measurement shots.
        circuit_optimize (bool, optional): Enable Qiskit transpiler
            optimization (level 3).
        measurement_amend: Reserved (unused).
        auto_mapping (Union[bool, list], optional): ``True`` for SABRE
            layout, a list for explicit initial layout, ``False`` for
            default mapping.
        compile_only: Reserved (unused).
        specified_block: Reserved (unused).
        savepath (os.PathLike, optional): Directory for local task records.

    Returns:
        qiskit.providers.Job: The submitted Qiskit job object.

    Raises:
        ValueError: If *chip_id* is invalid or *shots* exceeds the backend
            limit.
        RuntimeError: If circuit execution fails.
    """
    backends_name = [i.name for i in backends]
    if chip_id not in backends_name:
        raise ValueError(f'no such chip, should be one of {backends_name}')
    backend = provider.get_backend(chip_id)
    max_group_size = backend.max_circuits
    max_shots = backend.max_shots
    if shots > max_shots:
        raise ValueError(f'maximum shots number exceeded, should less than {max_shots}')

    if len(circuits) > max_group_size:
        groups = []
        group = []
        for circuit in circuits:
            if len(group) >= max_group_size:
                groups.append(group)
                group = []
            group.append(circuit)
        if group:
            groups.append(group)

        return [_submit_task_group(group,
                                   '{}_{}'.format(task_name, i),
                                   tasktype,
                                   chip_id,
                                   shots,
                                   circuit_optimize,
                                   measurement_amend,
                                   auto_mapping,
                                   compile_only,
                                   specified_block,
                                   savepath) for i, group in enumerate(groups)]
    '''
    这里问题比较大，主要是线路编译和qubit map的问题。使用execute方法似乎不会自动分配，而是除非结构不合理，否则就按照程序的比特顺序进行。
    如果结构不合理，则会自动纠正到合理位置。
    这里我考虑一般程序都是从0~n-1的比特来写的，如果auto_mapping给定一个列表作为映射，则利用transpile进行映射。
    如果auto_mapping为True，则使用sabre的方法。
    
    '''
    if circuit_optimize:
        circuits = qiskit.compiler.transpile(circuits, backend=backend, optimization_level=3)

    if auto_mapping is True:
        circuits = qiskit.compiler.transpile(circuits, backend=backend, layout_method='sabre', optimization_level=1)
    elif isinstance(auto_mapping, list):
        circuits = qiskit.compiler.transpile(circuits, backend=backend, initial_layout=auto_mapping, 
                                             optimization_level=1)
    else:
        circuits = qiskit.compiler.transpile(circuits, backend=backend, optimization_level=1)
        
    try:
        job = qiskit.execute(
            experiments=circuits,
            backend=backend,
            shots=shots,
        )
    except Exception as e:
        raise RuntimeError(f'Error in submit_task. '
                           f'Error information: {e}')
    return job


# =======
import qiskit
# import qiskit_ibm_provider
from qpandalite.task.task_utils import write_taskinfo


"""
    The module is an attempt to convert our circuit in OriginIR into OpenQASM 2.0;

    Although there are not so many differences between the two, apparently simply using from_qasm_str 
    is not able to import the circuit written in OriginIR. 

    OPENQASM 2.0;
    include "qelib1.inc";
    qreg q[3];                          QINIT 3
    creg c[3];                          CREG 3
    h q[0];                             H q[0]
    cx q[0],q[1];                       CNOT q[0], q[1]
    cx q[0],q[2];                       CNOT q[0], q[2]             
    measure q[0] -> c[0];               MEASURE q[0], c[0]           
    measure q[1] -> c[1];               MEASURE q[1], c[1]
    measure q[2] -> c[2];               MEASURE q[2], c[2]
 
    They have similar structure, but
    1. the OPENQASM 2.0 has an additional header;
    2. In the main(circuit) part,
        2.1. case sensitive: QASM-uppercase, OriginIR-lowercase
        2.2. naming: QASM-qreg, OriginIR-QINIT
        2.3. gate definition: I could imagine there are lots of differences 
    3. In the measurement part, 
        OPENQASM uses " -> ", while OriginIR chooses ", "

    4. MORE ADDED
        We, as a team of developers, may need your help and feedbacks in order to make the final transition from  OriginIR into OpenQASM 2.0

        The testing program is at the end of this file, you may run this file by typing()
        python task.py in your terminal, but be sure of your relative directory.

        Once you find something new we are not currently support, please let us know via WeChat, or start an issue on the Github.
"""

# try:
#     with open('ibm_online_config.json', 'r') as fp:
#         default_online_config = json.load(fp)
#     default_token = default_online_config['default_token']
#     qiskit.IBMQ.enable_account(default_token)
#     qiskit_ibm_provider.IBMProvider.save_account(default_token)
#     provider = qiskit_ibm_provider.IBMProvider(instance='ibm-q/open/main')
    
# except:
#     raise ImportError('ibm_online_config.json is not found. '
#                       'It should be always placed at current working directory (cwd).')
    
def submit_task(circuit,
                task_name=None,
                tasktype=None,
                chip_id=72,
                shots=1000,
                circuit_optimize=True,
                measurement_amend=False,
                auto_mapping=False,
                specified_block=None,
                savepath=Path.cwd() / 'online_info'):
    """Submit one or more quantum circuits for execution on IBM Quantum.

    Accepts Qiskit ``QuantumCircuit`` objects, QASM strings, or lists
    thereof.

    Args:
        circuit (Union[QuantumCircuit, str, list]): Circuit(s) to submit.
        task_name (str, optional): Human-readable task name.
        tasktype: Reserved (unused).
        chip_id (str, optional): IBM backend name.
        shots (int, optional): Number of measurement shots.
        circuit_optimize (bool, optional): Enable transpiler optimization.
        measurement_amend: Reserved (unused).
        auto_mapping (Union[bool, list], optional): Qubit mapping strategy.
        specified_block: Reserved (unused).
        savepath (os.PathLike, optional): Directory for local task records.

    Returns:
        str: The IBM Quantum job ID.

    Raises:
        TypeError: If circuits are not ``QuantumCircuit`` or valid QASM.
    """
    if isinstance(circuit, qiskit.circuit.QuantumCircuit):
        circuit = [circuit]
    try:
        new_circuit = []
        for c in circuit:
            if isinstance(c, str):
                c = qiskit.QuantumCircuit.from_qasm_str(c)
                new_circuit.append(c)
    except:
        raise TypeError('str should in qasm')
    if not all(isinstance(i, qiskit.circuit.QuantumCircuit) for i in new_circuit):
        raise TypeError('all circuits should be qiskit.circuit.QuantumCircuit type or qasm')

    job = _submit_task_group(circuits=new_circuit,
                             task_name=task_name,
                             tasktype=tasktype,
                             chip_id=chip_id,
                             shots=shots,
                             circuit_optimize=circuit_optimize,
                             measurement_amend=measurement_amend,
                             auto_mapping=auto_mapping,
                             compile_only=False,
                             specified_block=specified_block,
                             savepath=savepath)
    task_id = job.job_id()

    ret = {'taskid': task_id, 'taskname': task_name}
    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')

    return task_id


def query_all_tasks(savepath=None):
    """Query all locally recorded IBM Quantum tasks and cache results.

    Args:
        savepath (os.PathLike, optional): Directory containing local task
            records.

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
        if not os.path.exists(savepath / '{}.txt'.format(taskid)):
            ret = query_by_taskid(taskid).copy()
            write_taskinfo(taskid, taskinfo=ret, savepath=savepath)
            finished += 1
        else:
            finished += 1
    return finished, task_count

def query_all_task(savepath = None):
    """Deprecated — use :func:`query_all_tasks` instead."""
    warnings.warn(DeprecationWarning("Use query_all_tasks instead"))
    return query_all_tasks(savepath)

if __name__ == '__main__':
    import numpy as np
    from qiskit import QuantumCircuit
    circ = QuantumCircuit(3)
    
    circ.h(0)
    circ.rx(0.4, 0)
    circ.x(0)
    circ.ry(0.39269908169872414, 1)
    circ.y(0)
    circ.rz(np.pi/8, 1)
    circ.z(0)
    circ.cz(0, 1)
    circ.cx(0, 2) 

    circ.sx(0)
    circ.iswap(0, 1)
    circ.cz(0, 2)
    circ.ccx(0, 1, 2)
    x_circuit = QuantumCircuit(2, name='Xs')
    x_circuit.x(range(2))
    xs_gate = x_circuit.to_gate()
    cxs_gate = xs_gate.control()
    circ.append(cxs_gate, [0, 1, 2])
    
    # Create a Quantum Circuit
    meas = QuantumCircuit(3, 3)
    meas.measure(range(3), range(3))
    qc = meas.compose(circ, range(3), front=True)
    QASM_string = qc.qasm()
    print(QASM_string)

    # The quantum circuit in OriginIR
    import qpandalite
    from qpandalite.circuit_builder.qcircuit import Circuit
    c = Circuit()
    c.h(0)
    c.rx(0, np.pi/8)
    c.x(0)
    c.ry(1, np.pi/8)
    c.y(0)
    c.rz(2, np.pi/8)
    c.z(0)
    c.cz(0, 1)
    c.cnot(0, 2) 
    c.rphi(3, np.pi/4, np.pi/3) # phi, theta
    c.measure(0,1,2,3)
    # print(c.circuit)
    print(c.qasm)
    
    import qpandalite.simulator as sim
    qsim = sim.OriginIR_Simulator()

    result = qsim.simulate_pmeasure(c.circuit)

    print(result)
    # The qasm file from previous circuit object in OriginIR
    # now is imported into qiskit using from_qasm_str
    origin_qc = qiskit.QuantumCircuit.from_qasm_str(c.qasm)
    print(origin_qc.qasm())
    # Import Aer
    from qiskit import Aer

    # Run the quantum circuit on a statevector simulator backend
    backend = Aer.get_backend('statevector_simulator')

    # Create a Quantum Program for execution
    job = backend.run(origin_qc)
    result = job.result()
    outputstate = result.get_statevector(origin_qc)
    print(outputstate)
