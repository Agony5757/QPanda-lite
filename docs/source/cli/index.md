# 命令行工具 (CLI)

QPanda-lite 提供了一个功能完整的命令行工具，覆盖量子计算的核心工作流：电路格式转换、本地模拟、云端任务提交、结果查询、配置管理和任务管理。

## 安装与入口

CLI 工具随 `qpandalite` 包一同安装，提供两种调用方式：

```bash
# 推荐：直接命令
qpandalite --help

# 备选：模块方式
python -m qpandalite --help
```

## 电路格式转换 (`qpandalite circuit`)

在 OriginIR 和 OpenQASM 2.0 格式之间转换电路。

### 基本用法

```bash
# 自动检测输入格式，转换为另一种格式
qpandalite circuit input.ir

# 指定输出格式
qpandalite circuit input.ir --format qasm

# 输出到文件
qpandalite circuit input.ir --format qasm --output circuit.qasm
```

### 查看电路统计信息

```bash
qpandalite circuit input.ir --info
```

输出示例：

```
┏━━━━━━━━━━━┳━━━━━━━┓
┃ Property  ┃ Value ┃
┡━━━━━━━━━━━╇━━━━━━━┩
│ Qubits    │ 2     │
│ Cbits     │ 2     │
│ Depth     │ 2     │
│ Gates     │ 3     │
└───────────┴───────┘
```

### 支持的格式

| 格式 | 说明 |
|------|------|
| `originir` | QPanda-lite 原生格式 |
| `qasm` | OpenQASM 2.0 格式 |

## 本地模拟 (`qpandalite simulate`)

在本地运行量子电路模拟。

### 基本用法

```bash
# 使用状态向量后端，默认 1024 shots
qpandalite simulate circuit.ir

# 指定后端和 shots 数
qpandalite simulate circuit.ir --backend statevector --shots 1000

# 使用密度矩阵后端
qpandalite simulate circuit.ir --backend density --shots 2048
```

### 输出格式

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

### 后端类型

| 后端 | 说明 |
|------|------|
| `statevector` | 状态向量模拟器，返回精确概率分布 |
| `density` | 密度矩阵模拟器，支持噪声模拟 |

## 云端任务提交 (`qpandalite submit`)

将电路提交到量子云平台。

### 基本用法

```bash
# 提交单个电路
qpandalite submit circuit.ir --platform originq --shots 1000

# 指定芯片 ID
qpandalite submit circuit.ir --platform originq --chip-id 72 --shots 1000

# 提交并等待结果
qpandalite submit circuit.ir --platform originq --wait --timeout 300
```

### 批量提交

```bash
# 提交多个电路
qpandalite submit circuit1.ir circuit2.ir circuit3.ir --platform originq
```

### 支持的平台

| 平台 | 说明 |
|------|------|
| `originq` | 本源量子云平台 |
| `quafu` | QUAFU 量子云平台 |
| `ibm` | IBM Quantum |
| `dummy` | 本地模拟器（用于测试） |

### 输出格式

```bash
# 表格输出（默认）
qpandalite submit circuit.ir --platform originq

# JSON 输出
qpandalite submit circuit.ir --platform originq --format json
```

## 结果查询 (`qpandalite result`)

查询已提交任务的结果。

### 基本用法

```bash
# 查询任务结果
qpandalite result TASK_ID --platform originq

# 等待任务完成
qpandalite result TASK_ID --platform originq --wait

# 设置超时时间
qpandalite result TASK_ID --platform originq --wait --timeout 600
```

### 输出格式

```bash
# 表格输出（默认）
qpandalite result TASK_ID --platform originq

# JSON 输出
qpandalite result TASK_ID --platform originq --format json
```

表格输出示例：

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Result for TASK123456    ┃
┡━━━━━━━┳━━━━━━━┳━━━━━━━━━┩
│ State │ Count │ Prob    │
├───────┼───────┼─────────┤
│ 00    │ 487   │ 48.7%   │
│ 11    │ 513   │ 51.3%   │
└───────┴───────┴─────────┘
```

## 配置管理 (`qpandalite config`)

管理云平台的 API 密钥和配置。

### 初始化配置

```bash
# 创建默认配置文件
qpandalite config init
```

配置文件位置：`~/.qpandalite/qpandalite.yml`

### 设置配置项

```bash
# 设置平台 Token
qpandalite config set originq.token YOUR_TOKEN
qpandalite config set quafu.token YOUR_TOKEN
qpandalite config set ibm.token YOUR_TOKEN

# 在指定 profile 下设置
qpandalite config set originq.token YOUR_TOKEN --profile production
```

### 查看配置

```bash
# 查看特定平台配置
qpandalite config get originq

# 列出所有平台配置状态
qpandalite config list

# 以 JSON 格式输出
qpandalite config list --format json
```

### 验证配置

```bash
# 验证当前配置是否有效
qpandalite config validate
```

### 配置 Profile 管理

```bash
# 列出所有 profile
qpandalite config profile list

# 切换 profile
qpandalite config profile use production

# 创建新 profile
qpandalite config profile create testing
```

## 任务管理 (`qpandalite task`)

管理已提交的任务。

### 列出任务

```bash
# 列出所有任务
qpandalite task list

# 按状态筛选
qpandalite task list --status success
qpandalite task list --status failed

# 按平台筛选
qpandalite task list --platform originq

# 限制显示数量
qpandalite task list --limit 10
```

表格输出示例：

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Tasks                              ┃
┡━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━┩
│ Task ID    │ Platform │ Status │ Shots │ Submit Time    │
├────────────┼──────────┼────────┼───────┼────────────────┤
│ TASK001    │ originq  │ success│ 1000  │ 2026-04-18 10: │
│ TASK002    │ originq  │ running│ 2000  │ 2026-04-18 11: │
└────────────┴──────────┴────────┴───────┴────────────────┘
```

### 查看任务详情

```bash
# 显示任务详情
qpandalite task show TASK_ID

# JSON 格式输出
qpandalite task show TASK_ID --format json
```

### 清理任务缓存

```bash
# 清理已完成的任务
qpandalite task clear --status completed

# 清理所有缓存（需确认）
qpandalite task clear

# 强制清理（无需确认）
qpandalite task clear --force
```

## 完整工作流示例

### 示例 1：本地开发测试

```bash
# 1. 构建电路（使用 Python API 或手动编写）
# 创建 bell.ir 文件

# 2. 查看电路信息
qpandalite circuit bell.ir --info

# 3. 本地模拟
qpandalite simulate bell.ir --shots 1000

# 4. 转换格式
qpandalite circuit bell.ir --format qasm --output bell.qasm
```

### 示例 2：云端任务提交

```bash
# 1. 初始化配置
qpandalite config init

# 2. 设置 API Token
qpandalite config set originq.token YOUR_TOKEN

# 3. 验证配置
qpandalite config validate

# 4. 提交任务
qpandalite submit bell.ir --platform originq --chip-id 72 --shots 1000

# 5. 查询结果
qpandalite result TASK_ID --platform originq --wait

# 6. 查看任务列表
qpandalite task list --platform originq
```

### 示例 3：批量处理

```bash
# 批量提交多个电路
qpandalite submit circuit1.ir circuit2.ir circuit3.ir \
    --platform originq \
    --chip-id 72 \
    --shots 1000 \
    --format json

# 查看所有任务状态
qpandalite task list --format json
```

## 常见问题

### Q：如何确认 CLI 已正确安装？

```bash
qpandalite --help
```

如果显示帮助信息，说明安装成功。

### Q：配置文件存储在哪里？

配置文件位于 `~/.qpandalite/qpandalite.yml`。可以通过 `qpandalite config init` 重新初始化。

### Q：如何切换不同的云平台账户？

使用 profile 功能：

```bash
# 创建不同账户的 profile
qpandalite config profile create account1
qpandalite config set originq.token TOKEN1 --profile account1

qpandalite config profile create account2
qpandalite config set originq.token TOKEN2 --profile account2

# 切换 profile
qpandalite config profile use account1
```

### Q：dummy 平台是什么？

`dummy` 是一个本地模拟器后端，用于测试工作流而无需连接真实云平台。提交到 dummy 的任务会立即返回模拟结果。

```bash
qpandalite submit bell.ir --platform dummy --wait
```

## 下一步

- [构建量子线路](../guide/circuit.md) —— 学习如何使用 Python API 构建复杂电路
- [本地模拟](../guide/simulation.md) —— 了解更多模拟后端和参数
- [提交任务](../guide/submit_task.md) —— 云端任务提交的详细说明
