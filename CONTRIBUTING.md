# Contributing to QPanda-lite

Thank you for your interest in contributing to QPanda-lite!

## How to Contribute

### Reporting Issues

- Search existing issues before opening a new one.
- For bugs, please include a minimal reproducible example.
- For feature requests, please describe the use case and expected behavior.

### Pull Requests

1. **Fork** the repository and create a branch from `main`.
2. **Install development dependencies**:

   ```bash
   pip install -e ".[full]"
   pip install pre-commit
   pre-commit install
   ```

3. **Run tests** before submitting:

   ```bash
   pytest qpandalite/test/
   ```

4. **Write clear commit messages** and keep changes focused.

5. **Open a Pull Request** targeting the `main` branch.

### Code Style

- Follow [PEP 8](https://pep8.org/).
- Use meaningful variable and function names.
- Add docstrings to public functions and classes.
- Run `pre-commit run --all-files` before committing.

### Review Process

- Maintainers will review your PR as soon as possible.
- Please be responsive to feedback and willing to make changes.
