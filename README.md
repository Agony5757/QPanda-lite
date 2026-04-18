# QPanda-lite

[![GitHub version](https://badge.fury.io/gh/Agony5757%2FQPanda-lite.svg?icon=si%3Agithub)](https://badge.fury.io/gh/Agony5757%2FQPanda-lite)
[![Documentation Status](https://readthedocs.org/projects/qpanda-lite/badge/?version=latest)](https://qpanda-lite.readthedocs.io/zh-cn/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/qpandalite.svg?icon=si%3Apython)](https://badge.fury.io/py/qpandalite)
[![codecov](https://codecov.io/github/Agony5757/QPanda-lite/graph/badge.svg?token=PFQ6F7HQY7)](https://codecov.io/github/Agony5757/QPanda-lite)
[![Build and Test](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml/badge.svg?branch=main)](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml)

**QPanda**: **Q**uantum **P**rogramming **A**rchitecture for **N**ISQ **D**evice **A**pplication

QPanda-lite is a simple, easy-to-use, and transparent Python-native quantum computing framework.

---

## 核心工作流

QPanda-lite 围绕一个简洁的工作流设计：**任意方式构建线路 → CLI 统一执行**。

### 1. 安装

```bash
pip install qpandalite
```

### 2. 构建线路（支持 QPanda-lite 原生或任意第三方工具）

```python
from qpandalite.circuit_builder import Circuit

c = Circuit()
c.h(0)
c.cnot(0, 1)
c.measure(0, 1)

# 输出 OriginIR 格式，可供 CLI 使用
open('circuit.ir', 'w').write(c.originir)
```

> 你也可以使用 Qiskit、Cirq 等工具构建线路，只需最终输出 OriginIR 或 OpenQASM 2.0 格式。

### 3. CLI 统一执行

```bash
# 本地模拟
qpandalite simulate circuit.ir --shots 1000

# 提交到云端
qpandalite submit circuit.ir --platform originq --shots 1000

# 查询任务结果
qpandalite result <task_id>
```

---

## 设计理念

| 线路构建 | 原生 API 或任意工具，输出 OriginIR / QASM2 |
| CLI 执行 | 统一接口：模拟、云端、任务管理 |
| 结果分析 | 原生 Python 结构，易于集成 |

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

- Python 3.10 – 3.13

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

核心依赖（包括 `scipy`）在默认安装中已包含。以下为可选功能依赖：

| 功能 | 安装命令 |
|------|---------|
| OriginQ 云平台 | `pip install pyqpanda3` 或 `pip install qpandalite[originq]` |
| Quafu 执行后端 | `pip install pyquafu` 或 `pip install qpandalite[quafu]` |
| Qiskit 执行后端 | `pip install qiskit qiskit-aer` 或 `pip install qpandalite[qiskit]` |
| 高级模拟 (QuTiP) | `pip install qutip qutip-qip` 或 `pip install qpandalite[simulation]` |
| 可视化 | `pip install matplotlib seaborn pandas` 或 `pip install qpandalite[visualization]` |
| PyTorch 集成 | `pip install torch` 或 `pip install qpandalite[pytorch]` |
| 安装所有可选依赖 | `pip install qpandalite[all]` |

---

## CLI Quick Reference

```bash
# 查看帮助
qpandalite --help

# 本地模拟
qpandalite simulate circuit.ir --shots 1000

# 提交到云端（支持 originq / quafu / ibm / dummy）
qpandalite submit circuit.ir --platform originq --shots 1000

# 查询任务结果
qpandalite result <task_id>

# 配置云平台 Token
qpandalite config init
qpandalite config set originq.token YOUR_TOKEN

# 也可以用 python -m 调用
python -m qpandalite simulate circuit.ir
```

---

## Examples

📁 [examples/](examples/README.md) — Runnable demonstrations

### Getting Started

| Example | Description |
|---------|-------------|
| [Circuit Remapping](examples/getting-started/1_circuit_remap.py) | Build a circuit and remap qubits for real hardware |
| [Dummy Server](examples/getting-started/2_dummy_server.py) | Submit tasks to the local dummy simulator |
| [Result Post-Processing](examples/getting-started/3_result_postprocess.py) | Convert and analyze results |

### Algorithms

| Example | Description |
|---------|-------------|
| [Grover Search](examples/algorithms/grover.md) | Unstructured search with quadratic speedup |
| [Quantum Phase Estimation](examples/algorithms/qpe.md) | Eigenvalue phase estimation |

---

## Documentation

📖 [Read the Docs](https://qpanda-lite.readthedocs.io/)

---

## Status

🚧 Actively developing. API may change.

