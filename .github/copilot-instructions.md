# GitHub Copilot Instructions for MCP OAuth Server

## Project Overview

This project is a Model Context Protocol (MCP) server with OAuth 2.1 authentication support, built in Python using FastMCP and Authlib. The server provides secure authentication for accessing third-party APIs (specifically GitHub) and is designed to be containerized with Docker.

## Code Style and Standards

### Python Style
- **Python Version**: Target Python 3.12
- **Formatting**: Use Black with 100 character line length
- **Linting**: Follow Ruff configuration in pyproject.toml
- **Type Hints**: All functions must have complete type hints
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Naming Conventions**:
  - Classes: PascalCase (e.g., `OAuthHandler`)
  - Functions/methods: snake_case (e.g., `get_authorization_url`)
  - Constants: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)
  - Private methods: prefix with underscore (e.g., `_internal_method`)

### Code Organization
- Keep modules focused and single-purpose
- Use dependency injection for testability
- Separate configuration, business logic, and I/O
- Follow the existing project structure

### Error Handling
- Use specific exception types
- Provide clear, actionable error messages
- Log errors with appropriate context
- Never suppress exceptions without explicit reason
- **ALWAYS use exception chaining**: Use `raise ... from err` or `raise ... from None`
  ```python
  # Good: Shows exception chain
  try:
      result = api_call()
  except Exception as e:
      raise ValueError(f"API call failed: {e}") from e
  
  # Bad: Hides the original exception
  try:
      result = api_call()
  except Exception as e:
      raise ValueError(f"API call failed: {e}")
  ```

### Code Quality Rules (Ruff)
The project uses Ruff for linting with the following enabled rules:
- **E/W**: pycodestyle errors and warnings (PEP 8 compliance)
- **F**: pyflakes (detect unused imports, undefined names, etc.)
- **I**: isort (import sorting)
- **B**: flake8-bugbear (common bugs and design problems)
- **C4**: flake8-comprehensions (better list/dict/set comprehensions)
- **UP**: pyupgrade (modern Python syntax)

Common violations to avoid:
- **No trailing whitespace** (W291)
- **No whitespace in blank lines** (W293)
- **Keep imports sorted** (I001) - stdlib, third-party, first-party
- **Remove unused imports** (F401)
- **Use exception chaining** (B904) - Always use `from e` or `from None`
- **Line length**: Maximum 100 characters (enforced by Black and Ruff)

## Testing Requirements

### Test Coverage
- Maintain >80% code coverage
- Write tests before implementing features (TDD)
- Use pytest for all tests
- Mock external services (HTTP calls, OAuth providers)

### Test Structure
- Place tests in `tests/` directory
- Mirror source structure in test files
- Use descriptive test names: `test_<what>_<when>_<expected>`
- Group related tests in classes if needed

### Test Fixtures
- Define fixtures in `conftest.py`
- Reuse fixtures across test files
- Mock environment variables for consistency

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mcp_server --cov-report=term-missing

# Run specific test markers
pytest -m unit
pytest -m integration
```

### MCP Server Testing and Validation

When developing MCP (Model Context Protocol) servers, always validate that the server correctly reports its capabilities:

#### Testing Tools
- Use the MCP Inspector CLI (`@modelcontextprotocol/inspector`) for automated testing
- Validate that all registered tools are correctly reported via `tools/list`
- Verify tool schemas, descriptions, and metadata are accurate
- Test that tools handle missing or invalid inputs gracefully

#### Testing Prompts
- Validate that all registered prompts are correctly reported via `prompts/list`
- Verify prompt descriptions and argument specifications
- Test prompt templates with various parameter combinations

#### Automated Testing
- Add GitHub Actions workflow for continuous MCP server validation
- Use `--cli` mode for non-interactive testing in CI/CD pipelines
- Generate summary reports showing available tools and prompts
- Store test results as artifacts for debugging

#### Local Testing
```bash
# Test tools
npx @modelcontextprotocol/inspector --cli --method tools/list python3 -m mcp_server.main

# Test prompts
npx @modelcontextprotocol/inspector --cli --method prompts/list python3 -m mcp_server.main

# Test resources (if applicable)
npx @modelcontextprotocol/inspector --cli --method resources/list python3 -m mcp_server.main
```

#### Best Practices
- Run MCP Inspector tests before every release
- Document all available tools and prompts in README
- Keep test output as artifacts for reference
- Validate server capabilities match documentation
- Test both success and error paths for all endpoints
- Ensure proper error messages are returned to clients

## Security Best Practices

### OAuth Implementation
- Always use PKCE for public clients
- Implement proper state parameter validation
- Never log or expose tokens
- Use secure token storage
- Implement token refresh logic

### Environment Variables
- Never hardcode secrets or credentials
- Use `.env` files for local development
- Validate all environment variables at startup
- Provide clear error messages for missing config

### Docker Security
- Run containers as non-root user
- Use minimal base images
- Keep dependencies updated
- Implement health checks
- Use multi-stage builds

## MCP Protocol Implementation

### Protocol Compliance
- **CRITICAL**: This project MUST comply with MCP Specification 2025-06-18 (LATEST)
- **Protocol Version**: Always use `2025-06-18` - this is the current latest specification
- **Specification URL**: https://modelcontextprotocol.io/specification/2025-06-18
- **Never use outdated protocol versions** like 2025-03-26 or earlier
- All code, documentation, and references must use the 2025-06-18 specification

### Server Structure
- Use FastMCP for high-level abstractions
- Register all prompts and tools properly
- Implement proper error handling in tools
- Provide clear descriptions for prompts/tools
- Follow MCP specification 2025-06-18 (LATEST)

### Prompts
- Provide clear, actionable prompt templates
- Include parameter descriptions
- Handle optional parameters gracefully

### Tools
- Define clear input schemas
- Validate all inputs
- Return structured, parseable output
- Handle authentication requirements
- Provide helpful error messages

## Development Workflow

### Code Quality Tools

#### Pre-commit Hooks (Recommended)
We use pre-commit hooks to automatically check code quality before commits:

```bash
# Install pre-commit hooks (one-time setup)
pip install pre-commit
pre-commit install

# Manually run on all files
pre-commit run --all-files
```

The pre-commit configuration includes:
- **Ruff**: Automatic linting and formatting
- **mypy**: Type checking
- **Trailing whitespace removal**
- **End-of-file fixes**
- **YAML/JSON/TOML validation**
- **Dockerfile linting**
- **Shell script validation**

#### VS Code Integration
For VS Code users, install the recommended extensions:
- **charliermarsh.ruff** - Ruff linter and formatter
- **ms-python.python** - Python support
- The `.vscode/settings.json` file is already configured for automatic formatting on save

#### Manual Checks
If not using pre-commit hooks, run these before committing:

1. **Format code**: `ruff format src/ tests/`
2. **Run linters**: `ruff check --fix src/ tests/`
3. **Run type checker**: `mypy src/`
4. **Run tests**: `pytest`
5. **Ensure 100% test pass rate**
6. **Check coverage is maintained**

### Adding New Features
1. Write tests first (TDD)
2. Implement minimal code to pass tests
3. Refactor for clarity and maintainability
4. Update documentation
5. Run full test suite

### Adding New Dependencies
1. Add to `pyproject.toml` under `dependencies` or `[project.optional-dependencies]`
2. Use version constraints appropriately
3. Test with clean virtual environment
4. Update requirements in Dockerfile if needed
5. Document why dependency is needed

## Common Patterns

### Async/Await
```python
# Preferred pattern for async functions
async def fetch_data() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

### Configuration
```python
# Use pydantic_settings for configuration
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    api_key: str
```

### Error Handling
```python
# Provide context in exceptions
try:
    result = await api_call()
except httpx.HTTPError as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise ValueError(f"Failed to fetch data: {str(e)}") from e
```

### Logging
```python
# Use appropriate log levels
logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

## File Templates

### New Module Template
```python
"""Brief module description.

Detailed explanation if needed.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ClassName:
    """Class description."""
    
    def __init__(self) -> None:
        """Initialize the class."""
        pass
    
    def method_name(self, param: str) -> str:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Return value description
            
        Raises:
            ExceptionType: When this exception is raised
        """
        return param
```

### Test File Template
```python
"""Tests for module_name."""

import pytest

from mcp_server.module_name import ClassName


@pytest.fixture
def instance() -> ClassName:
    """Create instance for testing."""
    return ClassName()


def test_method_name(instance: ClassName) -> None:
    """Test that method_name does what it should."""
    result = instance.method_name("test")
    assert result == "test"


@pytest.mark.asyncio
async def test_async_method() -> None:
    """Test async method."""
    result = await async_function()
    assert result is not None
```

## Documentation

### README Updates
- Keep README.md up to date with new features
- Include clear usage examples
- Update architecture diagrams if structure changes
- Document new environment variables

### Code Comments
- Write self-documenting code first
- Add comments for complex logic
- Explain "why" not "what"
- Keep comments up to date

### Docstrings
- Every public class, method, and function needs a docstring
- Use Google-style format
- Include type information in Args and Returns sections
- Document exceptions

## CI/CD

### GitHub Actions
- All tests must pass before merge
- Linting must pass
- Type checking must pass (warnings allowed)
- Docker build must succeed

### Pre-commit Checks
- Run locally before pushing
- Use provided scripts: `./scripts/test.sh`
- Fix issues before committing

## Docker

### Building Images
```bash
# Build locally
docker build -t mcp-oauth-server:latest .

# Build with docker-compose
docker-compose build
```

### Running Containers
```bash
# With docker-compose
docker-compose up

# Direct run
docker run --env-file .env -i mcp-oauth-server:latest
```

## Useful Commands

```bash
# Setup environment
./scripts/setup.sh          # or setup.ps1 on Windows

# Run tests
./scripts/test.sh           # or test.ps1 on Windows

# Run server locally
./scripts/run.sh            # or run.ps1 on Windows

# Build Docker image
./scripts/build-docker.sh   # or build-docker.ps1 on Windows

# Format code
black src/ tests/

# Check types
mypy src/

# Lint code
ruff check src/ tests/
```

## Getting Help

### Documentation
- Check `docs/RESEARCH.md` for implementation details
- Read MCP specification: https://modelcontextprotocol.io/
- Review FastMCP docs: https://fastmcp.wiki/

### Debugging
- Use Python debugger: `python -m pdb`
- Check logs for detailed error information
- Use verbose test output: `pytest -v`
- Enable debug logging: `LOG_LEVEL=DEBUG`

## Key Principles

1. **Security First**: Never compromise on security
2. **Test Everything**: Maintain high test coverage
3. **Clear Documentation**: Code should be self-explanatory
4. **Type Safety**: Use type hints everywhere
5. **Error Handling**: Fail gracefully with helpful messages
6. **Simplicity**: Keep it simple and maintainable
7. **Standards Compliance**: Follow MCP spec and OAuth 2.1 spec
8. **Performance**: Consider performance, but clarity first

## Project-Specific Notes

### OAuth Flow
- This project implements OAuth 2.1 with PKCE
- Authorization code flow is primary method
- Refresh tokens are supported
- State parameter is mandatory for CSRF protection

### GitHub API Integration
- API client is specifically built for GitHub API v3
- Requires authentication for most endpoints
- Rate limiting should be considered in future enhancements
- API version is specified in headers

### MCP Protocol
- Server uses stdio transport for communication
- Supports both prompts and tools
- Tools require OAuth authentication
- Prompts can be used without authentication

### Future Enhancements
- Add support for other OAuth providers
- Implement rate limiting
- Add caching for API responses
- Support for multiple concurrent users
- Web-based OAuth callback handler
- Token persistence across restarts

---

*Last Updated: 2025-10-23*
*Version: 1.0*