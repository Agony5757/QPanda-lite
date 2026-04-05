# Contributing to QPanda-lite

Thank you for your interest in contributing to QPanda-lite!

## Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/Agony5757/QPanda-Lite.git
cd QPanda-Lite

# Create a virtual environment (Python 3.9–3.12)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install in editable mode with all optional dependencies
pip install -e ".[full]"

# Install development dependencies
pip install pytest pytest-cov flake8 mypy isort black
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=qpandalite --cov-report=html

# Run specific test file
pytest qpandalite/test/test_originir_parser.py
```

## Building the C++ Extension (Optional)

```bash
# Requires CMake, a C++ compiler (g++ or clang++), and pybind11
pip install pybind11 cmake ninja

# Build with C++ support
python install setup.py build_ext --inplace

# Or build without C++ (pure Python simulator only)
pip install -e . --no-cpp
```

## Code Style

- **Formatting**: We use `black` for code formatting and `isort` for import sorting.
  ```bash
  black qpandalite/
  isort qpandalite/
  ```

- **Type checking**: We use `mypy` for static type checking.
  ```bash
  mypy qpandalite/
  ```

- **Linting**: We use `flake8`.
  ```bash
  flake8 qpandalite/
  ```

## Pre-commit Hooks

We recommend using pre-commit hooks to automatically check code before each commit:

```bash
pip install pre-commit
pre-commit install
```

## Submitting Changes

1. **Fork** the repository and create a branch from `main`.
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**. Follow the code style guidelines above.

3. **Write tests** for any new functionality.

4. **Ensure all tests pass**:
   ```bash
   pytest
   ```

5. **Commit your changes** with a clear commit message:
   ```bash
   git commit -m "Add feature: short description"
   ```

6. **Push to your fork** and submit a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Open a Pull Request against the `main` branch. Fill in the PR template with a clear description of your changes.

## Reporting Issues

- Search existing issues before creating a new one.
- For bugs, include a minimal reproducible example.
- For feature requests, explain the use case and expected behavior.

## Branch Policy

- `main` — stable, always releasable
- `feature/*` — work in progress for new features
- `fix/*` — work in progress for bug fixes

## License

By contributing to QPanda-lite, you agree that your contributions will be licensed under the Apache License 2.0.
