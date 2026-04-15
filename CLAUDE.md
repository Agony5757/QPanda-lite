# CLAUDE.md

本文件为未来运行在本仓库中的 Claude Code (claude.ai/code) 实例提供指导。

## Agent 行为准则（必读）

- **Python 环境优先级**：Pixi > uv > python/python3。本仓库当前没有 `pixi.toml`，若将来加了就改走 Pixi；临时脚本优先 `uv run`。
- **项目依赖走 uv，命令选择**：
  - 安装/同步项目本身（读 `pyproject.toml` + 触发 CMake 扩展构建）：**`uv sync`**。
  - 新增运行时依赖：**`uv add <package>`**（会写入 `pyproject.toml` 的 `[project.dependencies]`）。
  - 新增开发依赖：**`uv add --dev <package>`**（写入 `[dependency-groups.dev]`）。
  - 用可执行脚本：**`uv run <cmd>`**，不要手动 `source .venv/bin/activate`。
  - **不要用 `uv pip install ...`**——它绕过 `pyproject.toml`，会让环境和项目声明漂移。`uv pip` 仅用于 debug / 一次性探测。
- **临时依赖运行脚本**：新写的 Python 脚本依赖写进 PEP 723 元数据；给已有脚本临时加依赖用 `uv run --with <package> <script>`，不要污染项目环境。
- **需求不清时先问**：行为有分歧、边界不明确时调用 askQuestion，不要擅自决定或中断对话。
- **Git 纪律**：
  - 未经用户明确指令，禁止自动执行 `git add` 或 `git commit`。
  - 用户明确要求提交且暂存区为空：`git add .` → `git commit`。
  - 用户明确要求提交但暂存区非空：先说明暂存/工作区状况，再 askQuestion 确认提交范围，不要默认把所有改动一起提交。
- **删除文件用 `trash-put` 代替 `rm`**；误删恢复只能由用户手动 `trash-restore`，agent 不得自动执行。
- **优先用内置工具**（Read/Edit/Write/Glob/Grep）完成改动，不用 shell 命令绕过；批量改动前先和用户对齐。
- **先复用已有工具和 skills**，再考虑自己手写实现；需要 subagents 时按其描述的能力边界调用。
- **每次回复末尾追加"喝水水中"并配一个好玩的 emoji。**

## Git 远端与分支

- **`origin` = fork**：`git@github.com:TMYTiMidlY/QPanda-lite.git`（本仓库主开发者的 fork）。
- **upstream = 原仓库**：`Agony5757/QPanda-lite`——CI/PR 目标、发布源；本地需要拿上游更新时手动加 `upstream` remote 再 fetch（不要把 origin 改回原仓库）。
- **`fix/ci-r1r3r10`**：当前活跃 PR 分支（PR #139），CI 修复工作在此分支进行。
- **`fix/ci-main`**：CI 修复的基底分支（`3f271c8` = Agony5757 `main` 头），历史节点，不再直接开发。
- **`main`**：镜像 Agony5757 `main`，保持只跟随上游、不要直接改。
- **`ci-baseline`**：历史对账点（`d26e0b2`），**不要以它为修复基底**——它的"全绿"是 `python_functions = run_test_*` 限制收集造成的伪绿。

## 构建（Build）

项目使用 **setuptools（Python 打包） + CMake（C++ pybind11 扩展）**，在 `setup.py` 里通过自定义 `CMakeExtension` / `CMakeBuild` 粘合。

- **默认安装（含 C++ 模拟器）** —— 与 CI 一致：`pip install .`
  - CI **没有安装 Ninja**。Linux 回落到 CMake 默认生成器 Unix Makefiles + `gcc`/`g++`；Windows 用 MSVC 生成器 + MSBuild。保持一致，**不要引入 Ninja 依赖**。
  - **本地必须手动拉 submodule**：`QPandaLiteCpp/Thirdparty/fmt` 和 `pybind11` 是 submodule，首次 clone 后不是自动初始化的，必须跑 `git submodule update --init --recursive`，否则 CMake 会报 `does not contain a CMakeLists.txt` 并 `Unknown CMake command "pybind11_add_module"`。CI 通过 `actions/checkout` 的 `submodules: 'true'` 自动处理。
- **纯 Python（跳过 C++）**：`pip install . --no-cpp` —— 该参数由 `setup.py` 自己消费。
- **可编辑开发安装**：`pip install -e .`
- **打 wheel**：`pip install .` → `python stubgen.py && python setup.py bdist_wheel`（复刻 `python_build_wheel.yml`）。

`stubgen.py` 负责重生成 C++ 扩展的 `.pyi` 存根；C++ API 改动后要跑一遍。

## 测试（Test）

测试约定不标准——**动测试前先读 `qpandalite/test/README.md`**。

当前 `pytest.ini` 收集规则（`main` 分支放宽后，历史 `ci-baseline` 更严）：

```ini
python_files   = test_*.py
python_classes = Test* RunTest*
python_functions = test_* run_test_*
```

- **被 `@qpandalite_test('<描述>')` 装饰的函数**命名为 `run_test_<feature>`，是正式测试。
- 未装饰的 `test_*` 辅助函数可能也会被 pytest 收集（`python_functions = test_* run_test_*`）——不要把内部辅助函数命名为 `test_*`，否则会被重复收集。
- 跑全部：`uv run pytest qpandalite/test/ -v`
- 跑单个：`uv run pytest qpandalite/test/test_general.py::run_test_general -v`
- 覆盖率（同 CI）：
  ```bash
  uv run pytest qpandalite/test/ \
    --cov=qpandalite --cov-report=term-missing -v \
    --deselect qpandalite/test/test_random_QASM.py::test_random_qasm_compare_density_operator
  ```
  `--deselect` 是故意的——C++ `density_operator` 后端 `crx`/`crz`/`cy` 有已知 bug，该测试会失败（见 `已知问题.md`）。

## 代码风格（Lint / Format）

- `ruff check .` 和 `ruff format .`（配置在 `pyproject.toml`，line-length 120，target py39）。
- `pre-commit run --all-files` 跑全部钩子；用 `pre-commit install` 开启提交触发。
- 忽略了 `N801`/`N803`/`N806`，因为物理代码会用单字母 / CapWords 标识符（`U`、`H`、`K`、`E`）——**不要去"修"这些**。

## 调试 / 修 bug 的通用原则

从本仓库 CI 修复过程中提炼的可长期复用的规则：

- **先读 traceback + 代码，再定性**：测试和库都可能是错的。"失败 ≠ 库错"——测试期望值可能是 copy-paste 遗留的错误；"通过 ≠ 正确"——对称态（如 GHZ）会掩盖位序 bug。改库之前先手推一个最小例子的正确结果，再和测试期望对照。

- **bit / tensor 顺序踩坑**：
  - `QASM_Simulator` / `OriginIR_Simulator` 的 outcome 整数是 **LSB-first**：bit `i` = qubit `i` 的测量结果。
  - `qt.tensor(A, B)` 中 A 占 **MSB 子系统**，B 占 LSB。密度矩阵 index 按 LSB-first 编码，因此重建时需从后往前 tensor（qubit n-1 最左）。
  - 遇到"对角线对、off-diagonal 全乱"先怀疑 kron/tensor 顺序，再查 bit 提取方式。

- **非对称态 smoke test**：用 `|01⟩`（qubit 0=0, qubit 1=1）之类非对称态验证 tomography / shadow，比 GHZ 更早暴露位序 bug（GHZ 对换 qubit 0 和 qubit 2 对称，容易掩盖问题）。

- **shadow / tomography 类随机估计量的修法顺序**：
  1. 先确认单比特反演公式正确（期望值对）
  2. 再分析方差来源（basis-selection variance、shots noise 各占多少）
  3. 最后选估计器（pure mean / stratified sampling / MoM）
  顺序不能颠倒；MoM 对单个 Pauli 的 sample complexity 不比 pure mean 好，它的收益是同时估多个 Pauli 时的 uniform tail bound。

## 架构（Architecture）

QPanda-lite 是一个透明的、Python 原生的量子编程框架，数据流向：

```
用户代码 ──▶ Circuit (circuit_builder) ──▶ 文本 IR (OriginIR / OpenQASM 2.0)
                                              │
                         ┌────────────────────┼─────────────────────┐
                         ▼                    ▼                     ▼
                 originir / qasm          simulator/*          task/* (云端)
                 parser → opcodes        后端执行            submit / query
                                              │                     │
                                              ▼                     ▼
                                      analyzer（期望、结果适配、绘图）
```

单个文件看不全的跨层关键点：

- **Circuit → IR → opcodes → simulator**：`circuit_builder/qcircuit.py` 生成 OriginIR / QASM 文本；`circuit_builder/opcode.py` 是内部归一化形式；`originir/`、`qasm/` 把文本解析回 opcodes；`simulator/opcode_simulator.py` 是所有高层模拟器（`originir_simulator.py`、`qasm_simulator.py`、QuTiP 实现）共用的**唯一执行核心**。新增一个门必须**横穿**：`circuit_builder` spec → IR parser → opcode 定义 → C++/Python 模拟器，一层都不能漏。
- **模拟器后端**：`OriginIR_Simulator` / `QASM_Simulator` 通过 `backend=` 选 `statevector`、`density_operator`（Python）、`density_operator_qutip`、或 C++ 的 `qpandalite_cpp`。已知坏掉：密度矩阵后端的 `crx`/`crz`/`cy` + `controlled_by`（见 README "Known Issues" 和 `已知问题.md`）——别写"它们应该是对的"的测试。
- **Transpiler**：`transpiler/` 做 Qiskit ↔ OriginIR 的双向桥（有些后端 / benchmark 是 Qiskit 原生）；`translate_qasm2_oir.py` 处理 OpenQASM 2 ↔ OriginIR。
- **云端 task 系统**（`task/`）：厂商子包（`originq`、`origin_qcloud`、`originq_dummy`、`quafu`、`ibm`）共用 `adapters/` + `task_utils.py` + `platform_template/` 做 submit/poll/结果适配。各厂商的配置在 `qcloud_config/`，从 `qcloud_config_template/` 初始化。**`originq_dummy` 是本地 stand-in**，测试 / 示例优先用它，不要打真云。
- **Analyzer**：`analyzer/expectation.py` 从原始 shot 字典算 Pauli 期望；`result_adapter.py` 把各厂商结果格式归一化，让 analyzer 对所有后端表现一致。

## 文档索引

项目内有多个 md 文件，按用途分类：

### 顶层
- `README.md` —— 项目介绍、安装、快速示例、已知问题
- `CONTRIBUTING.md` —— 分支命名、Conventional Commits、PR 流程、代码风格
- `CODE_OF_CONDUCT.md` —— 行为准则（Contributor Covenant）
- `CLAUDE.md` —— 本文件
- `已知问题.md` —— 当前未关闭的 bug / 性能欠账（含 R10 C++ 密度矩阵、CircuitControlContext 设计缺陷等）

### 测试
- `qpandalite/test/README.md` —— **测试约定规范**（`@qpandalite_test` 装饰器、`run_test_*` 命名、pytest 收集规则）

### Sphinx 文档（`docs/source/`，对应 readthedocs 站点）
- **Guide**（入门指南）：`guide/installation.md`、`guide/quickstart.md`、`guide/circuit.md`、`guide/originir.md`、`guide/qasm.md`、`guide/simulation.md`、`guide/submit_task.md`、`guide/testing.md`
- **Advanced**（进阶）：`advanced/circuit_analysis.md`、`advanced/noise_simulation.md`、`advanced/opcode.md`
- **Algorithm**（算法说明）：`algorithm/` 下 `amplitude_estimation`、`deutsch-jozsa`、`dicke_state`、`entangled_states`、`grover`、`grover_oracle`、`hadamard_superposition`、`qaoa`、`qft`、`qpe`、`rotation_prepare`、`shadow_tomography`、`state_tomography`、`thermal_state`、`vqd`、`vqe`，共 16 个

### 示例（`examples/`）
- `examples/README.md` —— 示例导航总入口
- `examples/getting-started/README.md`、`examples/circuits/README.md` —— 分类入口
- 算法示例说明：`examples/algorithms/grover.md`、`qaoa.md`、`qpe.md`、`vqe.md`

涉及用户侧 API / 算法使用时，先查 `docs/source/guide/` 与 `docs/source/algorithm/`；涉及可运行脚本时，进 `examples/`。

## 相关量子软件参考

本项目在 transpiler / 模拟器后端 / 兼容性测试中与以下外部框架有交互，查语义、对齐行为时从这里进：

- **QPanda2**（本源量子，C++ + pyqpanda；OriginIR 上游参考实现）
  - 源码：<https://github.com/OriginQ/QPanda-2>
  - 兄弟仓库：<https://github.com/OriginQ/QPanda>
  - 文档：仓库内 `QPanda-2.Documentation/`，英文站 <https://qpanda-tutorial.readthedocs.io/>
- **Qiskit**（IBM；`transpiler/` 做 Qiskit ↔ OriginIR 双向桥）
  - 组织：<https://github.com/qiskit>
  - 文档仓库：<https://github.com/Qiskit/documentation>
  - 在线文档：<https://docs.quantum.ibm.com/guides>
- **QuTiP**（密度矩阵后端 `density_operator_qutip` 依赖）
  - 源码：<https://github.com/qutip/qutip>
  - 文档：<https://qutip.org/documentation.html> · <https://qutip.readthedocs.io/>
- **PennyLane**（Xanadu；可微分量子编程 / QML 事实标准）
  - 源码：<https://github.com/PennyLaneAI/pennylane>
  - 文档：<https://pennylane.ai/> · <https://docs.pennylane.ai/>
- **Cirq**（Google；NISQ 电路 + 硬件噪声研究向）
  - 源码：<https://github.com/quantumlib/Cirq>
  - 文档：<https://quantumai.google/cirq>

## 本地复刻 CI

push / PR 触发的 workflow 共 **3 条**（`pypi-publish.yml` 只在 release/tag 触发，不算）。本地一次跑通以下命令就等价于把它们全过一遍。当前测试状态以 `已知问题.md` 为准，CI 目标是对齐 Agony5757/main 全绿。

### 本地 uv / CI pip 双轨（必读）

- **本地用 uv，CI 用 pip**，两条工具链并存，不要改 CI 去用 uv。理由：uv 在 CI 上要钉版本、要重写三条 workflow、要同步 `uv.lock` —— 引入 uv 会扩大 diff 范围、让定位 CI 问题变糊。
- `uv add --dev` 会修改 `pyproject.toml`（加 `[dependency-groups.dev]`）并生成 `uv.lock`。这两份文件 **CI 当前不消费**，但留在仓库里无害（`pip install .` 读不到 `dependency-groups`）。要不要把 `uv.lock` 提交、要不要把 `[dependency-groups.dev]` 改成 `[project.optional-dependencies]`——保留开放，动之前问用户。
- 临时跑 pip 复刻 CI 本身：`python3 -m venv .venv-pip && .venv-pip/bin/pip install . pytest pytest-cov && .venv-pip/bin/pytest qpandalite/test/ -v`。

### Python 版本策略

- 项目 `requires-python = ">=3.9,<3.13"`。
- CI 各 workflow 的 Python 版本：
  - `Build-and-test`：**用 runner 自带 Python**（未 `setup-python`），ubuntu-latest 通常 3.10/3.12，windows-latest 通常 3.11/3.12 —— 随 runner 漂。
  - `Pytest Coverage`：**钉 3.11**。
  - `Build Python Wheels`：矩阵 **3.9 / 3.10 / 3.11 / 3.12**。
- 本地默认 `uv sync --python 3.12`（对齐 wheel 矩阵上限、也是当前系统版本）。要覆盖多版本本地验证：`uv sync --python 3.9` / `3.10` / `3.11` 依次重建 `.venv`。

### 一次性环境准备（只需做一次）

```bash
git submodule update --init --recursive   # 拉 fmt / pybind11（CI 自动、本地必须手动）
uv sync --python 3.12                     # 建 .venv + 装 pyproject 声明的依赖 + 触发 CMake 编译 qpandalite_cpp
uv add --dev pytest pytest-cov            # dev 依赖写进 [dependency-groups.dev]
```

基准本地实测：`uv sync` ~33s（含首次 CMake+gcc 编译与 58 个依赖下载），`uv add --dev` ~26s。缓存后重跑秒级完成。

### ① Build-and-test（`build_and_test.yml`，push + PR）

CI 矩阵 `{ubuntu, windows} × {gcc, clang, cl}`，本地只能覆盖本机的 gcc/clang。

```bash
uv run pytest qpandalite/test/ -v
```

### ② Pytest Coverage（`pytest_coverage.yml`，push + PR）

```bash
uv run pytest qpandalite/test/ \
  --cov=qpandalite --cov-report=term-missing --cov-report=xml -v \
  --deselect qpandalite/test/test_random_QASM.py::test_random_qasm_compare_density_operator
```

`--deselect` 有**历史上下文**，别想当然删掉：对象 `test_random_qasm_compare_density_operator`（`test_random_QASM.py:219`）比对 C++ `density_operator` 后端与 QuTiP 的密度矩阵，**会失败**（C++ 后端 `crx`/`crz`/`cy` 有已知 bug，见 `已知问题.md`）。修 C++ 实现后才能删掉 deselect。

本地也会生成 `coverage.xml`。

### ③ Build Python Wheels（`python_build_wheel.yml`，push + workflow_dispatch）

CI 用 `{ubuntu, windows} × Python 3.9–3.12` 矩阵，**不跑 pytest，只打 wheel**。

```bash
uv run python stubgen.py
uv run python setup.py bdist_wheel
# 产物在 dist/*.whl
```

### 只跑一部分测试

- 按文件：`uv run pytest qpandalite/test/test_general.py -v`
- 按单个测试函数：`uv run pytest qpandalite/test/test_general.py::run_test_general -v`
- 按关键字匹配名字：`uv run pytest qpandalite/test/ -k "originir_parser"`
- 遇到失败快停：加 `-x`；跑上次失败的：加 `--lf`；只收集不执行：加 `--collect-only`
- 关闭警告噪音：加 `-W ignore`（本项目 15k+ 行 warning 主要来自 numpy/qiskit 依赖）

## 贡献约定

出自 `CONTRIBUTING.md`：Conventional Commits（`feat(scope): …`、`fix(scope): …` 等）+ 分支前缀 `feat/`、`fix/`、`ci/`、`docs/`、`refactor/`。PR 目标 `main`。
