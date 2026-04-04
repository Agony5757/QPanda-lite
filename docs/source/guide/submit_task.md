# 提交任务到量子云平台

QPanda-lite 支持将量子线路提交到多个量子计算云平台的真机上运行。

## 支持的平台

| 平台 | 模块 | 额外依赖 |
|------|------|---------|
| OriginQ（本源量子） | `qpandalite.task.originq` | — |
| OriginQ Dummy | `qpandalite.task.originq_dummy` | — |
| OriginQ Cloud | `qpandalite.task.origin_qcloud` | — |
| Quafu（北大） | `qpandalite.task.quafu` | `pip install quafu` |
| IBM Quantum | `qpandalite.task.ibm` | `pip install qiskit qiskit-ibm-provider` |

## 通用流程

所有平台遵循相同的流程：

1. **配置** — 设置平台 API 密钥/Token
2. **构建线路** — 使用 `Circuit` 构建
3. **提交任务** — 调用对应平台的提交函数
4. **获取结果** — 查询任务状态，获取结果

## OriginQ 平台

### 配置

```python
from qpandalite.qcloud_config import originq_online_config

originq_online_config.api_key = "your_api_key"
```

### 提交任务

```python
from qpandalite.task.originq import submit_task

task_id = submit_task(
    circuit=circuit.originir,
    shots=1000
)
```

### 查询结果

```python
result = query_result(task_id)
print(result)
```

> ⚠️ 提交到 OriginQ 服务器可能需要 VPN。

## Quafu 平台

### 配置

```python
from qpandalite.qcloud_config import quafu_online_config

quafu_online_config.api_key = "your_api_key"
```

### 提交任务

```python
from qpandalite.task.quafu import submit_task

task_id = submit_task(
    circuit=circuit.qasm,
    shots=1000
)
```

## IBM Quantum

### 配置

```python
from qpandalite.qcloud_config import ibm_online_config

ibm_online_config.api_key = "your_ibm_token"
```

### 提交任务

```python
from qpandalite.task.ibm import submit_task

task_id = submit_task(
    circuit=circuit.qasm,
    shots=1000
)
```

## OriginQ Dummy 模式

用于本地测试，模拟真机返回结果，无需连接服务器。

```python
from qpandalite.task.originq_dummy import submit_task

result = submit_task(
    circuit=circuit.originir,
    shots=1000
)
```

## API 参考

各平台的完整 API 见：

- `qpandalite.task.originq`
- `qpandalite.task.origin_qcloud`
- `qpandalite.task.originq_dummy`
- `qpandalite.task.quafu`
- `qpandalite.task.ibm`
- `qpandalite.task.platform_template` — 平台模板基类
