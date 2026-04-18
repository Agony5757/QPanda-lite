# 配置管理 (`qpandalite config`)

管理云平台的 API 密钥和配置。

## 初始化配置

```bash
# 创建默认配置文件
qpandalite config init
```

配置文件位置：`~/.qpandalite/qpandalite.yml`

## 设置配置项

```bash
# 设置平台 Token
qpandalite config set originq.token YOUR_TOKEN
qpandalite config set quafu.token YOUR_TOKEN
qpandalite config set ibm.token YOUR_TOKEN

# 在指定 profile 下设置
qpandalite config set originq.token YOUR_TOKEN --profile production
```

## 查看配置

```bash
# 查看特定平台配置
qpandalite config get originq

# 列出所有平台配置状态
qpandalite config list

# 以 JSON 格式输出
qpandalite config list --format json
```

## 验证配置

```bash
# 验证当前配置是否有效
qpandalite config validate
```

## 配置 Profile 管理

```bash
# 列出所有 profile
qpandalite config profile list

# 切换 profile
qpandalite config profile use production

# 创建新 profile
qpandalite config profile create testing
```
