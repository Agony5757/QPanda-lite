# QPanda-lite 安装

## 从 pip 安装

```bash
pip install qpandalite
```

## 从 conda 安装

```bash
conda install -c conda-forge qpandalite
```

## 安装验证

安装完成后，运行以下命令确认安装成功：

```bash
python -c "import qpandalite; print(qpandalite.__version__)"
```

若能打印出版本号（如 `0.200.0`），说明安装成功。

## 从源码构建

### 平台要求

- **操作系统**：跨平台，支持 Windows、Linux、macOS
- **Python**：>= 3.8, <= 3.13
- **C++ 编译器**：支持 C++17（MSVC / gcc / clang）
- **CMake**：>= 3.1

### 获取源码

```bash
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
```

### 克隆子模块（C++ 模拟器）

QPanda-lite 的 C++ 模拟器作为 Git 子模块存在。**首次克隆后必须初始化子模块**，否则 C++ 模拟器不会被包含：

```bash
git clone --recurse-submodules https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
```

如果克隆时忘记加 `--recurse-submodules`，后续可以补上：

```bash
git submodule update --init --recursive
```

### 构建并安装

```bash
# 完整安装（含 C++ 模拟器，需要 CMake）
pip install .

# 纯 Python 版本（不需要 C++ 编译环境）
pip install . --no-cpp

# 开发模式（可编辑源码）
pip install -e .
```

### 构建 C++ 扩展常见问题

**Q：编译时报 `CMake could not find...`**
> 确保 CMake 已安装并加入 PATH。Windows 上可使用 [CMake 官方安装包](https://cmake.org/download/)。

**Q：编译时报 `fatal error: pybind11/pybind11.h: No such file`**
> 确保已执行 `git clone --recurse-submodules`，pybind11 子模块未初始化会导致此错误。运行 `git submodule update --init --recursive` 后重新安装。

**Q：如何确认 C++ 模拟器已正确安装？**
> 安装后运行 `python -c "from QPandaLiteCpp import *; print('C++ 模拟器正常')"`。若无声出输出说明 C++ 扩展未安装成功。

## 额外依赖

### OriginQ 平台

```bash
pip install quafu
```

### Quafu 平台

```bash
pip install pyquafu
```

### IBM 平台

```bash
pip install qiskit
pip install qiskit-ibm-provider
pip install qiskit-ibmq-provider
```

## 构建文档

```bash
cd docs
pip install -r requirements.txt
make html
```

## 已知问题 {#known-issues}

- **`crx`/`crz`/`cy` 受控旋转门在 density matrix 后端存在 bug**：多门组合使用时计算结果错误，单门测试正常。测试带噪声模拟或 density matrix 后端时，应避免使用这三个门，或使用 `cry` 代替 `cy`。
