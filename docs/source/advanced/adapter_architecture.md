# 云平台适配器架构 {#advanced-adapter-architecture}

## 概述 {#advanced-adapter-overview}

QPanda-lite 的云平台适配器采用 **适配器模式（Adapter Pattern）**，通过统一的 `QuantumAdapter` 基类定义接口，各平台实现具体的适配逻辑。这种设计使得用户可以在不同量子云平台之间无缝切换，而无需修改业务代码。

### 架构图

```
                    ┌─────────────────────┐
                    │   QuantumAdapter    │
                    │     (抽象基类)       │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ OriginQAdapter│    │  QuafuAdapter │    │ QiskitAdapter │
│   (OriginQ)   │    │    (BAQIS)    │    │   (IBM)       │
└───────────────┘    └───────────────┘    └───────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ OriginIR API  │    │  Quafu SDK    │    │  Qiskit SDK   │
└───────────────┘    └───────────────┘    └───────────────┘

                    ┌───────────────┐
                    │ DummyAdapter  │
                    │  (本地模拟)    │
                    └───────────────┘
                           │
                           ▼
                    ┌───────────────┐
                    │OriginIR_Sim   │
                    └───────────────┘
```

## QuantumAdapter 基类 {#advanced-adapter-base-class}

`QuantumAdapter` 是所有适配器的抽象基类，定义了统一的接口。

### 接口定义

```python
class QuantumAdapter(ABC):
    """云平台适配器抽象基类。"""

    name: str  # 适配器名称

    @abstractmethod
    def translate_circuit(self, originir: str) -> Any:
        """将 OriginIR 转换为平台原生格式。"""
        pass

    @abstractmethod
    def submit(self, circuit: Any, *, shots: int = 1000, **kwargs) -> str:
        """提交单个线路，返回任务 ID。"""
        pass

    @abstractmethod
    def submit_batch(self, circuits: list[Any], *, shots: int = 1000, **kwargs) -> list[str]:
        """批量提交线路，返回任务 ID 列表。"""
        pass

    @abstractmethod
    def query(self, taskid: str) -> dict[str, Any]:
        """查询单个任务状态和结果。"""
        pass

    @abstractmethod
    def query_batch(self, taskids: list[str]) -> dict[str, Any]:
        """批量查询多个任务。"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查适配器是否可用。"""
        pass
```

### 方法详解

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `translate_circuit()` | 将 OriginIR 转换为平台原生格式 | 平台特定的电路对象 |
| `submit()` | 提交单个线路 | 任务 ID 字符串 |
| `submit_batch()` | 批量提交线路 | 任务 ID 列表 |
| `query()` | 查询任务状态 | `{'status': ..., 'result': ...}` |
| `query_batch()` | 批量查询任务 | `{'status': ..., 'result': [...]}` |
| `is_available()` | 检查适配器可用性 | 布尔值 |

### 任务状态常量

```python
TASK_STATUS_SUCCESS = "success"  # 任务成功完成
TASK_STATUS_FAILED = "failed"    # 任务失败
TASK_STATUS_RUNNING = "running"  # 任务运行中
```

## 各平台适配器 {#advanced-adapter-implementations}

### OriginQAdapter

用于接入 OriginQ 量子云平台。

```python
from qpandalite.task.adapters.originq_adapter import OriginQAdapter

adapter = OriginQAdapter()

# 转换电路（OriginIR 直接支持）
circuit = adapter.translate_circuit(originir_string)

# 提交任务
task_id = adapter.submit(circuit, shots=1000, chip_id='...')

# 查询结果
result = adapter.query(task_id)
```

**特点：**
- 直接支持 OriginIR 格式
- 使用 HTTP REST API 与云平台通信
- 支持批量任务分组

### QuafuAdapter

用于接入 BAQIS Quafu (ScQ) 量子云平台。

```python
from qpandalite.task.adapters.quafu_adapter import QuafuAdapter

adapter = QuafuAdapter()

# 转换电路（OriginIR -> Quafu QuantumCircuit）
circuit = adapter.translate_circuit(originir_string)

# 提交任务
task_id = adapter.submit(
    circuit,
    shots=10000,
    chip_id='ScQ-P18',
    auto_mapping=True
)

# 查询结果
result = adapter.query(task_id)
```

**支持的芯片：**
- `ScQ-P10`
- `ScQ-P18`
- `ScQ-P136`
- `ScQ-P10C`
- `Dongling`

### QiskitAdapter

用于接入 IBM Quantum 平台。

```python
from qpandalite.task.adapters.qiskit_adapter import QiskitAdapter

# 支持代理配置
adapter = QiskitAdapter(proxy={
    "http": "http://proxy:8080",
    "https": "https://proxy:8080"
})

# 转换电路（OriginIR -> QASM -> Qiskit QuantumCircuit）
circuit = adapter.translate_circuit(originir_string)

# 提交任务
task_id = adapter.submit(
    circuit,
    shots=1000,
    chip_id='ibmq_qasm_simulator',
    auto_mapping=True,
    circuit_optimize=True
)

# 阻塞等待结果
results = adapter.query_sync(task_id, timeout=300)
```

**特点：**
- 支持代理配置
- 支持电路优化和自动映射
- 提供 `query_sync()` 方法阻塞等待结果

### DummyAdapter

用于本地模拟，无需真实云平台连接。

```python
from qpandalite.task.adapters.dummy_adapter import DummyAdapter

# 基本使用
adapter = DummyAdapter()

# 带噪声模型
adapter = DummyAdapter(
    noise_model={'depol': 0.01},
    available_qubits=[0, 1, 2],
    available_topology=[[0, 1], [1, 2]]
)

# 提交任务（立即执行）
task_id = adapter.submit(originir_string, shots=1000)

# 查询结果（立即可用）
result = adapter.query(task_id)
```

**特点：**
- 无需网络连接
- 支持噪声模拟
- 支持拓扑约束
- 结果立即可用

## 结果归一化 {#advanced-adapter-normalization}

各平台适配器返回的结果格式可能不同，`normalizers` 模块提供了统一的结果转换函数。

### UnifiedResult 类

```python
from qpandalite.task.result_types import UnifiedResult

# 从计数结果创建
result = UnifiedResult.from_counts(
    counts={'00': 500, '11': 500},
    shots=1000,
    platform='originq',
    task_id='xxx'
)

# 从概率分布创建
result = UnifiedResult.from_probabilities(
    probabilities={'00': 0.5, '11': 0.5},
    shots=1000,
    platform='dummy',
    task_id='xxx'
)

# 计算期望值
expectation = result.get_expectation(observable='Z')
```

### 归一化函数

```python
from qpandalite.task.normalizers import (
    normalize_originq,
    normalize_quafu,
    normalize_ibm,
    normalize_dummy
)

# 将平台原始结果转换为 UnifiedResult
unified = normalize_originq(raw_result, task_id='xxx', shots=1000)
```

## 配置管理 {#advanced-adapter-configuration}

### 环境变量

适配器通过环境变量读取配置：

| 平台 | 环境变量 | 说明 |
|------|----------|------|
| OriginQ | `QPANDA_API_KEY` | API 密钥 |
| OriginQ | `QPANDA_SUBMIT_URL` | 提交 URL |
| OriginQ | `QPANDA_QUERY_URL` | 查询 URL |
| Quafu | `QUAFU_API_TOKEN` | API Token |
| IBM | `IBM_TOKEN` | IBM Quantum Token |
| Dummy | `QPANDALITE_DUMMY` | 启用 Dummy 模式 |

### 配置加载

```python
from qpandalite.task.config import (
    load_originq_config,
    load_quafu_config,
    load_ibm_config
)

config = load_originq_config()
api_key = config['api_token']
```

## 实现自定义适配器 {#advanced-adapter-custom}

要实现自定义适配器，继承 `QuantumAdapter` 并实现所有抽象方法：

```python
from qpandalite.task.adapters.base import (
    QuantumAdapter,
    TASK_STATUS_SUCCESS,
    TASK_STATUS_FAILED
)

class MyCustomAdapter(QuantumAdapter):
    """自定义量子云平台适配器。"""

    name = "my_custom"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = MyPlatformClient(api_key)

    def translate_circuit(self, originir: str) -> MyCircuit:
        """将 OriginIR 转换为平台格式。"""
        # 实现转换逻辑
        return my_circuit

    def submit(self, circuit: MyCircuit, *, shots: int = 1000, **kwargs) -> str:
        """提交任务。"""
        response = self._client.submit(circuit, shots=shots)
        return response['task_id']

    def submit_batch(self, circuits: list[MyCircuit], *, shots: int = 1000, **kwargs) -> list[str]:
        """批量提交。"""
        return [self.submit(c, shots=shots) for c in circuits]

    def query(self, taskid: str) -> dict:
        """查询任务状态。"""
        response = self._client.query(taskid)
        if response['status'] == 'completed':
            return {
                'status': TASK_STATUS_SUCCESS,
                'result': response['result']
            }
        return {'status': TASK_STATUS_FAILED, 'error': response.get('error')}

    def query_batch(self, taskids: list[str]) -> dict:
        """批量查询。"""
        results = [self.query(tid) for tid in taskids]
        overall_status = TASK_STATUS_SUCCESS
        for r in results:
            if r['status'] == TASK_STATUS_FAILED:
                overall_status = TASK_STATUS_FAILED
                break
        return {
            'status': overall_status,
            'result': [r.get('result', {}) for r in results]
        }

    def is_available(self) -> bool:
        """检查适配器是否可用。"""
        try:
            self._client.ping()
            return True
        except Exception:
            return False
```

## 最佳实践 {#advanced-adapter-best-practices}

### 1. 懒加载依赖

适配器应在实例化时才导入平台特定的包，避免导入错误：

```python
def __init__(self):
    from quafu import QuantumCircuit, Task, User
    self._QuantumCircuit = QuantumCircuit
    # ...
```

### 2. 状态优先级

在批量查询时，状态应按优先级合并：`failed` > `running` > `success`

```python
def query_batch(self, taskids):
    overall_status = TASK_STATUS_SUCCESS
    for r in results:
        if r['status'] == TASK_STATUS_FAILED:
            overall_status = TASK_STATUS_FAILED
            break
        elif r['status'] == TASK_STATUS_RUNNING:
            overall_status = TASK_STATUS_RUNNING
    # ...
```

### 3. 异常处理

使用 `MissingDependencyError` 提供清晰的依赖缺失提示：

```python
from qpandalite.task.optional_deps import MissingDependencyError, check_quafu

def __init__(self):
    if not check_quafu():
        raise MissingDependencyError("quafu", "quafu")
```

### 4. 缓存管理

对于长期运行的服务，实现缓存限制避免内存泄漏：

```python
class MyAdapter(QuantumAdapter):
    _MAX_CACHE_SIZE = 100

    def _add_to_cache(self, task_id, result):
        if len(self._cache) >= self._MAX_CACHE_SIZE:
            # 移除最旧的条目
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[task_id] = result
```

## API 参考 {#advanced-adapter-api-reference}

- {mod}`qpandalite.task.adapters.base` - 适配器基类
- {mod}`qpandalite.task.adapters.originq_adapter` - OriginQ 适配器
- {mod}`qpandalite.task.adapters.quafu_adapter` - Quafu 适配器
- {mod}`qpandalite.task.adapters.qiskit_adapter` - IBM Qiskit 适配器
- {mod}`qpandalite.task.adapters.dummy_adapter` - Dummy 适配器
- {mod}`qpandalite.task.result_types` - 统一结果类型
- {mod}`qpandalite.task.normalizers` - 结果归一化函数
