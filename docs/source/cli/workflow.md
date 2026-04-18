# 完整工作流与常见问题

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
qpandalite submit bell.ir --platform originq --backend origin:wuyuan:d5 --shots 1000

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
    --backend origin:wuyuan:d5 \
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
