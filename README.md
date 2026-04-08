# QPanda-lite

[![GitHub version](https://badge.fury.io/gh/Agony5757%2FQPanda-lite.svg?icon=si%3Agithub)](https://badge.fury.io/gh/Agony5757%2FQPanda-lite)
[![Documentation Status](https://readthedocs.org/projects/qpanda-lite/badge/?version=latest)](https://qpanda-lite.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/qpandalite.svg?icon=si%3Apython)](https://badge.fury.io/py/qpandalite)
[![codecov](https://codecov.io/github/Agony5757/QPanda-lite/graph/badge.svg?token=PFQ6F7HQY7)](https://codecov.io/github/Agony5757/QPanda-lite)
[![Build and Test](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml/badge.svg?branch=main)](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml)

**QPanda**: **Q**uantum **P**rogramming **A**rchitecture for **N**ISQ **D**evice **A**pplication

QPanda-lite is a simple, easy-to-use, and transparent Python-native version of QPanda.

---

## Table of Contents

- [Quick Example](#quick-example)
- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Documentation](#documentation)

---

## Quick Example

```python
from qpandalite.circuit_builder import Circuit
from qpandalite.simulator import OriginIR_Simulator

# Build a Bell state circuit
circuit = Circuit()
circuit.h(0)           # Hadamard on qubit 0
circuit.cnot(0, 1)     # CNOT from qubit 0 to qubit 1
circuit.measure(0, 1)   # Measure both qubits

# Simulate with 1000 shots
sim = OriginIR_Simulator()
result = sim.simulate_shots(circuit.originir, shots=1000)
print(result)
# Possible output: {0: 497, 3: 503}
```

---

## Features

QPanda-lite 围绕以下目标设计：

| 特性 | 说明 |
|------|------|
| **透明** | 清晰的量子程序组装与执行方式 |
| **Python 原生** | 纯 Python 实现，安装简单，集成方便 |
| **多后端** | 支持 OriginIR Simulator、QASM Simulator、Quafu、OriginQ 等多种执行后端 |
| **同步/异步** | 支持同步和异步两种任务提交模式 |
| **可扩展** | 易于添加新的量子门、操作符和模拟后端 |

**核心概念：**

- **Circuit** — 量子线路构建器，支持 OriginIR / OpenQASM 格式输出
- **Backend** — 量子模拟器或真实量子计算机
- **Result** — 测量结果以原生 Python 数据结构返回（dict / list / ndarray）

---

## Installation

### Supported Platforms

- Windows / Linux / macOS

### Requirements

- Python 3.9 – 3.12

### pip（推荐）

```bash
pip install qpandalite
```

### Build from Source

**纯 Python（无 C++ 依赖）：**

```bash
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
pip install . --no-cpp
```

**开发模式：**

```bash
pip install -e .
```

**含 C++ 模拟器（需 CMake）：**

```bash
git clone --recurse-submodules https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
pip install .
```

### Optional Dependencies

| 功能 | 安装命令 |
|------|---------|
| Quafu 执行后端 | `pip install pyquafu` |
| Qiskit 执行后端 | `pip install qiskit qiskit-aer` |

---

## Project Structure

```
QPanda-lite/
├── qpandalite/
│   ├── circuit_builder/          # Circuit class and gate definitions
│   ├── simulator/                # Local simulators (OriginIR, QASM, etc.)
│   ├── originir/                 # OriginIR parser
│   ├── qasm/                    # OpenQASM 2.0 parser
│   ├── task/                    # Cloud task submission (OriginQ / Quafu / IBM)
│   ├── transpiler/              # Circuit conversion (Qiskit ↔ OriginIR)
│   └── analyzer/                # Result analysis (expectation values, etc.)
├── QPandaLiteCpp/               # C++ backend (pybind11)
├── docs/                        # Sphinx documentation
└── test/                       # Unit tests
```

---

## Quick Start

### 1. Build a Circuit

```python
from qpandalite.circuit_builder import Circuit

c = Circuit()
c.rx(1, 0.1)         # RX rotation on qubit 1
c.cnot(1, 0)         # CNOT with control=1, target=0
c.measure(0, 1)      # Measure qubits 0 and 1

print(c.circuit)
# QINIT 2
# CREG 2
# RX q[1], (0.1)
# CNOT q[1], q[0]
# MEASURE q[0], c[0]
# MEASURE q[1], c[1]
```

> 注意：`measure` 只记录被测量的 qubit，电路中实际使用的 qubit 由门操作决定。

### 2. Circuit Simulation

```python
import qpandalite.simulator as qsim

sim = qsim.OriginIR_Simulator(reverse_key=False)

originir = '''
QINIT 72
CREG 3
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

res = sim.simulate_statevector(originir)
print(res)
print(sim.state)
```

### 3. Submit to Cloud Hardware

```python
import qpandalite.task.quafu as quafu

# Configure first: see qcloud_config_template/quafu_template.py
# quafu.create_quafu_online_config(...)

taskid = quafu.submit_task(circuit.originir, chip_id='ScQ-P10')
result = quafu.query_by_taskid_sync(taskid)
```

---

## Documentation

📖 [Read the Docs](https://qpanda-lite.readthedocs.io/)

---

## Status

🚧 Actively developing. API may change.

### Known Issues

- **`crx`/`crz`/`cy` bug**：密度矩阵后端的受控旋转门在多门组合时计算结果错误，单门测试正常。带噪声模拟时请规避这三个门。
- `controlled_by` simulation for density matrix is incorrect (`backend='density_operator'` / `backend='density_operator_qutip'`).
