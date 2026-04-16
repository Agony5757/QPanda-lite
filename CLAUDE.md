# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QPanda-lite is a Python-native quantum programming framework for NISQ devices. It provides circuit construction, simulation (local and cloud), and result analysis. The core is pure Python with an optional C++ simulation backend via pybind11.

## Build Commands

```bash
# Pure Python install (no C++ dependencies)
pip install . --no-cpp

# Full install with C++ simulator (requires git submodules and CMake >= 3.26)
git clone --recurse-submodules https://github.com/Agony5757/QPanda-lite.git
pip install .

# Editable install
pip install -e .
```

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

Ruff config: line length 120, target Python 3.9. Rules: E, F, W, I, N, UP, B, C4, SIM. E501 and physics naming conventions (N801/N803/N806) are intentionally ignored.

Pre-commit hooks are configured (ruff lint + format, YAML check, trailing whitespace).

## Architecture

### Core Flow: Circuit -> Simulator/Backend -> Result

1. **Circuit Builder** (`qpandalite/circuit_builder/`): The `Circuit` class provides a fluent API for constructing quantum circuits. It outputs OriginIR or OpenQASM 2.0 format strings. Gate definitions live in `opcode.py` (logical gate list), `originir_spec.py` (OriginIR gate syntax), and `qasm_spec.py` (QASM gate syntax).

2. **Simulators** (`qpandalite/simulator/`): Local simulation backends that consume OriginIR or QASM strings.
   - `OriginIR_Simulator` — primary simulator supporting statevector, density matrix, and noisy simulation
   - `QASM_Simulator` — OpenQASM 2.0 simulator
   - `qpandalite_cpp` — C++ extension (optional, pybind11)

3. **Parsers** (`qpandalite/originir/`, `qpandalite/qasm/`): Parse OriginIR and OpenQASM 2.0 assembly strings into structured representations.

4. **Cloud Task Submission** (`qpandalite/task/`): Adapter pattern for submitting circuits to quantum cloud platforms. Each provider (OriginQ, Quafu, IBM) has its own adapter and configuration module under `task/adapters/`, `task/ibm/`, `task/quafu/`, `task/origin_qcloud/`.

5. **Transpiler** (`qpandalite/transpiler/`): Converts between Qiskit circuits and OriginIR format.

6. **Analyzer** (`qpandalite/analyzer/`): Post-processing tools for measurement results — expectation values, measurement tomography, state tomography, etc.

### C++ Backend

`QPandaLiteCpp/` contains the C++ simulation backend compiled as a pybind11 extension (`qpandalite_cpp`). Dependencies (pybind11 v2.13.6, fmt) are git submodules under `QPandaLiteCpp/Thirdparty/`. The `CMakeExtension` class in `setup.py` handles CMake-based compilation. Building without C++ uses `pip install . --no-cpp`.

## Known Issues

- `crx`/`crz`/`cy` gates produce incorrect results with the density matrix backend when combined with multiple gates. Avoid these in noisy simulation.
- `controlled_by` simulation is incorrect with `backend='density_operator'` / `backend='density_operator_qutip'`.
