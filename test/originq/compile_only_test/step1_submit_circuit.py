
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

if __name__ == '__main__':
    circuit = circuit_1

    taskid = submit_task_compile_only(
        circuit, 
        circuit_optimize=True,
        auto_mapping=False,
        task_name='CompileOnlyTest', 
        savepath = Path.cwd() / 'origin_online_info_verify')