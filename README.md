# QPanda-lite

[![GitHub version](https://badge.fury.io/gh/Agony5757%2FQPanda-lite.svg?icon=si%3Agithub)](https://badge.fury.io/gh/Agony5757%2FQPanda-lite)
[![Documentation Status](https://readthedocs.org/projects/qpanda-lite/badge/?version=latest)](https://qpanda-lite.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/qpandalite.svg?icon=si%3Apython)](https://badge.fury.io/py/qpandalite)
[![codecov](https://codecov.io/github/Agony5757/QPanda-lite/graph/badge.svg?token=PFQ6F7HQY7)](https://codecov.io/github/Agony5757/QPanda-lite)
[![Build and Test](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml/badge.svg?branch=main)](https://github.com/Agony5757/QPanda-lite/actions/workflows/build_and_test.yml)

**QPanda**: **Q**uantum **P**rogramming **A**rchitecture for **N**ISQ **D**evice **A**pplication

QPanda-lite is a simple, easy-to-use, and transparent Python-native version of QPanda.

## Quick Example

```python
from qpandalite import Circuit
from qpandalite.simulator import OriginIR_Simulator

circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

sim = OriginIR_Simulator()
print(sim.simulate_shots(circuit.originir, shots=1000))
```

## Status

🚧 Actively developing. API may change.

### Known Issues

- **`crx`/`crz`/`cy` bug**：Density matrix 后端的受控旋转门在多门组合时计算结果错误。单门测试正常。如需带噪声模拟，请规避这三个门。
- `controlled_by` simulation for density matrix is incorrect, including `backend='density_operator'` and `backend='density_operator_qutip'`.

---

## Design Principles

- **Transparent** — a clear way to assemble and execute quantum programs
- **Sync & Async** — support both modes for execution on quantum hardware
- **Clear errors** — helpful error messages when things go wrong
- **Well documented** — full, high-quality documentation
- **Visualizable** — visualization of quantum programs
- **Portable** — migrate to different quantum backends
- **Extensible** — support more quantum operations and simulation backends

### Core Concepts

| Concept | Type | Description |
|---------|------|-------------|
| **Opcode** | `Tuple` | A tuple representing a quantum operation: name, qubits, parameters, etc. [📖 Docs](https://qpanda-lite.readthedocs.io/en/latest/source/guide/opcode.html) |
| **Circuit** | `Circuit` | A collection of opcodes representing a quantum program. Can be converted to OriginIR/QASM. [📖 Docs](https://qpanda-lite.readthedocs.io/en/latest/source/guide/build_circuit_simple.html) |
| **Circuit String** | `str` | A string in [OriginIR](https://qpanda-lite.readthedocs.io/en/latest/source/guide/originir_simple.html) or [QASM](https://qpanda-lite.readthedocs.io/en/latest/source/guide/qasm.html) format, ready for backend execution. |
| **Backend** | `Backend` | A [quantum simulator](https://qpanda-lite.readthedocs.io/en/latest/source/guide/simulation_simple.html) or hardware that executes a circuit. |
| **Result** | `dict` / `list` / `ndarray` | Execution results (measurements, states) in native Python data structures. |

---

## Installation

### Supported Platforms

- Windows
- Linux (partially tested)
- macOS (partially tested)

### Requirements

- Python ≥ 3.8

#### Optional Dependencies

| Feature | Install |
|---------|---------|
| **Quafu execution** | `pip install pyquafu` |
| **Qiskit execution** | `pip install qiskit qiskit-ibm-provider qiskit-ibmq-provider` |
| **C++ simulator** | CMake ≥ 3.1, C++ compiler with C++14 support (MSVC / gcc / clang) |

### pip (Recommended)

```bash
pip install qpandalite
```

Python 3.9 – 3.12 supported.

### Build from Source

**Minimum (pure Python):**

```bash
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
pip install . --no-cpp
```

**Development mode:**

```bash
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
pip install -e .
```

**With C++ simulator (requires CMake in PATH):**

```bash
git clone --recurse-submodules https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
pip install .
```

---

### 项目结构

```
QPanda-lite/
├── qpandalite/                  # Python 前端
│   ├── circuit_builder/         # 量子线路构建（Circuit 类）
│   ├── simulator/                # 本地模拟器
│   │   ├── originir_simulator.py    # OriginIR 模拟器
│   │   ├── qasm_simulator.py        # QASM 模拟器
│   │   ├── opcode_simulator.py      # Opcode 底层模拟器
│   │   └── error_model.py           # 噪声模型
│   ├── qasm/                   # OpenQASM 2.0 解析器
│   ├── originir/               # OriginIR 解析器
│   ├── task/                   # 任务提交（OriginQ / Quafu / IBM）
│   ├── transpiler/             # 电路转译（Qiskit / OriginIR 互转）
│   ├── analyzer/               # 结果分析（期望值计算等）
│   └── qcloud_config/          # 各平台云配置
├── docs/                       # Sphinx 文档
├── QPandaLiteCpp/              # C++ 后端（pybind11）
├── test/                       # 单元测试
└── setup.py
```

---

## Quick Start

### 1. Build a Circuit

```python
from qpandalite import Circuit

c = Circuit()
c.rx(1, 0.1)
c.cnot(1, 0)
c.measure(0, 1, 2, 3)
print(c.circuit)
```

| Function | Code | Note |
|----------|------|------|
| Initialize circuit | `c = Circuit()` | No need to specify qubit count |
| Add gate | `c.cnot(1, 2)` | Use qubit indices directly |
| Measure | `c.measure(0, 1, 2)` | No mid-circuit measurement support |
| Remap qubits | `c = c.remapping({0:10, 1:11})` | Returns a new `Circuit` |
| Export to string | `c.circuit` / `c.originir` | Returns `str` |

### 2. Run on Quantum Devices / Simulators

| Function | Code | Note |
|----------|------|------|
| Import platform | `import qpandalite.task.originq as originq` | Platforms are under `qpandalite.task` |
| Submit task | `taskid = originq.submit_task(circuits)` | `circuits`: `str` or `List[str]` |
| Query (sync) | `results = originq.query_by_taskid_sync(taskid)` | Blocks until done; returns `list` |
| Query (async) | `res = originq.query_by_taskid(taskid)` | Returns immediately; check `res['status']` |
| Convert result | `originq.convert_originq_result(results, style='keyvalue', prob_or_shots='prob', key_style='bin')` | Styles: `keyvalue` / `list` |
| Expectation | `calculate_expectation(result, ['ZII', 'IZI', 'IIZ'])` | Diagonal Hamiltonians only |

#### 2.1 OriginQ

1. Create config — see [`qcloud_config_template/originq_template.py`](qcloud_config_template/originq_template.py)
2. Call `create_originq_online_config` with token, URLs, group_size
3. `originq_online_config.json` will be generated in your working directory
4. Submit tasks to the online chip

**Dummy mode** — use `create_originq_dummy_config` to simulate locally without accessing real hardware.

#### 2.2 Quafu

1. Create config — see [`qcloud_config_template/quafu_template.py`](qcloud_config_template/quafu_template.py)
2. Call `create_quafu_online_config` with token, URLs, group_size
3. Submit tasks

#### 2.3 IBM

*Coming soon.*

### 3. Circuit Simulation

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
```

---

## Documentation

📖 **[Read the Docs](https://qpanda-lite.readthedocs.io/)**

### OpenQASM 2.0 Support

[OpenQASM 2.0 Guide](https://qpanda-lite.readthedocs.io/en/latest/source/guide/qasm.html)

### Build Docs Locally

```bash
cd docs
pip install -r requirements.txt
sphinx-apidoc -o docs/source qpandalite
make html
```
