# VERIFY THE BIT SEQUENCE !!!

from pathlib import Path
from qpandalite.task.quafu import *

circuit_1 = \
'''
QINIT 2
CREG 2
H q[0]
X q[1]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
'''.strip()
# Expect result like: {"key":["10","11","00","01"],"value":[413,428,75,84]}
# Ideal result: ["10", "11"] (10+11 means q[59]=c[0]=0+1=key[1], q[60]=c[1]=1=key[0])

circuit_2 = \
'''
QINIT 2
CREG 2
H q[0]
X q[1]
MEASURE q[0],c[1]
MEASURE q[1],c[0]
'''.strip()
# Expect result like: {"key":["01","11","00","10"],"value":[412,403,86,99]}
# Ideal result: ["01", "11"]

circuit_3 = \
'''
QINIT 2
CREG 3
H q[0]
X q[1]
MEASURE q[0],c[2]
MEASURE q[1],c[0]
'''.strip()
# Expect result like: {"key":["01","11","00","10"],"value":[386,409,100,105]}
# Ideal result: ["01", "11"]

circuit_4 = \
'''
QINIT 2
CREG 3
H q[0]
MEASURE q[0],c[2]
MEASURE q[1],c[0]
'''.strip()
# Expect result like: {"key":["00","01","10","11"],"value":[450,485,29,36]}
# Ideal result: ["00", "01"]


if __name__ == '__main__':
    circuits = [circuit_1, circuit_2, circuit_3, circuit_4]
    for i,circuit in enumerate(circuits):
        taskid = submit_task(circuit, 
                             task_name=f'Verify-{i}',
                             chip_id='ScQ-P136',
                             shots=10000,
                             savepath = Path.cwd() / 'quafu_online_info_verify')
        print(taskid)
