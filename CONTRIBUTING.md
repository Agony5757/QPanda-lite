# Contributing to QPanda-lite

Thank you for your interest in contributing to QPanda-lite! This document outlines how you can get involved and help improve the project.

## Environment Setup

### Prerequisites

- Python 3.9 – 3.12
- Git

### Clone & Install

```bash
git clone https://github.com/Agony5757/QPanda-lite.git
cd QPanda-lite
pip install -e .
```

For development dependencies (testing, linting):

```bash
pip install -e ".[dev]"   # if a [dev] extras section is defined
# otherwise manually install:
pip install pytest ruff pre-commit
```

Install pre-commit hooks:

```bash
pre-commit install
```

## Branch Naming

Use descriptive prefix branches:

| Prefix | Use case |
|--------|----------|
| `feat/<description>` | New features |
| `fix/<description>` | Bug fixes |
| `ci/<description>` | CI/CD changes |
| `docs/<description>` | Documentation updates |
| `refactor/<description>` | Code refactoring (no behavior change) |

Examples: `feat/add-noise-simulator`, `fix/gate-depth-calculation`

## Commit Message Format

We recommend [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**

- `feat` – new feature
- `fix` – bug fix
- `docs` – documentation only
- `style` – formatting, missing semicolons, etc. (no code change)
- `refactor` – code change that neither fixes a bug nor adds a feature
- `test` – adding or correcting tests
- `ci` – CI/CD configuration

**Examples:**

```
feat(simulator): add depolarizing noise model
fix(circuit): correct gate decomposition order
docs(api): clarify Measure result return type
ci: add coverage reporting to GitHub Actions
```

## Development Workflow

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** — write code, add tests, update docs.

3. **Run checks locally** before pushing:
   ```bash
   ruff check .
   ruff format .
   pytest
   pre-commit run --all-files
   ```

4. **Commit** your changes with a clear message.

5. **Push** and open a Pull Request:
   ```bash
   git push -u origin feat/your-feature-name
   ```

## Pull Request Process

1. Open a PR against `main` with a clear title and description.
2. Fill in the PR template (if one exists).
3. Ensure all CI checks pass.
4. Request a review from a maintainer.
5. Once approved, a maintainer will merge your PR.

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix and format
ruff format .
```

Run these before committing. The pre-commit hook will also run them automatically.

## Testing

Run the test suite with [pytest](https://pytest.org/):

```bash
pytest
```

If the project uses [tox](https://tox.wiki/):

```bash
tox
```

## Questions?

If you have questions or need help, feel free to open an issue for discussion.
