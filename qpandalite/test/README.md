# 测试设计与规范

## 目录结构

```
qpandalite/test/
├── core/                # 核心解析测试
├── circuit_builder/     # 电路构建测试
├── algorithmics/        # 算法电路测试
│   ├── circuits/        # 电路组件测试
│   ├── measurement/     # 测量测试
│   └── state_preparation/ # 态制备测试
├── simulator/           # 模拟器测试
├── cloud/               # 云平台测试
│   └── platforms/       # 平台配置测试
├── transpiler/          # 转译器测试
├── adapter/             # 适配器测试
├── analyzer/            # 分析器测试
├── benchmark/           # 基准测试
└── integration/         # 集成测试
```

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

# 运行特定类别
pytest qpandalite/test/core/ -v
pytest qpandalite/test/simulator/ -v

# 单独运行某个测试
python -m pytest qpandalite/test/core/test_originir_parser.py::run_test_originir_parser -v

# 通过 run_test() 运行全部（旧方式，已废弃）
from qpandalite.test import run_test
run_test()
```

## 当前测试项清单

| 测试文件 | 正式测试函数 | 说明 |
|---------|------------|------|
| `core/test_general.py` | `run_test_general()` | 通测占位（当前为空） |
| `core/test_originir_parser.py` | `run_test_originir_parser()` | OriginIR 解析器 |
| `core/test_qasm_parser.py` | `run_test_qasm_parser()` | OpenQASM2 解析器 |
| `cloud/test_demos.py` | `run_test_demos()` | OriginQ 远程任务示例 |
| `cloud/test_result_adapter.py` | `run_test_result_adapter()` | 结果适配器 |
| `simulator/test_simulator.py` | `run_test_simulator()` | 噪声模拟器 |
| `simulator/test_random_QASM.py` | `run_test_random_qasm_*` | 随机 QASM 电路（4个测试） |
| `simulator/test_random_OriginIR.py` | `run_test_random_originir_density_operator()` | 随机 OriginIR 电路 |
| `simulator/test_random_QASM_measure.py` | `run_test_random_qasm_compare_shots()` | 随机电路 shot 对比 |
| `benchmark/test_QASMBench.py` | `run_test_qasm()` | QASMBench 电路集 |

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
- **Pytest Coverage workflow**：使用 `pytest qpandalite/test/ -v --deselect qpandalite/test/simulator/test_random_QASM.py::test_random_qasm_compare_density_operator`

两个 workflow 现已统一使用 pytest。
