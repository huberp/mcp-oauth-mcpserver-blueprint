# Code Quality and Linting Guide

This document explains the code quality tools and linting setup for the MCP OAuth Server project.

## Overview

The project uses a modern Python code quality stack with automated enforcement:

- **Ruff**: Fast, all-in-one linter and formatter (replaces Black, Flake8, isort, and more)
- **mypy**: Static type checking
- **pytest**: Testing framework with coverage
- **pre-commit**: Automated git hooks for quality checks
- **EditorConfig**: Consistent formatting across editors
- **VS Code**: Integrated development environment with auto-formatting

## Quick Start

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest, pytest-cov, pytest-mock, pytest-asyncio (testing)
- ruff (linting and formatting)
- mypy (type checking)
- black (fallback formatter)

### 2. Set Up Pre-commit Hooks (Recommended)

```bash
pip install pre-commit
pre-commit install
```

Now quality checks run automatically before each commit!

### 3. Configure Your Editor

#### VS Code (Recommended)

1. Install recommended extensions (VS Code will prompt you):
   - Ruff (`charliermarsh.ruff`)
   - Python (`ms-python.python`)
   - EditorConfig (`editorconfig.editorconfig`)

2. Settings are already configured in `.vscode/settings.json`:
   - Auto-format on save
   - Auto-fix linting issues
   - Auto-organize imports

#### Other Editors

Install the EditorConfig plugin for your editor. The `.editorconfig` file ensures consistent formatting.

## Ruff Configuration

Ruff is configured in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # function calls in argument defaults
]
```

### Enabled Rules

- **E/W (pycodestyle)**: PEP 8 style violations
- **F (pyflakes)**: Logical errors like unused imports
- **I (isort)**: Import sorting
- **B (bugbear)**: Common bugs and design problems
- **C4 (comprehensions)**: Better list/dict/set comprehensions
- **UP (pyupgrade)**: Modern Python syntax

### Common Violations

1. **Trailing whitespace** (W291)
   ```python
   # Bad
   def hello():·
       pass
   
   # Good
   def hello():
       pass
   ```

2. **Whitespace in blank lines** (W293)
   ```python
   # Bad
   def hello():
       pass
   ····
   def world():
       pass
   
   # Good
   def hello():
       pass

   def world():
       pass
   ```

3. **Import sorting** (I001)
   ```python
   # Bad
   from myapp import config
   import json
   from datetime import datetime
   
   # Good (sorted: stdlib, third-party, first-party)
   import json
   from datetime import datetime

   from myapp import config
   ```

4. **Unused imports** (F401)
   ```python
   # Bad
   import json
   import secrets  # Never used
   
   # Good
   import json
   ```

5. **Exception chaining** (B904)
   ```python
   # Bad
   try:
       result = api_call()
   except Exception as e:
       raise ValueError(f"Failed: {e}")
   
   # Good
   try:
       result = api_call()
   except Exception as e:
       raise ValueError(f"Failed: {e}") from e
   ```

## Using Ruff

### Format Code

```bash
# Format all files
ruff format src/ tests/

# Check formatting without modifying
ruff format --check src/ tests/
```

### Lint Code

```bash
# Check for issues
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/

# Auto-fix including unsafe fixes (like removing whitespace)
ruff check --fix --unsafe-fixes src/ tests/
```

### In VS Code

With the Ruff extension installed:
- **Auto-format**: Save file (Ctrl+S / Cmd+S)
- **Manual format**: Shift+Alt+F (Windows) / Shift+Option+F (Mac)
- **Fix all**: Ctrl+. or Cmd+. then select "Fix all auto-fixable problems"

## Pre-commit Hooks

The `.pre-commit-config.yaml` file defines hooks that run before each commit:

### Hooks Included

1. **Ruff linter**: Checks and fixes linting issues
2. **Ruff formatter**: Formats code
3. **mypy**: Type checking
4. **Trailing whitespace**: Removes trailing spaces
5. **End-of-file fixer**: Ensures files end with newline
6. **YAML/JSON/TOML check**: Validates config files
7. **Large files check**: Prevents committing large files
8. **Merge conflict check**: Detects merge conflict markers
9. **Private key detection**: Prevents committing secrets
10. **Dockerfile linting**: Validates Dockerfile
11. **Shell script checking**: Validates shell scripts

### Usage

```bash
# Automatic: Just commit normally
git commit -m "Your message"

# Manual: Run on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate

# Skip hooks (not recommended)
git commit -m "Your message" --no-verify
```

## Type Checking with mypy

Type checking is configured in `pyproject.toml`:

```bash
# Run type checking
mypy src/

# In CI/CD
mypy src/ --strict
```

All functions must have type hints:

```python
# Good
def get_user(user_id: str) -> dict[str, Any]:
    return {"id": user_id}

# Bad (missing type hints)
def get_user(user_id):
    return {"id": user_id}
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mcp_server --cov-report=term-missing

# Run specific test
pytest tests/test_oauth_handler.py -v
```

## CI/CD Integration

GitHub Actions runs quality checks on every push:

```yaml
# .github/workflows/ci.yml
- name: Run linting with ruff
  run: ruff check src/ tests/

- name: Run type checking with mypy
  run: mypy src/

- name: Run tests with pytest
  run: pytest --cov=src/mcp_server
```

## EditorConfig

The `.editorconfig` file ensures consistent formatting:

```ini
[*.py]
indent_style = space
indent_size = 4
max_line_length = 100
trim_trailing_whitespace = true
insert_final_newline = true
```

This works in most modern editors with an EditorConfig plugin.

## Troubleshooting

### Pre-commit hooks failing

```bash
# Update hooks
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install --install-hooks

# Skip a specific hook
SKIP=mypy git commit -m "Your message"
```

### VS Code not formatting on save

1. Check that Ruff extension is installed
2. Verify `.vscode/settings.json` exists
3. Reload VS Code (Ctrl+Shift+P → "Reload Window")
4. Check output panel (View → Output → Ruff)

### Ruff conflicts with Black

Ruff's formatter is compatible with Black. If you have Black installed:

```bash
# Use Ruff instead
ruff format src/ tests/

# Remove Black (optional)
pip uninstall black
```

### Import sorting issues

Ruff sorts imports automatically:

```python
# Standard library
import json
import logging

# Third-party
from fastmcp import FastMCP
from starlette.requests import Request

# First-party
from .config import settings
from .oauth_handler import OAuthHandler
```

## Best Practices

1. **Always run pre-commit hooks**
   - Install with `pre-commit install`
   - Don't skip with `--no-verify` unless absolutely necessary

2. **Format on save in your editor**
   - Prevents formatting conflicts
   - Keeps code consistently styled

3. **Fix linting issues immediately**
   - Don't accumulate technical debt
   - Most issues auto-fix with `ruff check --fix`

4. **Use type hints everywhere**
   - Makes code self-documenting
   - Catches bugs early with mypy

5. **Test your changes**
   - Run `pytest` before committing
   - Maintain >80% code coverage

## Additional Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pre-commit Documentation](https://pre-commit.com/)
- [EditorConfig](https://editorconfig.org/)
- [PEP 8 Style Guide](https://pep8.org/)

## Summary

This project uses modern, automated code quality tools:

✅ **Ruff** for fast linting and formatting  
✅ **mypy** for type safety  
✅ **pre-commit** for automatic enforcement  
✅ **VS Code** integration for seamless development  
✅ **EditorConfig** for cross-editor consistency  

Set up takes 2 minutes, but saves hours of code review time!
