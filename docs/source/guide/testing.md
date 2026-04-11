# 测试覆盖说明

本页介绍 QPanda-lite 的测试体系：测试框架、文件组织、各模块的测试方式与覆盖范围，以及如何运行测试和 CI 集成。

## 什么时候进入本页

- 你想知道项目有哪些测试、覆盖了哪些模块
- 你在开发新功能，需要了解如何编写或运行测试
- 你在排查问题，想确认某个模块是否有对应的测试

## 测试框架

- **框架**：[pytest](https://docs.pytest.org/)
- **测试目录**：`qpandalite/test/`
- **配置文件**：`pytest.ini`（项目根目录）

测试函数命名规则（由 `pytest.ini` 中的 `python_functions` 配置）：
- `test_*`：被 pytest 自动收集的标准测试
- `run_test_*`：被 pytest 自动收集的测试入口（兼容历史命名）

## 运行测试

```bash
# 运行全部测试
pytest qpandalite/test/ -v

# 运行指定模块测试
pytest qpandalite/test/test_simulator.py -v

# 运行测试并生成覆盖率报告
pytest qpandalite/test/ --cov=qpandalite --cov-report=term-missing -v
```

> **注意**：部分随机回归测试（`test_random_*`）依赖 `qiskit`、`qiskit-aer`、`qutip` 等外部包，需额外安装。

## 逐模块测试覆盖

| 模块 | 测试文件 | 测试方式 | 覆盖范围 |
|------|----------|----------|----------|
| **simulator** | `test_simulator.py` | 单元测试 | 噪声模拟器（`OriginIR_NoisySimulator`）statevector/density_matrix 后端计算正确性；含自定义错误模型测试 |
| **originir** | `test_originir_parser.py`, `test_random_OriginIR.py` | 单元测试 + 随机回归 | 解析器：随机生成 OriginIR → 解析 → 重建 → 模拟结果一致性验证；密度矩阵后端与 QuTip 对比 |
| **qasm** | `test_qasm_parser.py`, `test_random_QASM.py`, `test_random_QASM_measure.py`, `test_QASMBench.py` | 单元测试 + 随机回归 + Benchmark | QASM 解析与重建一致性；statevector/density_matrix 后端与 Qiskit 对比；shots 采样与 Qiskit 对比；QASMBench 兼容性验证 |
| **transpiler** | `test_transpile.py` | 单元测试 | `plot_time_line` 脉冲序列可视化正确性 |
| **analyzer** | `test_result_adapter.py` | 单元测试 | 结果适配器工具函数基本验证 |
| **circuit_builder** | `test_general.py` | 集成测试 | 电路构建基本功能（iswap 等特殊门操作） |
| **demos** | `test_demos.py` | 集成测试 | 示例代码（`originq_dummy` 模式）端到端运行验证 |

### 各测试文件详细说明

#### test_simulator.py

测试模拟器的计算正确性，主要覆盖：

- **噪声模拟器测试**：构建含噪声量子线路，验证 `OriginIR_NoisySimulator` 在 statevector 和 density_matrix 两种后端下的结果
- **自定义错误模型**：测试 `BitFlip`、`PhaseFlip`、`Depolarizing`、`TwoQubitDepolarizing`、`AmplitudeDamping` 等预设错误模型

#### test_originir_parser.py

验证 OriginIR 解析器的正确性：

- 随机生成 OriginIR 代码 → 解析为 `Circuit` 对象 → 重新导出 OriginIR → 比较两次模拟结果
- 确保解析-重建往返（round-trip）不丢失语义信息

#### test_random_OriginIR.py

随机回归测试，与 QuTip 交叉验证：

- 随机生成多门组合线路，分别用 QPanda-lite 和 QuTip 模拟
- 比较 density matrix 结果的一致性
- 支持含噪声线路的对比测试

#### test_qasm_parser.py

验证 QASM 解析器的正确性：

- 随机生成 QASM 代码 → 解析 → 重建 → 模拟结果一致性验证
- 与 OriginIR 解析器类似的 round-trip 测试策略

#### test_random_QASM.py

随机回归测试，与 Qiskit 交叉验证：

- **statevector 对比**：QPanda-lite 与 Qiskit statevector 模拟结果对比
- **density matrix 对比**：QPanda-lite density matrix 后端与 Qiskit 对比
- **QuTip 对比**：density matrix 与 QuTip 结果一致性验证

#### test_random_QASM_measure.py

Shots 采样测试：

- QPanda-lite 与 Qiskit 的 shots 采样结果对比
- 验证测量概率分布的统计一致性

#### test_QASMBench.py

QASMBench 基准测试兼容性：

- 加载 QASMBench 数据集（`.pkl`）
- 解析、转译 QASM 电路并验证模拟结果

#### test_transpile.py

转译工具测试：

- `plot_time_line`：验证脉冲序列 JSON 的解析和可视化

#### test_result_adapter.py

结果适配器工具函数的基本验证。

#### test_general.py

电路构建集成测试：

- 验证 `sx`、`xy` 等特殊门操作
- 基本的模拟器初始化和状态验证

#### test_demos.py

示例端到端测试：

- `originq_dummy` 模式的完整工作流：创建配置 → 构建线路 → 提交任务 → 获取结果
- 验证示例代码可正确运行

## CI 集成

项目有两套 CI workflow 涉及测试：

### 1. Build-and-test（`build_and_test.yml`）

- **触发**：push/PR 到 main
- **环境**：Ubuntu（gcc/clang）+ Windows（MSVC）
- **内容**：C++ 后端编译 + 构建验证

### 2. Pytest Coverage（`pytest_coverage.yml`）

- **触发**：push/PR 到 main
- **环境**：Ubuntu + Python 3.11
- **内容**：`pytest qpandalite/test/ --cov=qpandalite -v`
- **已知 deselect**：`test_random_qasm_compare_density_operator`（density matrix 后端 crx/crz/cy 已知 bug）
- **产出**：`coverage.xml` artifact

## 已知限制

1. **density matrix 后端 bug**：`crx`、`crz`、`cy` 门在多门组合时结果不正确，相关测试（`test_random_qasm_compare_density_operator`）在 CI 中被 deselect
2. **外部依赖**：随机回归测试需要 `qiskit`、`qiskit-aer`、`qutip`、`scipy`，不在默认安装范围内
3. **test_result_adapter / test_general**：当前测试内容较简单，主要验证导入和基本功能，未覆盖全部 API
4. **transpiler 测试**：仅覆盖 `plot_time_line`，未覆盖 `qiskit_transpile` 等转译功能
5. **task 模块**：`test_task_adapters.py` 在 `qpandalite/test/` 中，但需要 mock HTTP，CI 环境可能不完整覆盖

## 未来改进方向

- 补充 `analyzer` 模块的测试覆盖（expectation 计算、结果适配器完整 API）
- 补充 `transpiler` 模块测试（qiskit 转译、电路绘制）
- 增加 `circuit_builder` 的边界用例测试
- 密度矩阵 bug 修复后取消 CI deselect
- 引入 property-based testing（如 hypothesis）增强随机测试覆盖率
