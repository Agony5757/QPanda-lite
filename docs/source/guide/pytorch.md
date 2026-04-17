# PyTorch 集成 {#guide-pytorch}

## 什么时候进入本页

当你希望将量子电路集成到 PyTorch 模型中进行混合量子-经典训练时，阅读本页。

## 本页解决的问题

- 如何在 PyTorch 模型中使用参数化量子电路
- 如何通过 parameter-shift 规则计算梯度
- 如何构建量子-经典混合神经网络

## 前置条件

阅读本页前，建议你已经：

- 熟悉 PyTorch 基础用法（`nn.Module`、自动微分、优化器）
- 了解 [参数化电路](circuit.md#guide-circuit-parametric) 的概念
- 了解 [Named Circuit](circuit.md#guide-circuit-named-circuit) 的用法

## 安装

PyTorch 集成是可选功能，需要单独安装：

```bash
pip install qpandalite[pytorch]
```

这会安装 `torch>=2.0` 作为依赖。

## QuantumLayer

`QuantumLayer` 是一个 PyTorch `nn.Module`，用于将参数化量子电路封装为可训练层。

### 基本用法

```python
import torch
from qpandalite.pytorch import QuantumLayer
from qpandalite.circuit_builder import Circuit, Parameter
from qpandalite.simulator import OriginIR_Simulator

# 定义电路模板
def build_circuit(theta_value):
    c = Circuit()
    theta = Parameter("theta")
    theta.bind(theta_value)
    c.rx(0, theta.evaluate())
    c.measure(0)
    return c

# 定义期望值函数
def expectation(circuit):
    sim = OriginIR_Simulator()
    result = sim.simulate(circuit.originir, shots=1000)
    # 计算 <Z> 期望值
    return result.get_expectation([0])

# 创建 QuantumLayer
layer = QuantumLayer(
    circuit_template=build_circuit,
    expectation_fn=expectation,
    param_names=["theta"],
    shift=0.5
)
```

### 在模型中使用

```python
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(10, 4),
    nn.ReLU(),
    layer,  # QuantumLayer
    nn.Linear(1, 1)
)
```

### 训练

```python
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(100):
    optimizer.zero_grad()
    
    # 前向传播
    output = model(torch.randn(1, 10))
    
    # 计算损失
    loss = output.sum()
    
    # 反向传播（自动计算量子梯度）
    loss.backward()
    
    # 更新参数
    optimizer.step()
    
    print(f"Epoch {epoch}: loss = {loss.item():.4f}")
```

## Parameter-Shift 梯度

QuantumLayer 使用 parameter-shift 规则计算量子参数的梯度：

$$\frac{\partial f(\theta)}{\partial \theta} = \frac{f(\theta + s) - f(\theta - s)}{2s}$$

其中 $s$ 是 shift 参数（默认 0.5）。

### 自定义 shift 值

```python
layer = QuantumLayer(
    circuit_template=build_circuit,
    expectation_fn=expectation,
    param_names=["theta"],
    shift=0.25  # 自定义 shift 值
)
```

## 多参数电路

对于有多个参数的电路：

```python
def build_multi_param(params):
    c = Circuit()
    theta = Parameter("theta")
    phi = Parameter("phi")
    theta.bind(params[0])
    phi.bind(params[1])
    c.rx(0, theta.evaluate())
    c.ry(1, phi.evaluate())
    c.cnot(0, 1)
    c.measure(0, 1)
    return c

layer = QuantumLayer(
    circuit_template=build_multi_param,
    expectation_fn=expectation,
    param_names=["theta", "phi"],
    shift=0.5
)
```

## 完整示例：VQE

以下是一个简单的 VQE（变分量子本征求解器）示例：

```python
import torch
import torch.nn as nn
from qpandalite.pytorch import QuantumLayer
from qpandalite.circuit_builder import Circuit, Parameter
from qpandalite.simulator import OriginIR_Simulator
import numpy as np

# 定义哈密顿量 H = Z0 + Z1 + X0X1
def hamiltonian_expectation(circuit):
    sim = OriginIR_Simulator()
    result = sim.simulate(circuit.originir, shots=1000)
    
    # 计算 <Z0 + Z1 + X0X1>
    # 这里简化为只计算 Z0 + Z1
    exp_z0 = result.get_expectation([0])
    exp_z1 = result.get_expectation([1])
    
    return exp_z0 + exp_z1

# 定义 ansatz
def ansatz(params):
    c = Circuit()
    theta = Parameter("theta")
    theta.bind(params[0])
    
    # 初始化
    c.h(0)
    c.h(1)
    
    # 变分层
    c.cnot(0, 1)
    c.rz(1, theta.evaluate())
    
    c.measure(0, 1)
    return c

# 创建量子层
vqe_layer = QuantumLayer(
    circuit_template=ansatz,
    expectation_fn=hamiltonian_expectation,
    param_names=["theta"],
    shift=0.5
)

# 优化
param = torch.tensor([0.1], requires_grad=True)
optimizer = torch.optim.Adam([param], lr=0.1)

for epoch in range(50):
    optimizer.zero_grad()
    
    # 前向传播
    energy = vqe_layer(param)
    
    # 反向传播
    energy.backward()
    
    # 更新参数
    optimizer.step()
    
    print(f"Epoch {epoch}: Energy = {energy.item():.4f}")
```

## 批量执行

当需要并行执行多个电路时，可以使用 `batch_execute` 工具：

```python
from qpandalite.pytorch import batch_execute, batch_execute_with_params
from qpandalite.simulator import OriginIR_Simulator

# 定义执行函数
def simulate(circuit):
    sim = OriginIR_Simulator()
    return sim.simulate(circuit.originir, shots=1000)

# 批量执行多个电路
results = batch_execute(
    circuits=[c1, c2, c3],
    executor=simulate,
    n_workers=4
)

# 对同一模板绑定不同参数后批量执行
param_sets = [{'theta': 0.1}, {'theta': 0.2}, {'theta': 0.3}]
results = batch_execute_with_params(
    circuit_template=parametric_circuit,
    param_values=param_sets,
    executor=simulate,
    n_workers=4
)
```

批量执行使用 `ThreadPoolExecutor` 实现并行，适用于：
- 梯度计算（每个参数需要 2 次电路执行）
- 超参数搜索
- 集成电路评估

## 性能优化建议

1. **减少 shots 数量**：调试时使用较少的 shots，最终训练时再增加。

2. **批量执行**：使用 `batch_execute` 并行化电路评估，充分利用多核 CPU。

3. **缓存中间结果**：对于不变的哈密顿量项，可以预计算并缓存结果。

4. **参数 shift 值**：
   - 默认 $\pi/2$ 适用于大多数旋转门
   - 对于特定门（如 RX、RY），可以根据门特性调整
   - 值过小会放大采样噪声，过大会降低梯度精度

5. **GPU 注意事项**：
   - `QuantumLayer` 的参数存储在 GPU 上（如果可用）
   - 量子电路模拟在 CPU 上执行
   - 数据传输开销可能影响性能，建议批量处理

## 注意事项

1. **期望值函数**：`expectation_fn` 必须返回一个标量值，用于计算梯度。

2. **模拟器开销**：每次梯度计算需要执行 $2n$ 次电路模拟（$n$ 为参数数量），对于复杂电路可能较慢。

3. **数值稳定性**：shift 值的选择会影响梯度计算的精度，通常 0.1 到 0.5 之间效果较好。

4. **GPU 支持**：QuantumLayer 的参数在 GPU 上，但量子计算本身在 CPU 上执行。

## 相关 API

- {mod}`qpandalite.pytorch` — PyTorch 集成模块
- {class}`qpandalite.pytorch.QuantumLayer` — 量子层封装
- {func}`qpandalite.pytorch.parameter_shift_gradient` — Parameter-shift 梯度计算
- {func}`qpandalite.pytorch.batch_execute` — 并行电路执行
- {func}`qpandalite.pytorch.batch_execute_with_params` — 参数化批量执行
- {func}`qpandalite.pytorch.compute_all_gradients` — 计算所有参数梯度

## 下一步

- 了解 [参数化电路](circuit.md#guide-circuit-parametric) 的更多用法
- 学习 [Named Circuit](circuit.md#guide-circuit-named-circuit) 构建复杂电路
- 探索 [算法示例](../algorithm/vqe.md) 中的 VQE 算法
