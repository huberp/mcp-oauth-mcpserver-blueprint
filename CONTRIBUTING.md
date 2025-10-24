# Contributing to MCP OAuth Server

Thank you for your interest in contributing to the MCP OAuth Server project! This document provides guidelines and best practices for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style and Standards](#code-style-and-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)
- [CI/CD Expectations](#cicd-expectations)
- [Getting Help](#getting-help)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

### Our Standards

- **Be Respectful**: Treat everyone with respect and consideration
- **Be Collaborative**: Work together to achieve the best outcomes
- **Be Professional**: Keep discussions focused and professional
- **Be Patient**: Help others learn and grow
- **Be Open**: Welcome feedback and different perspectives

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12** or higher
- **Git** for version control
- **Docker** (optional, for containerized development)
- **GitHub OAuth App credentials** (for testing OAuth functionality)

### Setting Up Your Development Environment

1. **Fork the Repository**
   ```bash
   # Visit https://github.com/huberp/n-eight-n and click "Fork"
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/n-eight-n.git
   cd n-eight-n
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/huberp/n-eight-n.git
   ```

4. **Set Up the Development Environment**
   
   **Linux/macOS:**
   ```bash
   ./scripts/setup.sh
   ```
   
   **Windows:**
   ```powershell
   .\scripts\setup.ps1
   ```
   
   This will:
   - Create a Python virtual environment
   - Install all dependencies (including dev dependencies)
   - Create a `.env` file from the template

5. **Configure OAuth Credentials**
   
   Edit `.env` file with your GitHub OAuth App credentials. See the [GitHub OAuth Setup Guide](docs/setup-auth-github.md) for detailed instructions.

6. **Verify Your Setup**
   ```bash
   # Run tests
   ./scripts/test.sh  # or test.ps1 on Windows
   ```

## Development Workflow

### Creating a Feature Branch

1. **Sync with Upstream**
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
   
   Branch naming conventions:
   - `feature/` for new features
   - `bugfix/` for bug fixes
   - `docs/` for documentation updates
   - `refactor/` for code refactoring
   - `test/` for test improvements

### Making Changes

1. **Write Tests First** (TDD Approach)
   - Write tests that define the expected behavior
   - Run tests to see them fail
   - Implement the minimal code to make tests pass
   - Refactor while keeping tests green

2. **Follow Code Style Guidelines**
   - See [Code Style and Standards](#code-style-and-standards) section
   - Run linters before committing

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=src/mcp_server
   
   # Run specific test file
   pytest tests/test_oauth_handler.py
   ```

4. **Verify Code Quality**
   ```bash
   # Linting
   ruff check src/ tests/
   
   # Type checking
   mypy src/
   
   # Format code
   black src/ tests/
   ```

### Testing Your Changes

#### Running Tests

```bash
# Run all tests
./scripts/test.sh  # or test.ps1 on Windows

# Run specific test markers
pytest -m unit
pytest -m integration

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_oauth_handler.py::test_generate_pkce_pair -v
```

#### MCP Server Testing

Test the MCP server using the MCP Inspector CLI:

```bash
# Test tools
npx @modelcontextprotocol/inspector --cli --method tools/list python3 -m mcp_server.main

# Test prompts
npx @modelcontextprotocol/inspector --cli --method prompts/list python3 -m mcp_server.main
```

#### Docker Testing

```bash
# Build Docker image
./scripts/build-docker.sh  # or build-docker.ps1 on Windows

# Run with docker-compose
docker-compose up

# Run directly
docker run --env-file .env -i mcp-oauth-server:latest
```

## Code Style and Standards

### Python Style Guidelines

We follow strict Python coding standards to maintain code quality:

- **Python Version**: Python 3.12
- **Formatting**: Black with 100 character line length
- **Linting**: Ruff (configured in pyproject.toml)
- **Type Hints**: All functions must have complete type hints
- **Docstrings**: Google-style docstrings for all public functions and classes

### Naming Conventions

- **Classes**: PascalCase (e.g., `OAuthHandler`)
- **Functions/Methods**: snake_case (e.g., `get_authorization_url`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)
- **Private Methods**: Prefix with underscore (e.g., `_internal_method`)
- **Module Names**: lowercase with underscores (e.g., `oauth_handler.py`)

### Code Organization

- **Keep modules focused**: Each module should have a single, clear purpose
- **Use dependency injection**: Makes code more testable
- **Separate concerns**: Configuration, business logic, and I/O should be separate
- **Follow existing structure**: Maintain consistency with the current project layout

### Error Handling

- **Use specific exception types**: Don't catch generic exceptions
- **Provide clear error messages**: Make errors actionable
- **Log with context**: Include relevant information for debugging
- **Never suppress exceptions**: Unless you have a specific reason and document it

### Documentation

- **Docstrings**: Every public class, method, and function needs a docstring
- **Google-style format**: Use Google-style docstrings consistently
- **Type information**: Include type information in Args and Returns sections
- **Document exceptions**: List exceptions that can be raised

Example:
```python
def fetch_user_data(user_id: str) -> dict[str, Any]:
    """
    Fetch user data from the API.
    
    Args:
        user_id: The unique identifier for the user
        
    Returns:
        Dictionary containing user information
        
    Raises:
        ValueError: If user_id is empty or invalid
        APIError: If the API request fails
    """
    pass
```

## Testing Requirements

### Test Coverage

- **Maintain >80% coverage**: All new code should have tests
- **Test-Driven Development**: Write tests before implementing features
- **Use pytest**: All tests use pytest framework
- **Mock external services**: Mock HTTP calls, OAuth providers, etc.

### Test Structure

- **Location**: Place tests in `tests/` directory
- **Naming**: Mirror source structure in test files
- **Test names**: Use descriptive names: `test_<what>_<when>_<expected>`
- **Fixtures**: Define reusable fixtures in `conftest.py`

### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_oauth_handler_initialization():
    """Test OAuthHandler initialization."""
    pass

@pytest.mark.integration
def test_oauth_flow_end_to_end():
    """Test complete OAuth flow."""
    pass

@pytest.mark.slow
def test_large_dataset_processing():
    """Test processing of large datasets."""
    pass
```

### Writing Good Tests

```python
# Good test example
def test_generate_pkce_pair_returns_valid_values():
    """Test that PKCE pair generation returns valid verifier and challenge."""
    verifier, challenge = OAuthHandler.generate_pkce_pair()
    
    # Verify verifier length and characters
    assert len(verifier) == 128
    assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' for c in verifier)
    
    # Verify challenge is base64url encoded
    assert challenge is not None
    assert len(challenge) > 0
```

## Pull Request Process

### Before Submitting a Pull Request

1. **Ensure all tests pass**
   ```bash
   ./scripts/test.sh
   ```

2. **Run code quality checks**
   ```bash
   ruff check src/ tests/
   mypy src/
   black src/ tests/
   ```

3. **Update documentation**
   - Update README.md if you added features
   - Update docstrings for changed functions
   - Add or update relevant documentation in `docs/`

4. **Add tests for new features**
   - Unit tests for all new functions
   - Integration tests for new workflows
   - Ensure >80% coverage is maintained

### Submitting a Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

2. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with:
     - Clear description of changes
     - Link to related issues
     - Testing performed
     - Screenshots (for UI changes)

3. **PR Title Format**
   - Use clear, descriptive titles
   - Prefix with type: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
   - Example: `feat: Add support for OAuth token refresh`

4. **PR Description Should Include**
   - **What**: What changes were made
   - **Why**: Why these changes were necessary
   - **How**: How the changes work
   - **Testing**: What testing was performed
   - **Screenshots**: For any UI/output changes

### Code Review Process

- **Be responsive**: Respond to review comments promptly
- **Be open to feedback**: Reviews help improve code quality
- **Make requested changes**: Address all review comments
- **Keep PRs focused**: One feature/fix per PR when possible
- **Be patient**: Reviewers are volunteers with limited time

### After PR Approval

- **Squash commits**: If requested by maintainers
- **Wait for CI**: Ensure all CI checks pass
- **Merge**: Maintainers will merge approved PRs

## Commit Message Guidelines

We follow conventional commit message format for clarity and automated changelog generation.

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no code change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
# Good commit messages
git commit -m "feat(oauth): Add PKCE support for OAuth 2.1"
git commit -m "fix(api): Handle rate limiting in GitHub API client"
git commit -m "docs(readme): Update installation instructions"
git commit -m "test(oauth): Add tests for token refresh flow"

# Multi-line commit
git commit -m "feat(server): Add MCP sampling support

Add analyze_code_with_llm tool that uses MCP sampling
capability to request LLM analysis from the client.

Closes #42"
```

### Best Practices

- **Use imperative mood**: "Add feature" not "Added feature"
- **Keep subject line under 72 characters**: Be concise
- **Separate subject from body**: Use blank line
- **Explain what and why**: Not how (code shows how)
- **Reference issues**: Use "Closes #123" or "Fixes #123"

## CI/CD Expectations

### Automated Checks

All pull requests must pass the following automated checks:

1. **Unit Tests**
   - Run on Ubuntu, macOS, and Windows
   - Must pass on all platforms
   - Coverage must be >80%

2. **Integration Tests**
   - Run on Ubuntu
   - Must pass all integration tests

3. **Linting**
   - Ruff checks for code style
   - Must pass with no errors

4. **Type Checking**
   - MyPy type checking
   - Warnings are acceptable, errors are not

5. **MCP Server Validation**
   - MCP Inspector tests
   - Validates prompts and tools are correctly reported

6. **Docker Build**
   - Docker image must build successfully
   - No security vulnerabilities in base image

### Running CI Locally

Before pushing, run the same checks that CI runs:

```bash
# Run all tests
pytest -v --cov=src/mcp_server

# Lint code
ruff check src/ tests/

# Type check
mypy src/

# Format code
black src/ tests/

# Test MCP server
npx @modelcontextprotocol/inspector --cli --method tools/list python3 -m mcp_server.main

# Build Docker
docker build -t mcp-oauth-server:latest .
```

### Continuous Integration

- **All tests must pass**: PRs cannot be merged with failing tests
- **No blocking issues**: Address all CI failures before review
- **Keep CI green**: Fix broken builds promptly

## Getting Help

### Resources

- **Documentation**: Check the [docs/](docs/) directory
- **GitHub OAuth Setup**: See [GitHub OAuth Setup Guide](docs/setup-auth-github.md)
- **Implementation Notes**: See [RESEARCH.md](docs/RESEARCH.md)
- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **FastMCP Documentation**: [FastMCP Wiki](https://fastmcp.wiki/)

### Asking Questions

- **GitHub Issues**: Open an issue for questions or problems
- **Discussions**: Use GitHub Discussions for general questions
- **Pull Requests**: Ask questions in PR comments

### Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, dependencies
6. **Logs**: Relevant error messages or logs
7. **Screenshots**: If applicable

### Suggesting Features

When suggesting features, include:

1. **Use Case**: Why this feature is needed
2. **Proposed Solution**: How you envision it working
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Any other relevant information

## Project-Specific Guidelines

### OAuth Implementation

- **Always use PKCE**: For public clients
- **Validate state parameter**: Prevent CSRF attacks
- **Never log tokens**: Keep credentials secure
- **Use secure storage**: For token persistence
- **Implement refresh logic**: Handle token expiration

### MCP Protocol

- **Follow MCP specification**: Use latest spec (2025-06-18)
- **Use FastMCP**: Leverage high-level abstractions
- **Clear descriptions**: For prompts and tools
- **Structured output**: Define clear schemas
- **Error handling**: Return helpful error messages

### Security Considerations

- **No hardcoded secrets**: Use environment variables
- **Validate all inputs**: Prevent injection attacks
- **Use HTTPS only**: For external communication
- **Run as non-root**: In Docker containers
- **Keep dependencies updated**: Security patches

### Adding Dependencies

When adding new dependencies:

1. **Add to pyproject.toml**: Under appropriate section
2. **Use version constraints**: Pin major versions
3. **Test in clean environment**: Verify installation works
4. **Update Dockerfile**: If needed for production
5. **Document reason**: Why dependency is needed

## Thank You!

Thank you for contributing to the MCP OAuth Server project! Your contributions help make this project better for everyone.

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
