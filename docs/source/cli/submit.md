# 云端任务提交 (`qpandalite submit`)

将电路提交到量子云平台。

## 基本用法

```bash
# 提交单个电路
qpandalite submit circuit.ir --platform originq --shots 1000

# 指定后端名称
qpandalite submit circuit.ir --platform originq --backend origin:wuyuan:d5 --shots 1000

# 提交并等待结果
qpandalite submit circuit.ir --platform originq --wait --timeout 300
```

## 批量提交

```bash
# 提交多个电路
qpandalite submit circuit1.ir circuit2.ir circuit3.ir --platform originq
```

## 支持的平台

| 平台 | 说明 |
|------|------|
| `originq` | 本源量子云平台 |
| `quafu` | QUAFU 量子云平台 |
| `ibm` | IBM Quantum |
| `dummy` | 本地模拟器（用于测试） |

## 输出格式

```bash
# 表格输出（默认）
qpandalite submit circuit.ir --platform originq

# JSON 输出
qpandalite submit circuit.ir --platform originq --format json
```
