# 本地模拟 (`qpandalite simulate`)

在本地运行量子电路模拟。

## 基本用法

```bash
# 使用状态向量后端，默认 1024 shots
qpandalite simulate circuit.ir

# 指定后端和 shots 数
qpandalite simulate circuit.ir --backend statevector --shots 1000

# 使用密度矩阵后端
qpandalite simulate circuit.ir --backend density --shots 2048
```

## 输出格式

```bash
# 表格输出（默认）
qpandalite simulate circuit.ir

# JSON 输出
qpandalite simulate circuit.ir --format json

# 输出到文件
qpandalite simulate circuit.ir --output result.json
```

表格输出示例：

```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Simulation Results        ┃            ┃
┡━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┩
│ State │ Count │ Probability│
├───────┼───────┼────────────┤
│ 00    │ 498   │ 49.8%      │
│ 11    │ 502   │ 50.2%      │
└───────┴───────┴────────────┘
```

## 后端类型

| 后端 | 说明 |
|------|------|
| `statevector` | 状态向量模拟器，返回精确概率分布 |
| `density` | 密度矩阵模拟器，支持噪声模拟 |
