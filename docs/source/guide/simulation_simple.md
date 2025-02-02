# 本地模拟量子线路

## OpcodeSimulator 文档
`OpcodeSimulator` 是一个多后端的量子电路模拟器，用于在本地计算机上运行量子线路的模拟。它通过一组通用的操作码（opcode）来描述量子线路中的每个模块，并支持多种后端模拟器（如状态向量模拟器和密度矩阵模拟器）。

### 核心功能
`OpcodeSimulator` 提供了以下核心功能：

 - 量子门操作模拟：支持常见的单量子比特门、双量子比特门、三量子比特门以及参数化门的模拟。
 - 错误通道模拟：支持常见的量子错误通道（如比特翻转、相位翻转、去极化噪声等）。
 - 状态向量和密度矩阵模拟：支持基于状态向量和密度矩阵的量子态模拟。
 - 测量操作：支持对量子比特的测量操作，并返回测量结果的概率分布或单次测量结果。
 - 控制结构和 `DAGGER` 操作：支持控制量子比特和 `DAGGER`（共轭转置）操作。

### 后端支持

`OpcodeSimulator` 支持以下后端模拟器：

 - 状态向量模拟器（Statevector Simulator）：
    - 使用状态向量表示量子态。
    - 适用于无噪声的量子线路模拟。

  - 密度矩阵模拟器（Density Operator Simulator）：  
    - 使用密度矩阵表示量子态。
    - 适用于包含噪声和混合态的量子线路模拟。

  - Qutip 密度矩阵模拟器（Density Operator Simulator with Qutip）：
    - 基于 `Qutip` 库的密度矩阵模拟器，支持更复杂的噪声模型。
  

通过 `backend_alias` 函数，用户可以使用别名来指定后端类型。支持的别名包括：

 - 状态向量模拟器：`statevector`, `state_vector`
 - 密度矩阵模拟器：`density_matrix`, `density_operator`, `DensityMatrix`, `DensityOperator`
 - Qutip 密度矩阵模拟器：`density_matrix_qutip`, `density_operator_qutip`

### 方法

#### 初始化

```Python
def __init__(self, backend_type='statevector'):
    '''
    初始化 OpcodeSimulator。

    参数：
    - backend_type: 后端类型，默认为 'statevector'。
                   支持的别名包括 'statevector', 'density_matrix', 'density_matrix_qutip' 等。
    '''
```

#### simulate_opcodes_pmeasure

模拟量子线路并返回测量结果的概率分布。

```python
def simulate_opcodes_pmeasure(self, n_qubit, program_body, measure_qubits):
    '''
    模拟量子线路并返回测量结果的概率分布。

    参数：
    - n_qubit: 量子比特总数。
    - program_body: 量子线路的操作码列表。
    - measure_qubits: 需要测量的量子比特索引列表。

    返回：
    - prob_list: 测量结果的概率分布。
    '''
```

#### simulate_opcodes_statevector

模拟量子线路并返回状态向量。

```python
def simulate_opcodes_statevector(self, n_qubit, program_body):
    '''
    模拟量子线路并返回状态向量。

    参数：
    - n_qubit: 量子比特总数。
    - program_body: 量子线路的操作码列表。

    返回：
    - statevector: 量子态的状态向量。
    '''
```

#### simulate_opcodes_stateprob

模拟量子线路并返回量子态的概率分布。

```python
def simulate_opcodes_stateprob(self, n_qubit, program_body):
    '''
    模拟量子线路并返回量子态的概率分布。

    参数：
    - n_qubit: 量子比特总数。
    - program_body: 量子线路的操作码列表。

    返回：
    - stateprob: 量子态的概率分布。
    '''
```

#### simulate_opcodes_density_operator

模拟量子线路并返回密度矩阵。

```python
def simulate_opcodes_density_operator(self, n_qubit, program_body):
    '''
    模拟量子线路并返回密度矩阵。

    参数：
    - n_qubit: 量子比特总数。
    - program_body: 量子线路的操作码列表。

    返回：
    - density_matrix: 量子态的密度矩阵。
    '''
```

#### simulate_opcodes_shot

模拟量子线路并返回单次测量结果。

```python
def simulate_opcodes_shot(self, n_qubit, program_body, measure_qubits):
    '''
    模拟量子线路并返回单次测量结果。

    参数：
    - n_qubit: 量子比特总数。
    - program_body: 量子线路的操作码列表。
    - measure_qubits: 需要测量的量子比特索引列表。

    返回：
    - shot_result: 单次测量结果。
    '''
```

### 支持的量子门和错误通道
#### 量子门
 - 单量子比特门：H, X, Y, Z, S, SX, T, RX, RY, RZ, U1, U2, U3, RPhi90, RPhi180, RPhi
 - 双量子比特门：CNOT, CZ, SWAP, ISWAP, TOFFOLI, CSWAP, XX, YY, ZZ, XY, PHASE2Q, UU15
 - 三量子比特门：TOFFOLI, CSWAP

#### 错误通道

 - 单量子比特错误通道：PauliError1Q, Depolarizing, BitFlip, PhaseFlip, AmplitudeDamping, Kraus1Q
 - 双量子比特错误通道：PauliError2Q, TwoQubitDepolarizing
  
### 使用示例

以下是一个使用 `OpcodeSimulator` 模拟量子线路并返回测量结果的概率分布的示例：
```python
from OpcodeSimulator import OpcodeSimulator

# 初始化模拟器
simulator = OpcodeSimulator(backend_type='statevector')

# 定义量子线路的操作码
program_body = [
    ('H', 0, None, None, set(), False),  # 在量子比特 0 上应用 Hadamard 门
    ('CNOT', [0, 1], None, None, set(), False),  # 在量子比特 0 和 1 上应用 CNOT 门
    ('MEASURE', 0, 0, None, set(), False)  # 测量量子比特 0，结果存储到经典寄存器 0
]

# 模拟量子线路并返回测量结果的概率分布
n_qubit = 2
measure_qubits = [0]
prob_list = simulator.simulate_opcodes_pmeasure(n_qubit, program_body, measure_qubits)
print("测量结果的概率分布：", prob_list)
```


## BaseSimulator 类文档
`BaseSimulator` 类是一个抽象类，旨在为模拟 OriginIR 或 QASM 格式的量子程序提供一个通用接口。它不直接面向最终用户使用，而是作为 `OriginIR_Simulator` 和 `QASM_Simulator` 等更具体模拟器类的基类。`BaseSimulator` 类依赖于 `OpcodeSimulator` 作为其后端，用于实际模拟量子操作。
### 类定义
```python
class BaseSimulator:
```
### 构造函数
```python
def __init__(self, backend_type='statevector', available_qubits: List[int] = None, available_topology: List[List[int]] = None, **extra_kwargs)
```
- `backend_type`: 要使用的后端模拟器类型，默认为 'statevector'。
- `available_qubits`: 量子设备上可用的量子比特列表。
- `available_topology`: 表示量子设备拓扑的列表。
- `**extra_kwargs`: 用于未来扩展的额外关键字参数。
### 方法
#### 初始化和实用方法
- `def _handle_kwargs(self, kwargs: dict)`: 处理额外的关键字参数。
- `def _clear(self)`: 重置模拟器的状态。
- `def _add_used_qubit(self, qubit)`: 将量子比特添加到已使用的量子比特列表中。
- `def _extract_actual_used_qubits(self)`: 提取程序中实际使用的量子比特。
- `def _check_available_qubits(self)`: 检查使用的量子比特是否在设备上可用。
- `def _check_topology(self, qubit)`: 检查门操作的拓扑是否被设备支持。
#### 模拟预处理
- `def simulate_preprocess(self, originir)`: 对量子程序进行模拟预处理。
#### 模拟执行
- `def simulate_pmeasure(self, quantum_code)`: 模拟量子程序的概率测量。
- `def simulate_statevector(self, quantum_code)`: 模拟并返回量子程序的状态向量。
- `def simulate_stateprob(self, quantum_code)`: 模拟并返回量子程序的状态概率。
- `def simulate_density_matrix(self, quantum_code)`: 模拟并返回量子程序的密度矩阵。
- `def simulate_single_shot(self, quantum_code)`: 模拟量子程序的单次执行。
- `def simulate_shots(self, quantum_code, shots)`: 模拟量子程序的多次执行并返回结果。
#### 属性
- `@property def simulator(self)`: 返回后端模拟器。
- `@property def state(self)`: 返回后端模拟器的当前状态。
- 
## BaseNoisySimulator
`BaseNoisySimulator` 类继承自 `BaseSimulator`，并在模拟过程中添加了噪声行为。它覆盖了多个方法以包括噪声模型和读出错误。
```python
class BaseNoisySimulator(BaseSimulator):
```
### 构造函数
```python
def __init__(self, backend_type='statevector', available_qubits: List[int] = None, available_topology: List[List[int]] = None, error_loader: ErrorLoader = None, readout_error: Dict[int, List[float]]={})
```
- `error_loader`: `ErrorLoader` 实例，用于加载错误模型。
- `readout_error`: 包含每个量子比特读出错误率的字典。
  
### 方法
#### 带噪声的模拟方法
- `def simulate_preprocess(self, originir)`: 使用噪声模型对量子程序进行预处理。
- `def simulate_statevector(self, originir)`: 抛出 `NotImplementedError`，因为带噪声的模拟不支持状态向量。
- `def simulate_density_matrix(self, originir)`: 模拟并返回带有噪声的密度矩阵。
- `def simulate_pmeasure(self, originir)`: 模拟带有噪声的概率测量。
- `def simulate_single_shot(self, originir)`: 模拟带有噪声的单次执行。
- `def simulate_shots(self, quantum_code, shots)`: 模拟带有噪声的多次执行并返回结果。
- 
### 使用
要使用 `BaseSimulator` 或 `BaseNoisySimulator`，需要继承它们并实现必要的方法。直接使用应通过 `OriginIR_Simulator` 或 `QASM_Simulator` 进行，这些类为模拟量子程序提供了更友好的接口。

## OriginIR_Simulator 类

`OriginIR_Simulator` 和 `OriginIR_NoisySimulator` 是两个用于模拟量子程序的类，它们基于 C++ 实现，并在本地 PC 上运行。这两个类都继承自 `BaseSimulator` 类，但 `OriginIR_NoisySimulator` 额外包含了噪声模型的功能。
### 构造函数
```python
def __init__(self, backend_type='statevector', available_qubits=None, available_topology=None, **extra_kwargs)
```
初始化 `OriginIR_Simulator` 实例。
#### 参数
- `backend_type` (str, 可选): 后端类型，默认为 'statevector'。可选值为 'statevector' 或 'densitymatrix'。
- `available_qubits` (List[int], 可选): 可用的量子比特列表，如果需要检查量子比特可用性时使用。默认为 None。
- `available_topology` (List[List[int]], 可选): 可用的量子比特拓扑结构列表，如果需要检查拓扑结构时使用。默认为 None。
- `**extra_kwargs`: 其他可选关键字参数。
### 方法
- `_process_program_body()`: 处理量子程序的主体，将量子操作转换为模拟器可以理解的格式。
- `_clear()`: 清除模拟器的状态，重置为初始状态。
  
## OriginIR_NoisySimulator 类
### 构造函数
```python
def __init__(self, backend_type='statevector', available_qubits=None, available_topology=None, error_loader=None, readout_error={})
```
初始化 `OriginIR_NoisySimulator` 实例。
#### 参数
- `backend_type` (str, 可选): 后端类型，默认为 'statevector'。可选值为 'statevector' 或 'densitymatrix'。
- `available_qubits` (List[int], 可选): 可用的量子比特列表，如果需要检查量子比特可用性时使用。默认为 None。
- `available_topology` (List[List[int]], 可选): 可用的量子比特拓扑结构列表，如果需要检查拓扑结构时使用。默认为 None。
- `error_loader` (ErrorLoader, 可选): 错误加载器实例，用于加载噪声模型。默认为 None。
- `readout_error` (Dict[int, List[float]], 可选): 包含每个量子比特读出错误率的字典。默认为空字典。
### 方法
- `_process_program_body()`: 处理量子程序的主体，将量子操作转换为模拟器可以理解的格式，并考虑噪声模型。
- `_clear()`: 清除模拟器的状态，重置为初始状态。
### 使用说明
这两个类都不是直接用于模拟量子程序的。用户应该通过它们的子类 `OriginIRSimulator` 或 `QASMSimulator` 来进行量子程序的模拟。这些子类提供了更友好的接口，使得用户可以更容易地模拟量子程序。
在使用这些类之前，需要确保量子程序是以 OriginIR 格式编写的，并且已经通过 `OriginIR_BaseParser` 类进行了解析。模拟器将处理解析后的量子程序，并执行模拟操作。如果使用 `OriginIR_NoisySimulator`，还需要确保提供了噪声模型。

## QASM_Simulator 类

`QASM_Simulator` 和 `QASM_Noisy_Simulator` 类是用于模拟 QASM 格式的量子程序的模拟器。`QASM_Simulator` 提供了一个基本的模拟环境，而 `QASM_Noisy_Simulator` 在此基础上增加了噪声模型的支持。
这两个类都继承自 `BaseSimulator` 和 `BaseNoisySimulator` 类，并使用 `OpenQASM2_BaseParser` 来解析 QASM 代码。

### 构造函数
```python
def __init__(self, backend_type='statevector', available_qubits=None, available_topology=None, least_qubit_remapping=False, **extra_kwargs)
```
初始化 `QASM_Simulator` 实例。
#### 参数
- `backend_type` (str, 可选): 后端类型，默认为 'statevector'。可选值为 'statevector' 或 'densitymatrix'。
- `available_qubits` (List[int], 可选): 可用的量子比特列表。默认为 None。
- `available_topology` (List[List[int]], 可选): 可用的量子比特拓扑结构列表。默认为 None。
- `least_qubit_remapping` (bool, 可选): 是否启用最小量子比特重映射，默认为 False。
- `**extra_kwargs`: 其他可选关键字参数。
### 方法
- `_clear()`: 清除模拟器的状态，重置为初始状态。包括量子比特数量、测量量子比特列表、解析器和操作码模拟器。
## QASM_Noisy_Simulator 类
### 构造函数
```python
def __init__(self, backend_type='statevector', available_qubits=None, available_topology=None, error_loader=None, readout_error={})
```
初始化 `QASM_Noisy_Simulator` 实例。
#### 参数
- `backend_type` (str, 可选): 后端类型，默认为 'statevector'。可选值为 'statevector' 或 'densitymatrix'。
- `available_qubits` (List[int], 可选): 可用的量子比特列表。默认为 None。
- `available_topology` (List[List[int]], 可选): 可用的量子比特拓扑结构列表。默认为 None。
- `error_loader` (ErrorLoader, 可选): 错误加载器实例，用于加载噪声模型。默认为 None。
- `readout_error` (Dict[int, List[float]], 可选): 包含每个量子比特读出错误率的字典。默认为空字典。
### 方法
- `_clear()`: 清除模拟器的状态，重置为初始状态。包括量子比特数量、测量量子比特列表、解析器和操作码模拟器。
### 使用说明
这两个类用于模拟 QASM 格式的量子程序。用户应该通过这些类来执行量子程序的模拟，而不是直接使用它们。以下是如何使用这些类的示例：
```python
# 初始化 QASM_Simulator
simulator = QASM_Simulator(backend_type='statevector')
# 加载 QASM 程序
qasm_program = '...'
# 解析 QASM 程序
parsed_program = simulator.parser.load(qasm_program)
# 执行模拟
result = simulator.simulate(parsed_program)
# 对于噪声模拟器
noisy_simulator = QASM_Noisy_Simulator(backend_type='statevector', error_loader=error_loader)
# 执行带噪声的模拟
noisy_result = noisy_simulator.simulate(parsed_program)
```
请注意，上述代码中的 `simulate` 方法需要根据实际的类实现来定义，这里只是提供了一个使用示例。在实际使用中，可能还需要其他步骤，如配置噪声模型或处理模拟结果。
