# QPanda-lite

QPanda: **Q**uantum **P**rogramming **A**rchitecture for **N**ISQ **D**evice **A**pplication

QPanda-lite *should be* a simple, easy, and transparent python-native version for QPanda.

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

#### Optional for C++ simulator
 - CMake >= 3.1
 - C++ compiler (with C++ 14 support), including MSVC, gcc, clang, etc...


### Build from source

```
git clone https://github.com/Agony5757/QPanda-lite.git
python setup.py
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

Refer to [qcloud_config_template/make_originq_online_config.py](qcloud_config_template/make_originq_online_config.py)

#### Step 2. Create the circuit and run

Refer to [test/verify_real_chip_bitsequence_origin](test/verify_real_chip_bitsequence_origin)

### Circuit run on Quafu Device 

#### Step 1. Create online config

Refer to [qcloud_config_template/make_quafu_online_config.py](qcloud_config_template/make_quafu_online_config.py)

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
- Note: Have ImportError? (ImportError:qpandalite is not install with QPandaLiteCpp): You should install with QPandaLiteCpp before importing qpandalite.simulator  

## Documentation
Stay tuned.