# VERIFY THE BIT SEQUENCE !!!

from pathlib import Path
from qpandalite.task.originq import *

circuit_1 = \
'''
QINIT 72
CREG 2
H q[59]
X q[60]
MEASURE q[59],c[0]
MEASURE q[60],c[1]
'''.strip()
# Expect result like: {"key":["10","11","00","01"],"value":[413,428,75,84]}
# Ideal result: ["10", "11"] (10+11 means q[59]=c[0]=0+1=key[1], q[60]=c[1]=1=key[0])

circuit_2 = \
'''
QINIT 72
CREG 2
H q[59]
X q[60]
MEASURE q[59],c[1]
MEASURE q[60],c[0]
'''.strip()
# Expect result like: {"key":["01","11","00","10"],"value":[412,403,86,99]}
# Ideal result: ["01", "11"]

circuit_3 = \
'''
QINIT 72
CREG 3
H q[59]
X q[60]
MEASURE q[59],c[2]
MEASURE q[60],c[0]
'''.strip()
# Expect result like: {"key":["01","11","00","10"],"value":[386,409,100,105]}
# Ideal result: ["01", "11"]

circuit_4 = \
'''
QINIT 72
CREG 3
H q[59]
MEASURE q[59],c[2]
MEASURE q[60],c[0]
'''.strip()
# Expect result like: {"key":["00","01","10","11"],"value":[450,485,29,36]}
# Ideal result: ["00", "01"]


if __name__ == '__main__':
    circuits = [circuit_1, circuit_2, circuit_3, circuit_4]
    response = submit_task_group(circuits, 
                                shots=1000, 
                                task_name='Verify', 
                                measurement_amend=False, 
                                circuit_optimize=True,
                                auto_mapping=False,
                                savepath = Path.cwd() / 'origin_online_info_verify')