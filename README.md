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
 - pyquafu (manually install via pip : **pip install pyquafu**)
#### Optional for qiskit execution
 - qiskit (manually install via pip : **pip install qiskit**) and
 - qiskit-ibm-provider (**pip install qiskit-ibm-provider**)

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
python setup.py install
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
python setup.py install --has-cpp
```

### Build the docs
Will be released in the future.

### pip
Will be supported in the future.

## Examples

There are several ways to use QPanda-lite now.

- Circuit building (not supported now)
- Circuit simulation (not supported now)
- Run circuit on several backends

### Circuit run on OriginQ Device 

#### Step 1. Create online config

Refer to [qcloud_config_template/originq_template.py](qcloud_config_template/originq_template.py)

- Input the necessary information (token, urls, group_size) to call <font face ='consolas' style="background:#F5F5F5">create_originq_online_config</font>
- You will have the <font face ='consolas' style="background:#F5F5F5">originq_online_config.json</font> in your cwd.
- Now you can submit task to the online chip!
- (Note: if you fail to submit task, replace the token with the newest in json or this template and rerun.)

#### Step 2. Create the circuit and run

Refer to [test/verify_real_chip_bitsequence_origin](test/verify_real_chip_bitsequence_origin)

- Step 0: Create the online config and import the originq module like this: <font face ='consolas' style="background:#F5F5F5">from qpandalite.task.originq import *</font>
- Step 1.1: Prepare circuits written in OriginIR format (as <font face ='consolas' style="background:#F5F5F5">List[str]</font>)
- Step 1.2: Call <font face ='consolas' style="background:#F5F5F5">submit_task_group</font> and you will find the taskid is recorded to the <font face ='consolas' style="background:#F5F5F5">savepath</font> (Note: the upper limit count for quantum circuits is <font face ='consolas' style="background:#F5F5F5">default_task_group_size</font>)
- Step 2.1: Use <font face ='consolas' style="background:#F5F5F5">load_all_online_info</font> to load all taskids (as well as your taskname)
- Step 2.2: Use <font face ='consolas' style="background:#F5F5F5">query_all_task</font> to fetch the data from the platform. If not finished, it will not be fetched and return without waiting.
- Step 2.3: Use <font face ='consolas' style="background:#F5F5F5">query_by_taskid</font> is also available for fetching a single task result. It will return without waiting if the task is not finished.
- Step 3: Delete / move the online_info(savepath) folder to restore everything.

### Circuit run on Quafu Device 

#### Step 1. Create online config

Refer to [qcloud_config_template/quafu_template.py](qcloud_config_template/quafu_template.py)

- Input the necessary information (token, urls, group_size) to call <font face ='consolas' style="background:#F5F5F5">create_quafu_online_config</font>
- You will have the <font face ='consolas' style="background:#F5F5F5">quafu_online_config.json</font> in your cwd.
- Now you can submit task to the online chip!
#### Step 2. Create the circuit and run

Refer to [test/verify_real_chip_bitsequence_quafu](test/verify_real_chip_bitsequence_quafu)

### Circuit build (unfinished)

Refer to [test/draft_test/circuit_builder_test.py](test/draft_test/circuit_builder_test.py)

```python
from qpandalite import Circuit

c = Circuit('hello')
c.rx(1, angle = 0.1)
print(c)
```

### Circuit simulation (unfinished)

Refer to [test/draft_test/simulator_test.py](test/draft_test/simulator_test.py)

```python
import qpandalite.simulator as qsim

state = qsim.init_n_qubit(5)
print(len(state))

# Expect output: 32
```

#### Note: Have ImportError? <font face ='consolas' style="background:#F5F5F5">ImportError:qpandalite is not install with QPandaLiteCpp</font>. 
You should install with QPandaLiteCpp before importing <font face ='consolas' style="background:#F5F5F5">qpandalite.simulator  </font>

## Documentation
[Readthedocs: https://qpanda-lite.readthedocs.io/](https://qpanda-lite.readthedocs.io/)