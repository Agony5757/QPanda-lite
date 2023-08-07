# QPanda-lite

QPanda: **Q**uantum **P**rogramming **A**rchitecture for **N**ISQ **D**evice **A**pplication

QPanda-lite *should be* a simple, easy, and transparent python-native version for QPanda.

## Install

### OS
- Windows 
- Linux (not fully tested)
- MacOS (not fully tested)

### Requirements
 
 - python >= 3.7
 - CMake >= 3.1
 - C++ compiler (with C++ 14 support), including MSVC, gcc, clang, etc...


### Build from source

```
git clone https://github.com/Agony5757/QPanda-lite.git
python setup.py
```

### pip
Not supported yet.

## Usage

```python
import qpandalite

state = qpandalite.init_n_qubit(5)
print(len(state))
```

Expected output:
```
32
```

## Documentation
Stay tuned.