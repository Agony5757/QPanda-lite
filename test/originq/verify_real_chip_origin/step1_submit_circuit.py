# VERIFY THE BIT SEQUENCE !!!

from pathlib import Path
from qpandalite.task.originq import *

circuit_1 = \
'''
QINIT 72
CREG 6
H q[45]
H q[46]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_2 = \
'''
QINIT 72
CREG 6
H q[45]
H q[46]
H q[52]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_3 = \
'''
QINIT 72
CREG 6
H q[45]
H q[46]
H q[52]
H q[53]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_4 = \
'''
QINIT 72
CREG 6
H q[45]
H q[46]
H q[52]
H q[53]
H q[54]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_5 = \
'''
QINIT 72
CREG 6
H q[45]
H q[46]
H q[52]
H q[53]
H q[54]
H q[48]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_6 = \
'''
QINIT 72
CREG 6
H q[45]
CNOT q[45], q[46]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_7 = \
'''
QINIT 72
CREG 6
H q[45]
CNOT q[45],q[46]
CNOT q[46],q[52]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_8 = \
'''
QINIT 72
CREG 6
H q[45]
CNOT q[45],q[46]
CNOT q[46],q[52]
CNOT q[52],q[53]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_9 = \
'''
QINIT 72
CREG 6
H q[45]
CNOT q[45],q[46]
CNOT q[46],q[52]
CNOT q[52],q[53]
CNOT q[53],q[54]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuit_10 = \
'''
QINIT 72
CREG 6
H q[45]
CNOT q[45],q[46]
CNOT q[46],q[52]
CNOT q[52],q[53]
CNOT q[53],q[54]
CNOT q[54],q[48]
MEASURE q[45],c[0]
MEASURE q[46],c[1]
MEASURE q[52],c[2]
MEASURE q[53],c[3]
MEASURE q[54],c[4]
MEASURE q[48],c[5]
'''.strip()

circuits = [circuit_1, circuit_2, circuit_3, circuit_4, circuit_5, 
            circuit_6, circuit_7, circuit_8, circuit_9, circuit_10]

if __name__ == '__main__':
    
    taskid = submit_task(circuits, 
                        shots=1000, 
                        task_name='Verify', 
                        circuit_optimize=True,
                        auto_mapping=False,
                        savepath = Path.cwd() / 'origin_online_info_verify')
    print(f'taskid: {taskid}')
