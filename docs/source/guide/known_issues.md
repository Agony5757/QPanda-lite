# 已知问题 (Known Issues)

本文档记录 QPanda-lite 中已知的、尚未修复的问题。

## C++ 密度算符模拟中的受控旋转门问题

### 问题描述

C++ 密度算符（density operator）实现在处理受控旋转门（`crx`, `crz`, `cy`）时存在已知问题。这会导致涉及这些门的随机线路密度算符测试失败。

### 受影响的测试

以下测试目前在 CI 中通过 `--deselect` 跳过：

| 测试文件 | 测试函数 | 原因 |
|---------|---------|------|
| `test_random_QASM.py` | `test_random_qasm_compare_density_operator` | 受控旋转门失败 |
| `test_random_OriginIR.py` | `run_test_random_originir_density_operator` | 受控旋转门失败 |
| `test_random_QASM.py` | `run_test_random_qasm_density_operator_compare_with_qutip` | 受控旋转门失败 |

### 当前绕过方案

这些测试目前在 `.github/workflows/build_and_test.yml` 中被排除，以允许 CI 通过：

```yaml
pytest qpandalite/test/ -v \
  --deselect qpandalite/test/test_random_QASM.py::test_random_qasm_compare_density_operator \
  --deselect qpandalite/test/test_random_OriginIR.py::run_test_random_originir_density_operator \
  --deselect qpandalite/test/test_random_QASM.py::run_test_random_qasm_density_operator_compare_with_qutip
```

### 根本原因

问题的根源在于 C++ 密度算符实现对受控旋转门的处理。状态向量模拟工作正常，但密度算符路径产生不正确的结果。

### 影响

- 依赖密度算符模拟且使用受控旋转门的用户可能获得不正确的结果
- 验证密度算符与状态向量模拟的随机线路测试被禁用

### 未来工作

- [ ] 修复 C++ 密度算符实现中的 `crx`, `crz`, `cy` 门问题
- [ ] 修复完成后重新启用被跳过的测试
- [ ] 为密度算符模式下的受控旋转门添加针对性的单元测试

### 相关链接

- Issue: [#145](https://github.com/Agony5757/QPanda-lite/issues/145)
- 相关提交: a8c0b5b（原始排除）
- PR #143（恢复第一个排除）
- PR #144（添加额外的排除）
