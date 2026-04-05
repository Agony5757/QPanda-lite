# 测试设计与规范

## 核心原则

**只有被 `@qpandalite_test` 装饰器修饰的函数才是需要执行的正式测试。**

`@qpandalite_test` 会打印测试开始/结束信息，用于 CI 识别和人类阅读。

## 命名规范

### 正式测试函数
- 命名格式：`run_test_<功能名>`
- 必须被 `@qpandalite_test('<描述>')` 修饰
- pytest 会自动收集所有 `run_test_*` 函数

### 辅助函数（内部使用）
- 命名格式：`<功能名>`（不带前缀）或 `_<功能名>`
- 不带 `@qpandalite_test` 装饰器
- 被正式测试函数内部调用，不直接暴露给 pytest

## 测试执行入口

```python
# 通过 pytest 运行全部（推荐）
pytest qpandalite/test/ -v

# 单独运行某个测试
python -m pytest qpandalite/test/test_general.py::run_test_general -v

# 通过 run_test() 运行全部（旧方式，已废弃）
from qpandalite.test import run_test
run_test()
```

## 当前测试项清单

| 测试文件 | 正式测试函数 | 说明 | 辅助函数 |
|---------|------------|------|---------|
| `test_general.py` | `run_test_general()` | 通测占位（当前为空） | `iswap_test()` |
| `test_demos.py` | `run_test_demos()` | OriginQ 远程任务示例 | `demo_2()`, `demo_3()` |
| `test_simulator.py` | `run_test_simulator()` | 噪声模拟器 | `test_noisy_simulator()`, `test_noisy_simulator_2()` |
| `test_originir_parser.py` | `run_test_originir_parser()` | OriginIR 解析器 | — |
| `test_qasm_parser.py` | `run_test_qasm_parser()` | OpenQASM2 解析器 | — |
| `test_result_adapter.py` | `run_test_result_adapter()` | 结果适配器 | — |
| `test_transpile.py` | `run_test_transpile_plot_time_line()` | 电路转译时间线 | — |
| `test_QASMBench.py` | `run_test_qasm()` | QASMBench 电路集 | `test_qasm()` |
| `test_random_QASM.py` | `run_test_random_qasm_statevector()` | 随机 QASM 电路（statevector） | `_test_random_qasm_batch()` |
| `test_random_QASM.py` | `run_test_random_qasm_density_operator()` | 随机 QASM 电路（density_operator） | 同上 |
| `test_random_QASM.py` | `run_test_random_qasm_density_operator_qutip()` | 随机 QASM 电路（density_operator_qutip） | 同上 |
| `test_random_QASM.py` | `run_test_random_qasm_density_operator_compare_with_qutip()` | QPanda-lite vs QuTip 对比 | `_test_random_qasm_compare_density_operator()` |
| `test_random_OriginIR.py` | `run_test_random_originir_density_operator()` | 随机 OriginIR 电路 | `_test_random_originir_compare_density_operator()` |
| `test_random_QASM_measure.py` | `run_test_random_qasm_compare_shots()` | 随机电路 shot 对比 | `_run_test_random_qasm_compare_shots_impl()` |

**pytest 共收集 14 个正式测试函数。**

## pytest 配置说明

```ini
[pytest]
testpaths = qpandalite/test
python_files = test_*.py
python_functions = run_test_*
addopts = -v
```

- `python_functions = run_test_*` 确保只收集正式测试，不收集辅助函数
- 辅助函数不应以 `run_test_` 或 `test_` 开头，避免被 pytest 误收集

## CI 配置说明

- **Build-and-test workflow**：使用 `pytest qpandalite/test/ -v`
- **Pytest Coverage workflow**：使用 `pytest qpandalite/test/ -v --deselect qpandalite/test/test_random_QASM.py::test_random_qasm_compare_density_operator`

两个 workflow 现已统一使用 pytest。
