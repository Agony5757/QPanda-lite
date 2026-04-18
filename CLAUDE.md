# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Workflow

The `main` branch is protected — never push directly to it. Always:

1. Create a feature branch from `main`
2. Commit changes and push to the remote branch
3. Open a pull request targeting `main`
4. Wait for review and approval before merging

## Project Overview

QPanda-lite is a Python-native quantum programming framework for NISQ devices. It provides circuit construction, simulation (local and cloud), and result analysis. The core is pure Python with an optional C++ simulation backend via pybind11.

## Build Commands

```bash
# Pure Python install (no C++ dependencies)
pip install . --no-cpp

# Full install with C++ simulator
# Requirements: git submodules, CMake >= 3.26, C++ compiler with C++17 support
git clone --recurse-submodules https://github.com/Agony5757/QPanda-lite.git

# If system CMake is < 3.26, install newer version via pip first:
pip install cmake --upgrade

# For development: editable install with C++ extension
# Use --no-build-isolation to ensure pip cmake (not system cmake) is used
pip install -e . --no-build-isolation

# For production install (uses build isolation, requires CMake >= 3.26 in PATH)
pip install .
```

### CMake Requirement

The C++ backend requires CMake >= 3.26. Most Linux distributions ship older versions (e.g., Ubuntu 22.04 has cmake 3.22). For local development, install a newer cmake via pip:

```bash
pip install cmake --upgrade
```

This installs cmake to `~/.local/bin/` or the Python bin directory, which must be in PATH before the system cmake for editable installs with `--no-build-isolation`.

## Testing

```bash
# All tests
pytest qpandalite/test/ -v

# Single test file
pytest qpandalite/test/test_simulator.py -v

# Single test function
pytest qpandalite/test/test_simulator.py -v -k "test_function_name"
```

Test files follow `test_*.py` naming. Test classes: `Test*` or `RunTest*`. Test functions: `test_*` or `run_test_*`.

## Linting & Formatting

```bash
ruff check .          # lint
ruff format .         # format
ruff check . --fix    # auto-fix lint issues
```

Ruff config: line length 120, target Python 3.10. Rules: E, F, W, I, N, UP, B, C4, SIM. E501 and physics naming conventions (N801/N803/N806) are intentionally ignored.

Pre-commit hooks are configured (ruff lint + format, YAML check, trailing whitespace).

## Architecture

### Core Flow: Circuit -> Simulator/Backend -> Result

1. **Circuit Builder** (`qpandalite/circuit_builder/`): The `Circuit` class provides a fluent API for constructing quantum circuits. It outputs OriginIR or OpenQASM 2.0 format strings. Gate definitions live in `opcode.py` (logical gate list), `originir_spec.py` (OriginIR gate syntax), and `qasm_spec.py` (QASM gate syntax).

2. **Simulators** (`qpandalite/simulator/`): Local simulation backends that consume OriginIR or QASM strings.
   - `OriginIR_Simulator` — primary simulator supporting statevector, density matrix, and noisy simulation
   - `QASM_Simulator` — OpenQASM 2.0 simulator
   - `qpandalite_cpp` — C++ extension (optional, pybind11)

3. **Parsers** (`qpandalite/originir/`, `qpandalite/qasm/`): Parse OriginIR and OpenQASM 2.0 assembly strings into structured representations.

4. **Cloud Task Submission** (`qpandalite/task/`): Adapter pattern for submitting circuits to quantum cloud platforms. Each provider (OriginQ, Quafu, IBM) has an adapter under `task/adapters/`. Configuration is via environment variables. The `task_manager` module provides a unified API (`submit_task`, `query_task`, `wait_for_result`).

5. **Transpiler** (`qpandalite/transpiler/`): Converts between Qiskit circuits and OriginIR format.

6. **Analyzer** (`qpandalite/analyzer/`): Post-processing tools for measurement results — expectation values, measurement tomography, state tomography, etc.

### C++ Backend

`QPandaLiteCpp/` contains the C++ simulation backend compiled as a pybind11 extension (`qpandalite_cpp`). Dependencies (pybind11 v2.13.6, fmt) are git submodules under `QPandaLiteCpp/Thirdparty/`. The `CMakeExtension` class in `setup.py` handles CMake-based compilation. Building without C++ uses `pip install . --no-cpp`.

## Releasing

The package version is automatically managed by [setuptools_scm](https://setuptools-scm.readthedocs.io/), which extracts the version from git tags. The version is determined at build time from the latest git tag matching `v*`.

To release a new version:

1. Ensure all changes are committed and merged to `main`
2. Tag the release: `git tag vX.Y.Z` (the tag **must start with `v`**)
3. Push the tag: `git push origin --tags`

Pushing a `v*` tag triggers `pypi-publish.yml`, which builds wheels (Linux manylinux + Windows, Python 3.10–3.13) with the C++ extension via `cibuildwheel` and publishes them to PyPI using Trusted Publishing (OIDC). No manual version bump is needed — the version is automatically extracted from the git tag.

## Known Issues

- System cmake on Ubuntu 22.04 (cmake 3.22) is too old for building the C++ extension. Install via `pip install cmake --upgrade` and use `pip install -e . --no-build-isolation` for development.
