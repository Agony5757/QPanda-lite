
from pathlib import Path
from qpandalite.task.originq import *

circuit_1 = \
'''
QINIT 72
CREG 5
RY q[45],(-2.214297435588181)
RY q[46],(-1.570796)
RZ q[46],(-3.141593)
CZ q[45],q[46]
RY q[46],(-1.0471975511965979)
CZ q[45],q[46]
RY q[46],(-2.0943951023931953)
RZ q[46],(-3.141593)
RY q[52],(-1.570796)
RZ q[52],(-3.141593)
CZ q[46],q[52]
RY q[52],(-0.9553166181245093)
CZ q[46],q[52]
RY q[52],(-2.186276035465284)
RZ q[52],(-3.141593)
RY q[53],(-1.570796)
RZ q[53],(-3.141593)
CZ q[52],q[53]
RY q[53],(-0.7853981633974483)
CZ q[52],q[53]
RY q[53],(-2.356194490192345)
RZ q[53],(-3.141593)
CONTROL q[45]
RY q[46],(-2.0943951023931957)
ENDCONTROL
CONTROL q[46]
RY q[52],(-1.9106332362490186)
ENDCONTROL
CONTROL q[52]
RY q[53],(-1.5707963267948966)
ENDCONTROL
CNOT q[53],q[54]
CNOT q[52],q[53]
CNOT q[46],q[52]
CNOT q[45],q[46]
X q[45]
MEASURE q[45], c[0]
MEASURE q[46], c[1]
MEASURE q[52], c[2]
MEASURE q[53], c[3]
MEASURE q[54], c[4]
'''.strip()

savepath = Path.cwd() / 'online_info'

if __name__ == '__main__':
    taskid = submit_task_compile_only(
        circuit_1,
        circuit_optimize=True,
        auto_mapping=False,
        task_name='CompileOnlyTest', 
        savepath = savepath)
