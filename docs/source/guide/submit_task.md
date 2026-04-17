# 提交任务到量子云平台 {#guide-submit-task}

## 什么时候进入本页 {#guide-submit-task-when-to-read}

当你已经完成本地线路构建，并且已经通过 [快速上手](quickstart.md) 或 [本地模拟](simulation.md) 跑通了最小示例，接下来如果你希望：

- 把线路提交到云平台或真机执行
- 查询远端任务状态与执行结果
- 比较不同平台的接入方式与适用场景

就应该进入本页。

本页讨论的是**远端任务提交路径**，它解决的是"如何把已经在本地验证过的线路交给外部平台执行"的问题，而不是"如何在本地验证线路是否正确"。

## 本页解决的问题 {#guide-submit-task-problems}

- 什么时候应从本地模拟切换到提交任务路径
- 提交到云平台前需要准备哪些配置
- 不同平台各自适合什么场景
- 如何提交任务、查询状态并获取结果
- 使用远端平台前需要先了解哪些边界与限制

## 前置条件

阅读本页前，默认你已经完成以下至少一项：

- 已经完成 [快速上手](quickstart.md) 中的最小示例
- 已经会使用 `Circuit` 构建线路，并能导出 `originir` 或 `qasm`
- 已经通过 [本地模拟](simulation.md) 对线路做过基本验证

如果你还不确定线路是否正确、输出是否合理，建议先留在本地模拟路径，不要直接进入远端提交。

## 通用流程 {#guide-submit-task-flow}

无论选择哪个平台，远端任务提交通常都遵循以下流程：

1. **准备线路** —— 确认你已经有可提交的 `Circuit` 对象
2. **选择平台** —— 根据目标平台、依赖、成熟度与接入条件决定使用哪个后端
3. **准备配置** —— 通过环境变量配置 Token
4. **提交任务** —— 调用 `submit_task()` 提交任务
5. **查询结果** —— 通过 `wait_for_result()` 或 `query_task()` 获取结果

与本地模拟相比，这条路径多出了平台账号、环境变量配置、网络访问、任务排队与远端状态查询等因素。

## 统一云平台接口 {#guide-submit-task-unified-api}

QPanda-lite 提供统一的云平台接入层，通过一致的接口操作 OriginQ、Quafu 和 IBM 三大平台。

### 配置方式

推荐使用环境变量配置：

```bash
# OriginQ Cloud 配置
export QPANDA_API_KEY="your-originq-token"
export QPANDA_SUBMIT_URL="https://..."
export QPANDA_QUERY_URL="https://..."

# Quafu 配置
export QUAFU_API_TOKEN="your-quafu-token"

# IBM Quantum 配置
export IBM_TOKEN="your-ibm-token"
```

或者使用 YAML 配置文件 `~/.qpandalite/qpandalite.yml`：

```yaml
default:
  originq:
    token: "your-originq-token"
    submit_url: "https://..."
    query_url: "https://..."
  quafu:
    token: "your-quafu-token"
  ibm:
    token: "your-ibm-token"
    proxy:
      http: "http://proxy:8080"
      https: "https://proxy:8080"
```

### 基本用法

```python
from qpandalite import Circuit, submit_task, wait_for_result, query_task

# 1. 创建电路
circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

# 2. 提交任务
task_id = submit_task(circuit, backend='originq', shots=1000)
print(f"Task ID: {task_id}")

# 3. 等待结果
result = wait_for_result(task_id, backend='originq', timeout=300)
print(f"Counts: {result['counts']}")
print(f"Probabilities: {result['probabilities']}")

# 4. 查询任务状态
info = query_task(task_id, backend='originq')
print(info.status)  # 'running', 'success', 'failed'
```

### 平台选择

切换不同平台只需更改 `backend` 参数：

```python
# OriginQ Cloud
task_id = submit_task(circuit, backend='originq', shots=1000)

# Quafu（需要 pip install qpandalite[quafu]）
task_id = submit_task(circuit, backend='quafu', shots=1000, chip_id='ScQ-P10')

# IBM Quantum（需要 pip install qpandalite[qiskit]）
task_id = submit_task(circuit, backend='ibm', shots=1000)
```

### 任务管理

```python
from qpandalite import list_tasks, get_task, clear_completed_tasks, clear_cache

# 查看所有缓存的任务
tasks = list_tasks()
for task in tasks:
    print(f"{task.task_id}: {task.status}")

# 获取特定任务信息
task_info = get_task(task_id)

# 清理已完成的任务
cleared = clear_completed_tasks()
print(f"Cleared {cleared} tasks")

# 清空所有缓存
clear_cache()
```

### 后端信息

```python
from qpandalite import backend

# 列出所有可用后端
backends = backend.list_backends()
for name, info in backends.items():
    print(f"{name}: available={info['available']}")

# 获取特定后端实例
originq_backend = backend.get_backend('originq')
print(f"OriginQ available: {originq_backend.is_available()}")
```

## Dummy 模式（本地模拟） {#guide-submit-task-dummy}

Dummy 模式允许在不连接真实云平台的情况下测试任务提交流程。

### 启用方式

```bash
# 方式一：环境变量
export QPANDALITE_DUMMY=true
```

```python
# 方式二：代码中设置
import os
os.environ['QPANDALITE_DUMMY'] = 'true'

from qpandalite import submit_task, wait_for_result

# 现在所有提交都会使用本地模拟
task_id = submit_task(circuit, backend='originq', shots=1000)
result = wait_for_result(task_id)
```

```python
# 方式三：单次提交使用 dummy 参数
task_id = submit_task(circuit, backend='originq', dummy=True)
```

### Dummy 模式适用场景

- 开发阶段验证提交/查询调用链路
- 本地测试任务提交流程
- 在不具备真实平台访问条件时完成联调

## 批量提交

```python
from qpandalite import submit_batch

# 构建多个电路
circuits = []
for i in range(10):
    c = Circuit()
    c.h(0)
    c.rx(1, i * 0.1)
    c.cnot(0, 1)
    c.measure(0, 1)
    circuits.append(c)

# 批量提交
task_ids = submit_batch(circuits, backend='originq', shots=1000)
print(f"Submitted {len(task_ids)} tasks")
```

## 结果处理

### UnifiedResult 类型

任务结果统一为 `UnifiedResult` 格式：

```python
from qpandalite import UnifiedResult

result = wait_for_result(task_id, backend='originq')

# 访问测量结果
print(result['counts'])         # {'00': 512, '11': 488}
print(result['probabilities'])  # {'00': 0.512, '11': 0.488}

# 计算期望值
from qpandalite import calculate_expectation
exp_zz = calculate_expectation(result['probabilities'], 'ZZ')
print(f"<ZZ> = {exp_zz}")
```

### 平台特定后端参数

```python
# Quafu: 指定芯片
task_id = submit_task(circuit, backend='quafu', chip_id='ScQ-P10', auto_mapping=True)

# OriginQ: 指定芯片和优化选项
task_id = submit_task(circuit, backend='originq', chip_id='...', circuit_optimize=True)
```

## 平台选择说明 {#guide-submit-task-platform-selection}

| 平台 | 定位 | 适用场景 | 额外依赖 |
|------|------|---------|---------|
| OriginQ Cloud | 主生产路径 | 生产环境、真实量子计算 | 无额外依赖 |
| Quafu | 第三方云平台 | BAQIS ScQ 系列 | `pip install qpandalite[quafu]` |
| IBM Quantum | 第三方云平台 | IBM Quantum 生态 | `pip install qpandalite[qiskit]` |
| Dummy | 本地模拟 | 开发测试、联调 | `pip install qpandalite[simulation]` |

## 平台边界与限制

在进入远端提交路径前，建议先确认以下几点：

- **本地模拟 != 远端提交**：本地模拟解决的是线路验证问题；远端提交解决的是平台接入与任务执行问题。
- **配置是前置条件**：不同平台需要配置相应的环境变量。
- **网络与账号会影响可用性**：远端平台可能受网络环境、认证状态、平台可用性和排队情况影响。
- **额外依赖**：Quafu 和 IBM 需要安装额外的依赖包。

如果你还在反复修改线路结构、量子门或输出解释，说明你仍处于本地验证阶段，建议先回到 [本地模拟](simulation.md)。

## 下一步与参考

- 如果你还没有完成线路验证，先回到 [本地模拟](simulation.md)
- 如果你还不清楚线路如何构建，先阅读 [构建量子线路](circuit.md)
- API 参考：
  - {mod}`qpandalite.task_manager`
  - {mod}`qpandalite.backend`
  - {mod}`qpandalite.task.adapters`
  - {mod}`qpandalite.task.normalizers`
