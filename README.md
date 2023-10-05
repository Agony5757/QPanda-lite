# QPanda-lite

[![Documentation Status](https://readthedocs.org/projects/qpanda-lite/badge/?version=latest)](https://qpanda-lite.readthedocs.io/en/latest/?badge=latest)
      
QPanda: **Q**uantum **P**rogramming **A**rchitecture for **N**ISQ **D**evice **A**pplication

QPanda-lite *should be* a simple, easy, and transparent python-native version for QPanda.

## Status
Developing. Unstable.

## Design principles

- A clear, and tranparent way to assemble/execute a quantum program
- Support sync/async modes for execution on a quantum hardware
- Clear error hints
- Full, and better documentations
- Visualization of the quantum program
- Be able to migrate to different quantum backends

## Install

### OS
- Windows 
- Linux (not fully tested)
- MacOS (not fully tested)

### Requirements
 
 - Python >= 3.7

#### Optional for quafu execution
manually install via pip : 
 - pyquafu (**pip install pyquafu**)
#### Optional for qiskit execution
manually install via pip : 
 - qiskit (**pip install qiskit**) and
 - qiskit-ibm-provider (**pip install qiskit-ibm-provider**) and
 - qiskit-ibmq-provider (**pip install qiskit-ibmq-provider**)

#### Optional for C++ simulator
 - CMake >= 3.1
 - C++ compiler (with C++ 14 support), including MSVC, gcc, clang, etc...


### Build from source

#### A minimum version
```bash
# Clone the code
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite

# install
python setup.py install --no-cpp
```

#### For development
```
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite

# install
python setup.py develop
```
#### With C++ enabled (quantum circuit simulator written in C++)
```
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite

# install
python setup.py install
```

### Build the docs
Will be released in the future.

### pip

For python 3.8 to 3.10
```
pip install qpandalite
```

## Examples

There are several ways to use QPanda-lite now.

- Circuit building (not supported now)
- Circuit simulation (not supported now)
- Run circuit on several backends

### Circuit run on OriginQ Device 

#### Step 1. Create online config

Refer to [qcloud_config_template/originq_template.py](qcloud_config_template/originq_template.py)

- Input the necessary information (token, urls, group_size) to call <font face ='consolas' style="background:#F5F5F5">create_originq_online_config</font>
- You will have the <font face ='consolas' style="background:#F5F5F5">originq_online_config.json</font> in your current working directory (cwd).
- Now you can submit task to the online chip!

#### Step 1.1 (Optional). Use originq_dummy

Dummy server is used to emulate the behavior of an online-avaiable quantum computing server, without really accessing the system but with your local computer to simulate the quantum circuit.

- Input the necessary information (available_qubits and available_topology) to call <font face ='consolas' style="background:#F5F5F5">create_originq_dummy_config</font>.

- If you want both mode, use <font face ='consolas' style="background:#F5F5F5">create_originq_config</font> and inputting all needed information.

#### Step 2. Create the circuits and run

Refer to [test/demo](test/demo)

### Circuit run on Quafu Device 

#### Step 1. Create online config

Refer to [qcloud_config_template/quafu_template.py](qcloud_config_template/quafu_template.py)

- Input the necessary information (token, urls, group_size) to call <font face ='consolas' style="background:#F5F5F5">create_quafu_online_config</font>
- You will have the <font face ='consolas' style="background:#F5F5F5">quafu_online_config.json</font> in your cwd.
- Now you can submit task to the online chip!

#### Step 2. Create the circuit and run

Todo.

### Circuit build

Refer to [test/demo](test/demo)

```python
from qpandalite import Circuit

c = Circuit()
c.rx(1, 0.1)
print(c.circuit)
```

### Circuit simulation

Refer to [test/draft_test/originir_simulator_test.py](test/draft_test/originir_simulator_test.py)

```python

import qpandalite.simulator as qsim

sim = qsim.OriginIR_Simulator(reverse_key=False)

originir = '''
QINIT 72
CREG 2
RY q[45],(0.9424777960769379)
RY q[46],(0.9424777960769379)
CZ q[45],q[46]
RY q[45],(-0.25521154)
RY q[46],(0.26327053)
X q[46]
MEASURE q[45],c[0]
MEASURE q[46],c[2]
MEASURE q[52],c[1]
'''

res = sim.simulate(originir)
print(res)
print(sim.state)

# Expect output: 
# [0.23218757036469517, 0.04592184582945769, 0.0, 0.0, 0.6122094271102275, 0.10968115669561962, 0.0, 0.0]
# [(0.4818584546987789+0j), (-0.21429383059121812+0j), (0.7824381298928546+0j), (0.33118145584500897+0j), 0j, 0j, 0j, 0j]
```

#### Note: Have ImportError? <font face ='consolas' style="background:#F5F5F5">ImportError:qpandalite is not install with QPandaLiteCpp</font>. 
You should install with QPandaLiteCpp before importing <font face ='consolas' style="background:#F5F5F5">qpandalite.simulator  </font>

## Documentation
[Readthedocs: https://qpanda-lite.readthedocs.io/](https://qpanda-lite.readthedocs.io/)