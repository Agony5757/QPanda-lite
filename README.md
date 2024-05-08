# QPanda-lite

[![Documentation Status](https://readthedocs.org/projects/qpanda-lite/badge/?version=latest)](https://qpanda-lite.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/qpandalite.svg)](https://badge.fury.io/py/qpandalite)
[![Build and Test](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml/badge.svg?branch=main)](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml)

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
 
 - Python >= 3.8

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
#### With C++ enabled (quantum circuit simulator written in C++, ensure that CMAKE is included in your environment variables.)
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

## Tutorials

There are several ways to use QPanda-lite now.

- Circuit building
- Run circuit on several backends / dummies (classical-simulation backends)
- Circuit simulation

### 1. Circuit build

Refer to [test/demo](test/demo)

```python
from qpandalite import Circuit

c = Circuit()
c.rx(1, 0.1)
c.cnot(1, 0)
measure(0, 1, 2, 3)
print(c.circuit)
```

| Function  | Code sample | Explanation | 
|----------------|--------------|--------------|
| Circuit initialization | c = qpandalite.Circuit() |    
| Qubit/cbit initialization | | No need to specify the number |   
| Gate (like CNOT)    |  c.cnot(1,2)  | Directly use the qubit number |   
| Measure | c.measure(0,1,2)    | Directly use the qubit number (no support mid-circuit measurement) |   
| Remap | c = c.remapping({0:10, 1:11, 2:12}) | Input a python dict to indicate the mapping. It creates a new Circuit object. |
| Output as str | c.circuit / c.originir | Return a python str |

### 2. Circuit run on Quantum Devices / Dummies


| Function  | Code sample | Explanation | 
|----------------|--------------|--------------|
| "Import" the platform | import qpandalite.task.originq as originq  | This importing is independent from "import qpandalite". Available platforms are under qpandalite.task
| Prepare the account |  | See [qcloud_config_template](qcloud_config_template)
| Task submission | taskid = originq.submit_task(circuits)| Circuits is str or List[str]. Returned taskid can be either list or one str, depending on the number of inputting circuits. All returns are native python data structures. See [Circuit build](#circuit-build).|
| Query (synchronously)  |  results = originq.query_by_taskid_sync(taskid) | Inputting the taskid by the return of submit_task. The results are always a list (even if you only submit one circuit). All returns are native python data structures. |
| Query (asynchronously)  | status_and_result = originq.query_by_taskid(taskid)  | Inputting the taskid by the return of submit_task. This will immediately return without waiting. Use status_and_result['status'] to see if the computing is finished; use status_and_result['result'] to view results (the same with Query (synchronously), always being a list). All returns are native python data structures. |
| Handle measurement result | results = originq.convert_originq_result(results, style = 'keyvalue', prob_or_shots = 'prob', key_style = 'bin') | Convert the raw data to a more human-friendly format. Style includes "keyvalue" and "list", prob_or_shots includes "prob" and "shots". When inputting a list, the output is also a list corresponding to all inputs. All returns are native python data structures. |
| Calculate expectation | exps = [calculate_expectation(result, ['ZII', 'IZI', 'IIZ']) for result in results] | Calculate the Z/I expectations accroding to the measurement results. Note that it only accepts the diagonal Hamiltonians. The hamiltonians can be a list, where the output is also a list. However, the input "result" cannot be a list.|

### 2.1 OriginQ
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

### 2.2 Circuit run on Quafu Device 

#### Step 1. Create online config

Refer to [qcloud_config_template/quafu_template.py](qcloud_config_template/quafu_template.py)

- Input the necessary information (token, urls, group_size) to call <font face ='consolas' style="background:#F5F5F5">create_quafu_online_config</font>
- You will have the <font face ='consolas' style="background:#F5F5F5">quafu_online_config.json</font> in your cwd.
- Now you can submit task to the online chip!

#### Step 2. Create the circuit and run

Todo.

### 2.3 Circuit run on IBM Device 

Todo.

### 3. Circuit simulation

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

## Documentation (not finished)

### Readthedocs
[Readthedocs: https://qpanda-lite.readthedocs.io/](https://qpanda-lite.readthedocs.io/)

### Build the docs

The doc is based on 
```bash
cd docs
pip install -r requirements.txt
make html
```
