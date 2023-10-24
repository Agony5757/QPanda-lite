import json
import os
from pathlib import Path
import warnings
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


if __name__ == '__main__':
    import numpy as np
    from qiskit import QuantumCircuit
    
    The quantum circuit in qiskit
    # circ = QuantumCircuit(3)
    
    # circ.h(0)
    # circ.rx(0.4, 0)
    # circ.x(0)
    # circ.ry(0.39269908169872414, 1)
    # circ.y(0)
    # circ.rz(np.pi/8, 1)
    # circ.z(0)
    # circ.cz(0, 1)
    # circ.cx(0, 2) 

    # circ.sx(0)
    # circ.iswap(0, 1)
    # circ.cz(0, 2)
    # circ.ccx(0, 1, 2)
    # x_circuit = QuantumCircuit(2, name='Xs')
    # x_circuit.x(range(2))
    # xs_gate = x_circuit.to_gate()
    # cxs_gate = xs_gate.control()
    # circ.append(cxs_gate, [0, 1, 2])
    
    # # Create a Quantum Circuit
    # meas = QuantumCircuit(3, 3)
    # meas.measure(range(3), range(3))
    # qc = meas.compose(circ, range(3), front=True)
    # QASM_string = qc.qasm()
    # print(QASM_string)

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

    result = qsim.simulate(c.circuit)

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
