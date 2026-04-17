# 提交任务到量子云平台 {#guide-submit-task}

## 什么时候进入本页 {#guide-submit-task-when-to-read}

当你已经完成本地线路构建，并且已经通过 [快速上手](quickstart.md) 或 [本地模拟](simulation.md) 跑通了最小示例，接下来如果你希望：

- 把线路提交到云平台或真机执行
- 查询远端任务状态与执行结果
- 比较不同平台的接入方式与适用场景

就应该进入本页。

本页讨论的是**远端任务提交路径**，它解决的是“如何把已经在本地验证过的线路交给外部平台执行”的问题，而不是“如何在本地验证线路是否正确”。

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

1. **准备线路** —— 确认你已经有可提交的 `originir` 或 `qasm` 线路
2. **选择平台** —— 根据目标平台、依赖、成熟度与接入条件决定使用哪条路径
3. **准备配置** —— 配置 Token、URL 或账号信息
4. **提交任务** —— 调用对应平台的 `submit_task`
5. **查询结果** —— 通过任务 ID 查询执行状态与结果

与本地模拟相比，这条路径多出了平台账号、配置文件、网络访问、任务排队与远端状态查询等因素。

## 提交任务入口总览 {#guide-submit-task-entry-overview}

在 QPanda-lite 中，“提交任务”指的是**把已经完成本地验证的线路交给外部平台执行，并通过任务 ID 查询远端状态与结果**。进入本页前，建议先区分它与“本地模拟”的边界：

- 本地模拟：在当前环境直接运行线路，重点是验证线路是否正确，以及如何选择本地模拟后端。
- 提交任务：把线路交给云平台或真机执行，重点是平台配置、任务提交、状态查询与结果获取。

如果你仍在反复修改线路结构、量子门或输出解释，说明你还处在本地验证阶段，建议先回到 [本地模拟](simulation.md#guide-simulation-entry-overview)。

## 统一云平台接口（推荐方式） {#guide-submit-task-unified-api}

PR#182 引入了统一的云平台接入层，提供了一致的接口来操作 OriginQ、Quafu 和 IBM 三大平台。这是推荐的使用方式。

### 配置文件

统一接口使用 YAML 配置文件，位于 `~/.qpandalite/qpandalite.yml`：

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
import qpandalite
from qpandalite import Circuit

# 1. 获取 Backend
backend = qpandalite.get_backend('originq')  # 或 'quafu', 'ibm'
available = qpandalite.list_backends()

# 2. 创建电路
circuit = Circuit()
circuit.h(0)
circuit.cnot(0, 1)
circuit.measure(0, 1)

# 3. 提交任务
task_id = qpandalite.submit_task(circuit, backend='originq', shots=1000)

# 4. 等待结果
result = qpandalite.wait_for_result(task_id, backend='originq', timeout=300)

# 5. 查询任务状态
info = qpandalite.query_task(task_id, backend='originq')
print(info['status'])  # 'running', 'success', 'failed'
```

### 任务管理

```python
# 查看所有缓存的任务
tasks = qpandalite.list_tasks()

# 获取特定任务信息
task_info = qpandalite.get_task(task_id)

# 清理已完成的任务
qpandalite.clear_completed_tasks()

# 清空所有缓存
qpandalite.clear_cache()
```

### 统一接口 vs 平台特定接口

| 特性 | 统一接口（推荐） | 平台特定接口 |
|------|-----------------|-------------|
| 配置方式 | YAML 配置文件 | JSON 配置文件 |
| 平台切换 | 只需更改 backend 参数 | 需要导入不同模块 |
| 任务管理 | 内置本地缓存 | 无统一缓存 |
| 适用场景 | 生产环境、多平台开发 | 单平台开发 |

如果你只需要使用单一平台，或者需要使用平台特有的功能，可以继续使用下文介绍的平台特定接口。

## 平台选择说明 {#guide-submit-task-platform-selection}

在阅读具体平台小节前，建议先按“定位 / 适用场景 / 当前状态”理解几条路径的区别：

| 平台 | 定位 | 适用场景 | 额外依赖 / 配置 | 当前状态 |
|------|------|---------|----------------|---------|
| OriginQ Cloud | 主生产路径 | 已完成本地验证，准备提交到真实云平台或真机 | `originq_cloud_config.json` | 推荐优先阅读 |
| OriginQ Dummy | 本地联调替身 | 想复用提交接口做开发、测试、联调，但不消耗真实量子资源 | 可选读取 `originq_online_config.json` | 推荐作为联调路径 |
| Quafu | 第三方云平台路径 | 需要接入 Quafu 平台执行 | `pip install quafu` + `quafu_online_config.json` | 可用，但为独立平台接入 |
| IBM Quantum | 第三方云平台路径 | 需要接入 IBM Quantum 生态 | `pip install qiskit qiskit-ibm-provider` + `ibm_online_config.json` | 可用，但接入方式独立 |
| Legacy OriginQ (`qpandalite.task.originq`) | 旧接口说明 | 仅用于理解旧接口背景，不建议新用户进入 | 旧版配置 | 当前版本不可用 |

如果你只是想验证“提交任务”这一套调用流程本身是否跑通，优先看 OriginQ Dummy；如果你要真正把任务发到云端执行，优先看 OriginQ Cloud。

## 平台分节

### OriginQ Cloud {#guide-submit-task-originq-cloud}

这是当前应优先引导的真实云平台提交路径，适合已经完成本地验证、准备把线路提交到真实云端或真机执行的读者。

#### 配置

OriginQ Cloud 依赖当前工作目录下的 `originq_cloud_config.json`。可参考模板：

- `qcloud_config_template/originq_cloud_template.py`

#### 提交任务

```python
from qpandalite.task.origin_qcloud import submit_task

task_id = submit_task(
    circuit=circuit.originir,
    shots=1000
)
```

#### 查询结果

```python
from qpandalite.task.origin_qcloud import query_by_taskid

result = query_by_taskid(task_id)
print(result)
```

### OriginQ Dummy {#guide-submit-task-originq-dummy}

这是本地联调与测试路径，接口风格与远端提交相近，但不会真正连接真实量子平台，也不会消耗真实量子资源。

它适合：
- 在开发阶段验证提交 / 查询调用链路
- 本地测试任务提交流程
- 在暂时不具备真实平台访问条件时先完成联调

#### 使用 DummyAdapter

推荐使用新的 `DummyAdapter`，它提供了与其他云平台适配器一致的接口：

```python
from qpandalite.task.adapters.dummy_adapter import DummyAdapter

# 创建适配器（需要安装 qutip: pip install qpandalite[simulation]）
adapter = DummyAdapter()

# 提交任务
circuit = '''QINIT 2
CREG 2
H q[0]
CNOT q[0] q[1]
MEASURE q[0], c[0]
MEASURE q[1], c[1]'''
task_id = adapter.submit(circuit, shots=1000)

# 查询结果
result = adapter.query(task_id)
print(result['status'])  # 'success'
print(result['result']['counts'])
```

#### 全局 Dummy 模式

设置环境变量 `QPANDALITE_DUMMY=true` 可以启用全局 dummy 模式：

```bash
export QPANDALITE_DUMMY=true
```

在此模式下，所有任务提交都会自动使用本地模拟，无需真实云平台连接。

#### 旧版接口

```python
from qpandalite.task.originq_dummy import submit_task

result = submit_task(
    circuit=circuit.originir,
    shots=1000
)
```

### Quafu {#guide-submit-task-quafu}

这是独立的第三方云平台接入路径，适合已经确认要接入 Quafu 平台，并已准备好对应依赖与平台 Token 的读者。

#### 配置

- 需要额外安装依赖：`pip install quafu`
- 需要准备 `quafu_online_config.json`
- 可参考模板：`qcloud_config_template/quafu_template.py`

#### 提交任务

```python
from qpandalite.task.quafu import submit_task

task_id = submit_task(
    circuit=circuit.qasm,
    shots=1000
)
```

### IBM Quantum {#guide-submit-task-ibm}

这是 IBM Quantum 的独立接入路径，适合明确要使用 IBM 生态、并接受其依赖与账号体系的读者。

#### 配置

- 需要额外安装依赖：`pip install qiskit qiskit-ibm-provider`
- 需要准备 `ibm_online_config.json`
- 可参考模板：`qcloud_config_template/ibm_template.py`

#### 提交任务

```python
from qpandalite.task.ibm import submit_task

task_id = submit_task(
    circuit=circuit.qasm,
    shots=1000
)
```

### Legacy OriginQ（`qpandalite.task.originq`） {#guide-submit-task-legacy-originq}

这是旧的 OriginQ 接口说明。根据当前代码实现，`qpandalite.task.originq` 在当前版本中不可用，并在导入时直接提示应改用 `qpandalite.task.origin_qcloud`。

因此：
- 不应把它作为新用户入口
- 不应在平台主路径里与 OriginQ Cloud 并列推荐
- 仅在需要理解历史接口变化时再提及

## 平台边界与限制

在进入远端提交路径前，建议先确认以下几点：

- **本地模拟 != 远端提交**：本地模拟解决的是线路验证问题；远端提交解决的是平台接入与任务执行问题。
- **配置文件是前置条件**：不同平台依赖不同的 JSON 配置文件或账号保存机制。
- **网络与账号会影响可用性**：远端平台可能受网络环境、认证状态、平台可用性和排队情况影响。
- **平台输入格式不同**：OriginQ Cloud / Dummy 更偏向 `originir` 路径，Quafu 与 IBM 示例则使用 `qasm` 路径。
- **平台成熟度不同**：OriginQ Cloud 是当前主生产路径；Dummy 适合联调；Quafu / IBM 是独立平台接入；Legacy OriginQ 当前不可用。

如果你还在反复修改线路结构、量子门或输出解释，说明你仍处于本地验证阶段，建议先回到 [本地模拟](simulation.md#guide-simulation-entry-overview)。

## 下一步与参考

- 如果你还没有完成线路验证，先回到 [本地模拟](simulation.md#guide-simulation-entry-overview)
- 如果你还不清楚线路如何构建，先阅读 [构建量子线路](circuit.md#guide-circuit-when-to-read)
- 如果你已经确定目标平台，可继续查看对应模块 API：
  - {mod}`qpandalite.task.origin_qcloud`
  - {mod}`qpandalite.task.originq_dummy`
  - {mod}`qpandalite.task.quafu`
  - {mod}`qpandalite.task.ibm`
  - {mod}`qpandalite.task.platform_template`
