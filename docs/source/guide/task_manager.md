# 任务管理器 {#guide-task-manager}

## 什么时候进入本页 {#guide-task-manager-when-to-read}

当你需要：
- 统一管理多个量子云平台的任务
- 使用本地缓存保存任务状态和结果
- 批量提交多个量子线路
- 在开发阶段使用本地模拟代替真实云平台

就应该进入本页。

本页介绍的是 **统一任务管理接口**，提供跨平台的一致 API，简化云平台任务的提交、查询和结果管理。

## 概述 {#guide-task-manager-overview}

`task_manager` 模块提供了高层次的 API 来管理量子计算任务：

- **统一接口**：支持 OriginQ、Quafu、IBM Quantum 和本地 Dummy 模拟器
- **本地缓存**：自动保存任务状态和结果，支持离线查询
- **批量操作**：支持批量提交和批量查询
- **Dummy 模式**：开发测试时可使用本地模拟代替真实平台

## 快速开始 {#guide-task-manager-quickstart}

### 安装依赖

```bash
# 基础安装（OriginQ 平台）
pip install qpandalite

# Quafu 平台
pip install qpandalite[quafu]

# IBM Quantum 平台
pip install qpandalite[qiskit]

# 本地模拟（Dummy 模式）
pip install qpandalite[simulation]

# 全部平台
pip install qpandalite[all]
```

### 配置环境变量

```bash
# OriginQ Cloud
export QPANDA_API_KEY="your-api-key"
export QPANDA_SUBMIT_URL="https://..."
export QPANDA_QUERY_URL="https://..."

# Quafu
export QUAFU_API_TOKEN="your-quafu-token"

# IBM Quantum
export IBM_TOKEN="your-ibm-token"
```

### 基本用法

```python
from qpandalite import Circuit
from qpandalite.task_manager import submit_task, wait_for_result

# 创建量子线路
circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

# 提交到云平台
task_id = submit_task(
    circuit.originir,
    backend='originq',
    shots=1000
)

# 等待结果（阻塞直到完成）
result = wait_for_result(task_id, backend='originq', timeout=300)
print(result['counts'])
```

## 核心 API {#guide-task-manager-core-api}

### 任务提交

#### submit_task()

提交单个量子线路到云平台：

```python
from qpandalite.task_manager import submit_task

task_id = submit_task(
    circuit,              # OriginIR 或 QASM 格式的线路字符串
    backend='originq',    # 平台选择：'originq', 'quafu', 'ibm', 'dummy'
    shots=1000,           # 测量次数
    chip_id='...',        # 芯片 ID（平台相关）
    **kwargs              # 其他平台相关参数
)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `circuit` | str | 量子线路（OriginIR 或 QASM 格式） |
| `backend` | str | 平台名称：`'originq'`, `'quafu'`, `'ibm'`, `'dummy'` |
| `shots` | int | 测量次数，默认 1000 |
| `chip_id` | str | 目标芯片 ID（可选） |

#### submit_batch()

批量提交多个量子线路：

```python
from qpandalite.task_manager import submit_batch

task_ids = submit_batch(
    circuits,             # 线路列表
    backend='originq',
    shots=1000
)
```

### 任务查询

#### query_task()

查询单个任务状态：

```python
from qpandalite.task_manager import query_task

info = query_task(task_id, backend='originq')
print(info['status'])  # 'running', 'success', 'failed'
```

#### wait_for_result()

阻塞等待任务完成并返回结果：

```python
from qpandalite.task_manager import wait_for_result

result = wait_for_result(
    task_id,
    backend='originq',
    timeout=300,      # 超时时间（秒）
    interval=5        # 轮询间隔（秒）
)
```

### 任务管理

#### list_tasks()

列出所有缓存的任务：

```python
from qpandalite.task_manager import list_tasks

tasks = list_tasks()
for task in tasks:
    print(f"Task {task['task_id']}: {task['status']}")
```

#### get_task()

获取特定任务的详细信息：

```python
from qpandalite.task_manager import get_task

task_info = get_task(task_id)
```

#### clear_completed_tasks()

清理已完成的任务：

```python
from qpandalite.task_manager import clear_completed_tasks

cleared = clear_completed_tasks()
print(f"Cleared {cleared} tasks")
```

#### clear_cache()

清空所有缓存：

```python
from qpandalite.task_manager import clear_cache

clear_cache()
```

## Dummy 模式 {#guide-task-manager-dummy-mode}

### 环境变量控制

设置 `QPANDALITE_DUMMY` 环境变量可以全局启用本地模拟：

```bash
# 启用 Dummy 模式
export QPANDALITE_DUMMY=true

# 或
export QPANDALITE_DUMMY=1
```

### 检查 Dummy 模式

```python
from qpandalite.task_manager import is_dummy_mode

if is_dummy_mode():
    print("Running in dummy mode - tasks will be simulated locally")
```

### 使用 DummyAdapter

直接使用 `DummyAdapter` 进行本地模拟：

```python
from qpandalite.task.adapters.dummy_adapter import DummyAdapter

adapter = DummyAdapter()

# 支持噪声模拟
adapter_with_noise = DummyAdapter(
    noise_model={'depol': 0.01}  # 1% 去极化噪声
)

# 提交任务
task_id = adapter.submit(circuit, shots=1000)
result = adapter.query(task_id)
```

## 任务持久化 {#guide-task-manager-persistence}

### TaskPersistence 类

使用 `TaskPersistence` 进行更细粒度的任务存储管理：

```python
from qpandalite.task.persistence import TaskPersistence

# 创建持久化实例
persistence = TaskPersistence()

# 保存任务
persistence.save(task_id, {
    'status': 'running',
    'backend': 'originq',
    'circuit': circuit
})

# 加载任务
task = persistence.load(task_id)

# 列出所有任务
all_tasks = persistence.list_all()

# 按平台筛选
originq_tasks = persistence.list_by_platform('originq')

# 列出待处理任务
pending = persistence.list_pending()

# 清理已完成任务
persistence.clear_completed()
```

### 存储位置

任务数据默认存储在 `~/.qpandalite/tasks/` 目录下的 JSONL 文件中。

## 错误处理 {#guide-task-manager-error-handling}

### MissingDependencyError

当缺少平台依赖时抛出：

```python
from qpandalite.task.optional_deps import MissingDependencyError

try:
    from qpandalite.task.adapters.quafu_adapter import QuafuAdapter
    adapter = QuafuAdapter()
except MissingDependencyError as e:
    print(f"Missing dependency: {e.package}")
    print(f"Install with: pip install qpandalite[{e.extra}]")
```

### 任务状态

任务可能有以下状态：

| 状态 | 说明 |
|------|------|
| `pending` | 任务已提交但尚未开始执行 |
| `running` | 任务正在执行中 |
| `success` | 任务成功完成 |
| `failed` | 任务执行失败 |

## 平台对比 {#guide-task-manager-platform-comparison}

| 特性 | OriginQ | Quafu | IBM | Dummy |
|------|---------|-------|-----|-------|
| 输入格式 | OriginIR | QASM | QASM | OriginIR |
| 真机支持 | ✓ | ✓ | ✓ | ✗ |
| 噪声模拟 | ✗ | ✗ | ✗ | ✓ |
| 网络要求 | 需要 | 需要 | 需要 | 不需要 |
| 适用场景 | 生产环境 | BAQIS ScQ 系列 | 国际平台 | 开发测试 |

## 下一步 {#guide-task-manager-next-steps}

- 了解 [云平台适配器架构](../advanced/adapter_architecture.md)
- 查看具体的 [任务提交指南](submit_task.md)
- 参考 API 文档：{mod}`qpandalite.task_manager`
