# GitHub Copilot Instructions for MCP OAuth Server

## Project Overview

This is a production-ready Model Context Protocol (MCP) server implementing OAuth 2.1 authentication with PKCE, built with Python and FastMCP. The server provides secure access to GitHub APIs through OAuth authentication and demonstrates enterprise-grade MCP server development patterns.

**Key Architecture:**
- **Transport**: HTTP with Streamable SSE (per MCP Spec 2025-06-18)
- **Framework**: FastMCP for high-level abstractions
- **Auth**: GitHubProvider with OAuth 2.1 + PKCE
- **Deployment**: Docker containerization with health checks

## Critical Implementation Details

### Current Server Architecture
The server implements these **actual** components:

**Core Components:**
- `src/mcp_server/server.py` - FastMCP server with GitHubProvider auth
- `src/mcp_server/config.py` - Pydantic settings with OAuth metadata (RFC 8414)
- `src/mcp_server/api_client.py` - GitHub API client with proper auth headers
- `src/mcp_server/main.py` - HTTP transport server entry point

**Current Tools (OAuth Required):**
- `get_user_info()` - Basic authenticated user from token claims
- `get_github_user_info(include_repos, repo_limit)` - Full GitHub API user data

**NOT YET IMPLEMENTED** (referenced in docs but missing from code):
- Sampling capability tools
- Prompt templates
- `analyze_code_with_llm` tool

### MCP Sampling Showcase - GitHub Repository Analysis

**Use Case**: Combine OAuth data fetching with LLM analysis for intelligent repository insights.

This demonstrates the ideal pattern: use OAuth to fetch GitHub data, then use sampling to get AI insights about the code, architecture, or recommendations.

**Implementation Example:**
```python
# Add to src/mcp_server/server.py
import base64
import json
from fastmcp.server.capabilities import ClientCapabilities
from fastmcp.server.session import get_session

@mcp.tool()
async def analyze_repository(
    repo_owner: str,
    repo_name: str,
    analysis_type: str = "overview"
) -> str:
    """
    Analyze a GitHub repository using OAuth data + LLM sampling.

    Combines authenticated GitHub API data with AI analysis for insights.

    Args:
        repo_owner: Repository owner/organization
        repo_name: Repository name
        analysis_type: Type of analysis (overview, tech_stack, architecture, security)

    Returns:
        AI-generated analysis based on repository data
    """
    token = get_access_token()
    session = get_session()

    if not token:
        raise ValueError("OAuth authentication required")

    # Check if client supports sampling
    if not session.check_client_capability(ClientCapabilities.SAMPLING):
        raise ValueError("This tool requires sampling capability (LLM access)")

    try:
        # 1. Fetch repository data via OAuth
        repo_data = await api_client.get_repository(token, repo_owner, repo_name)
        readme_content = await api_client.get_readme(token, repo_owner, repo_name)
        languages = await api_client.get_repository_languages(token, repo_owner, repo_name)

        # 2. Prepare context for LLM analysis
        context = {
            "repository": {
                "name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "language": repo_data.get("language"),
                "languages": languages,
                "stars": repo_data.get("stargazers_count"),
                "forks": repo_data.get("forks_count"),
                "topics": repo_data.get("topics", []),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
            },
            "readme_snippet": readme_content[:2000] if readme_content else "No README found"
        }

        # 3. Create analysis prompt based on type
        analysis_prompts = {
            "overview": "Provide a comprehensive analysis of this repository including its purpose, technology stack, and notable features.",
            "tech_stack": "Analyze the technology stack and architecture. Identify frameworks, libraries, and design patterns used.",
            "architecture": "Examine the repository structure and provide insights about the software architecture and organization.",
            "security": "Review for potential security considerations and best practices based on the visible information."
        }

        prompt = f"""
Analyze this GitHub repository data:

{json.dumps(context, indent=2)}

Task: {analysis_prompts.get(analysis_type, analysis_prompts["overview"])}

Provide specific, actionable insights based on the data. Focus on:
- Code quality indicators
- Technology choices and their implications
- Potential improvements or recommendations
- Notable patterns or practices
"""

        # 4. Use sampling to get LLM analysis
        result = await session.create_message(
            messages=[{
                "role": "user",
                "content": {"type": "text", "text": prompt}
            }],
            max_tokens=800,
            system_prompt="You are a senior software architect and code reviewer. Provide detailed, technical analysis with specific recommendations.",
            temperature=0.3  # Lower temperature for more consistent analysis
        )

        # 5. Return structured analysis
        analysis_result = {
            "repository": f"{repo_owner}/{repo_name}",
            "analysis_type": analysis_type,
            "analysis": result.content.text,
            "model_used": result.model,
            "data_sources": ["GitHub API", "Repository metadata", "README content", "Language statistics"]
        }

        return json.dumps(analysis_result, indent=2)

    except Exception as e:
        logger.error(f"Repository analysis failed: {e}", exc_info=True)
        raise ValueError(f"Analysis failed: {str(e)}") from e
```

**Extended API Client Methods (add to api_client.py):**
```python
async def get_repository(self, token: AccessToken, owner: str, repo: str) -> dict[str, Any]:
    """Fetch repository metadata."""
    headers = self._get_auth_headers(token)
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.get(f"{self.base_url}/repos/{owner}/{repo}", headers=headers)
        response.raise_for_status()
        return response.json()

async def get_readme(self, token: AccessToken, owner: str, repo: str) -> str:
    """Fetch repository README content."""
    headers = self._get_auth_headers(token)
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        try:
            response = await client.get(f"{self.base_url}/repos/{owner}/{repo}/readme", headers=headers)
            response.raise_for_status()
            content = response.json().get("content", "")
            return base64.b64decode(content).decode("utf-8")
        except httpx.HTTPStatusError:
            return ""  # No README found

async def get_repository_languages(self, token: AccessToken, owner: str, repo: str) -> dict[str, int]:
    """Fetch repository language statistics."""
    headers = self._get_auth_headers(token)
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.get(f"{self.base_url}/repos/{owner}/{repo}/languages", headers=headers)
        response.raise_for_status()
        return response.json()
```

**Usage Example:**
```python
# In MCP client:
# Analyze FastMCP repository architecture
result = await analyze_repository("jlowin", "fastmcp", "architecture")

# Get overview of a popular Python project
result = await analyze_repository("microsoft", "vscode", "tech_stack")

# Security analysis of a repository
result = await analyze_repository("huberp", "mcp-oauth-mcpserver-blueprint", "security")
```

**Key Benefits of This Pattern:**
1. **OAuth + Sampling Synergy**: Combines authenticated data access with AI analysis
2. **Contextual Intelligence**: LLM gets rich, real repository data to analyze
3. **Flexible Analysis Types**: Different analysis modes for different use cases
4. **Error Handling**: Graceful fallbacks for missing capabilities or data
5. **Structured Output**: JSON format for easy integration and follow-up actions

**Testing the Sampling Feature:**
```python
# Test sampling capability detection
@pytest.mark.asyncio
async def test_analyze_repository_no_sampling():
    """Test repository analysis without sampling capability."""
    with patch('mcp_server.server.get_session') as mock_session:
        mock_session.return_value.check_client_capability.return_value = False

        with pytest.raises(ValueError, match="requires sampling capability"):
            await analyze_repository("owner", "repo")

# Test with sampling capability
@pytest.mark.asyncio
async def test_analyze_repository_with_sampling(mock_get_access_token, respx_mock):
    """Test repository analysis with sampling."""
    # Mock GitHub API responses
    respx_mock.get("https://api.github.com/repos/owner/repo").mock(
        return_value=Response(200, json={"full_name": "owner/repo", "language": "Python"})
    )

    # Mock sampling response
    with patch('mcp_server.server.get_session') as mock_session:
        mock_session.return_value.check_client_capability.return_value = True
        mock_session.return_value.create_message.return_value.content.text = "Test analysis"
        mock_session.return_value.create_message.return_value.model = "claude-3-sonnet"

        result = await analyze_repository("owner", "repo", "overview")
        assert "Test analysis" in result
```

### MCP Protocol Implementation

**Critical Requirements:**
- Always use MCP Specification 2025-06-18 (NEVER older versions)
- HTTP transport only (stdio is deprecated in this server)
- OAuth Resource Server classification per MCP spec
- Structured error responses with OAuth metadata

**Server Configuration Pattern:**
```python
# src/mcp_server/server.py - Actual implementation
from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

auth_provider = GitHubProvider(
    client_id=settings.oauth_client_id,
    client_secret=settings.oauth_client_secret,
    base_url="http://localhost:8000",  # Must match OAuth App
)

mcp = FastMCP(name=settings.server_name, auth=auth_provider)

@mcp.tool
async def get_github_user_info(include_repos: bool = True, repo_limit: int = 10) -> str:
    token = get_access_token()  # FastMCP dependency injection
    # Implementation validates auth, calls GitHub API, returns JSON
```

### Windows Development Notes

**PowerShell Script Patterns:**
All scripts have `.ps1` equivalents for Windows development:
- `scripts/setup.ps1` - Environment setup with venv creation
- `scripts/run.ps1 [-Foreground]` - Server start/stop with PID management
- `scripts/test.ps1` - Full test suite including coverage
- `runlocal/run-inspector.ps1 [-StartServer]` - MCP Inspector testing

**Key Windows-specific patterns:**
```powershell
# PID management for background processes
$Process = Start-Process -PassThru -WindowStyle Hidden
$Process.Id | Out-File -FilePath ".mcp-server.pid"

# Environment variable loading from .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#].+?)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
    }
}

# Virtual environment activation
if (Test-Path "venv\\Scripts\\python.exe") {
    $PythonCmd = "venv\\Scripts\\python.exe"
}
```

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

### HTTP Transport Implementation

**Key Difference from stdio:** This server runs as HTTP service, not subprocess.

**Actual Configuration (VS Code/Claude Desktop):**
```json
// .vscode/mcp.json or settings
{
  "mcpServers": {
    "mcp-oauth-server": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Development Workflow:**
1. Start server: `./scripts/run.ps1` (Windows) or `./scripts/run.sh` (Linux/Mac)
2. Server runs on port 8000 with endpoints:
   - `/mcp` - MCP protocol endpoint
   - `/oauth/authorize` - OAuth authorization
   - `/health` - Health check
3. Test with MCP Inspector: `./runlocal/run-inspector.ps1 -StartServer`

### OAuth Authorization Flow

**Critical Implementation Details:**
- Uses GitHubProvider from FastMCP (not custom OAuth implementation)
- OAuth metadata exposed via `settings.get_authorization_metadata()` (RFC 8414)
- PKCE enforced automatically by GitHubProvider
- Structured error responses per MCP spec enable client automation

**Example Tool Authorization Error:**
```json
{
  "code": -32001,
  "message": "Authentication required",
  "data": {
    "type": "oauth2",
    "authorization_url": "https://github.com/login/oauth/authorize",
    "scopes": ["read:user"]
  }
}
```

### OAuth Debugging and Testing

**Common OAuth Issues and Solutions:**

1. **Callback URL Mismatch**
   ```powershell
   # Check OAuth app settings match server config
   # GitHub OAuth App callback: http://localhost:8000/oauth/callback
   # Server config in .env: OAUTH_REDIRECT_URI=http://localhost:8000/oauth/callback
   ```

2. **PKCE Validation Errors**
   - FastMCP automatically handles PKCE - don't implement manually
   - Check browser dev tools Network tab for OAuth flow details
   - Look for `code_challenge` and `code_verifier` parameters

3. **Token Validation Issues**
   ```python
   # Debug token claims in tools
   token = get_access_token()
   logger.debug(f"Token claims: {token.claims}")
   logger.debug(f"Token scopes: {token.scopes}")
   ```

**Testing OAuth Flow Step-by-Step:**

1. **Start Server in Debug Mode**
   ```powershell
   # Set debug logging
   $env:LOG_LEVEL = "DEBUG"
   .\scripts\run.ps1 -Foreground
   ```

2. **Test Authorization Endpoint**
   ```powershell
   # Test OAuth metadata discovery
   curl http://localhost:8000/oauth/.well-known/oauth-authorization-server

   # Test authorization URL generation
   curl "http://localhost:8000/oauth/authorize?client_id=your_client_id&response_type=code&scope=read:user"
   ```

3. **Debug Token Exchange**
   ```python
   # Add to tool for debugging
   @mcp.tool
   async def debug_auth() -> dict:
       token = get_access_token()
       return {
           "has_token": token is not None,
           "scopes": token.scopes if token else None,
           "expires_at": token.expires_at if token else None,
           "claims": token.claims if token else None
       }
   ```

4. **Test with MCP Inspector**
   ```powershell
   # Start server and inspector together
   .\runlocal\run-inspector.ps1 -StartServer

   # Inspector will show OAuth errors in real-time
   # Check console for structured error responses
   ```

**OAuth Error Debugging Patterns:**

```python
# Pattern for OAuth-aware error handling
try:
    token = get_access_token()
    if not token:
        raise ValueError("OAuth token required")

    # API call
    result = await api_client.some_call(token)

except Exception as e:
    logger.error(f"Auth error: {e}", extra={
        "has_token": token is not None if 'token' in locals() else False,
        "token_scopes": token.scopes if 'token' in locals() and token else None,
        "client_id": settings.oauth_client_id[:8] + "..." if settings.oauth_client_id else None
    })
    raise
```

**Environment Variable Validation:**
```python
# Add to config.py for debugging
def validate_oauth_setup(self) -> dict[str, str]:
    """Validate OAuth configuration and return status."""
    issues = {}

    if not self.oauth_client_id:
        issues["client_id"] = "Missing OAUTH_CLIENT_ID"
    if not self.oauth_client_secret:
        issues["client_secret"] = "Missing OAUTH_CLIENT_SECRET"
    if not self.oauth_redirect_uri.startswith("http://localhost:8000"):
        issues["redirect_uri"] = f"Should start with http://localhost:8000, got {self.oauth_redirect_uri}"

    return issues
```

**Manual OAuth Testing:**
```bash
# Test full OAuth flow manually (useful for debugging)
# 1. Get authorization URL
curl -X GET "http://localhost:8000/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&scope=read:user&state=test123"

# 2. Follow redirect to GitHub, authorize, copy code from callback
# 3. Exchange code for token (this is handled by FastMCP automatically)

# 4. Test API with token (check server logs for token usage)
```

## Code Style and Standards
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

### OAuth Testing Patterns

**Mock OAuth Token for Tests:**
```python
# tests/conftest.py pattern
@pytest.fixture
def mock_oauth_token():
    """Create mock OAuth token for testing."""
    from fastmcp.server.auth import AccessToken

    return AccessToken(
        token="test_token_12345",
        scopes=["read:user"],
        expires_at=None,
        claims={
            "login": "testuser",
            "name": "Test User",
            "email": "test@example.com"
        }
    )

@pytest.fixture
def mock_get_access_token(mock_oauth_token):
    """Mock FastMCP's get_access_token dependency."""
    with patch('mcp_server.server.get_access_token', return_value=mock_oauth_token):
        yield mock_oauth_token
```

**Testing OAuth-Protected Tools:**
```python
@pytest.mark.asyncio
async def test_get_github_user_info_with_auth(mock_get_access_token, respx_mock):
    """Test tool with OAuth authentication."""
    # Mock GitHub API response
    respx_mock.get("https://api.github.com/user").mock(
        return_value=Response(200, json={"login": "testuser", "name": "Test User"})
    )

    # Call tool - should use mocked token
    result = await get_github_user_info(include_repos=False)

    # Verify API was called with correct auth header
    assert respx_mock["user"].called
    auth_header = respx_mock["user"].calls[0].request.headers["Authorization"]
    assert auth_header == "Bearer test_token_12345"

@pytest.mark.asyncio
async def test_get_github_user_info_no_auth():
    """Test tool without OAuth token."""
    with patch('mcp_server.server.get_access_token', return_value=None):
        with pytest.raises(ValueError, match="OAuth authentication required"):
            await get_github_user_info()
```

**Integration Testing with Real OAuth:**
```python
# tests/test_oauth_integration.py
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OAUTH_CLIENT_ID"), reason="OAuth not configured")
async def test_oauth_flow_integration():
    """Integration test with real OAuth (requires manual setup)."""
    # This test requires manually setting up OAuth app
    # and providing test credentials via environment
    pass
```

**Testing OAuth Configuration:**
```python
def test_oauth_config_validation():
    """Test OAuth configuration validation."""
    # Test missing credentials
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        assert not settings.is_oauth_configured()

    # Test valid configuration
    with patch.dict(os.environ, {
        "OAUTH_CLIENT_ID": "test_id",
        "OAUTH_CLIENT_SECRET": "test_secret"
    }):
        settings = Settings()
        assert settings.is_oauth_configured()

        metadata = settings.get_authorization_metadata()
        assert metadata["issuer"] == "https://github.com"
        assert "authorization_code" in metadata["grant_types_supported"]
```

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

### MCP Protocol Implementation

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

```powershell
# Setup environment
.\scripts\setup.ps1          # Windows

# Run tests
.\scripts\test.ps1           # Windows

# Run server locally
.\scripts\run.ps1            # Windows (background)
.\scripts\run.ps1 -Foreground # Windows (foreground)

# Stop server
.\scripts\stop.ps1           # Windows

# Build Docker image
.\scripts\build-docker.ps1   # Windows

# Format code
ruff format src/ tests/

# Check types
mypy src/

# Lint code
ruff check src/ tests/
```

## Getting Help

### OAuth Troubleshooting Checklist

**Before debugging, verify these basics:**
```powershell
# 1. Check .env file exists and has required OAuth settings
Get-Content .env | Select-String "OAUTH_"

# 2. Verify server is running and accessible
curl http://localhost:8000/health

# 3. Test OAuth metadata endpoint
curl http://localhost:8000/oauth/.well-known/oauth-authorization-server | ConvertFrom-Json

# 4. Check server logs for OAuth errors
.\scripts\run.ps1 -Foreground
# Look for "OAuth", "token", "authorization" in logs
```

**Common OAuth Error Scenarios:**

1. **"Client ID not found" or "Bad credentials"**
   ```powershell
   # Check GitHub OAuth App settings
   # Verify client ID matches .env file
   # Ensure client secret is correct and not expired
   ```

2. **"Redirect URI mismatch"**
   ```powershell
   # GitHub OAuth App callback URL: http://localhost:8000/oauth/callback
   # .env OAUTH_REDIRECT_URI: http://localhost:8000/oauth/callback
   # Server base_url in server.py: http://localhost:8000
   ```

3. **"Invalid PKCE challenge" or "Code verifier required"**
   ```powershell
   # FastMCP handles PKCE automatically
   # Check browser Network tab for OAuth flow
   # Verify code_challenge and code_verifier parameters present
   ```

4. **"Token expired" or "Invalid token"**
   ```powershell
   # Clear browser cookies for localhost:8000
   # Restart OAuth flow
   # Check token expiration in logs
   ```

**Debug OAuth Flow in Browser:**
1. Open browser dev tools (F12)
2. Go to Network tab
3. Navigate to tool that requires auth
4. Follow OAuth redirect chain
5. Check for:
   - `code_challenge` parameter in authorization URL
   - `code` parameter in callback URL
   - `access_token` in final response

**Server Log Analysis:**
```powershell
# Run server with debug logging
$env:LOG_LEVEL = "DEBUG"
.\scripts\run.ps1 -Foreground

# Look for these log patterns:
# "OAuth authorization request" - Initial auth request
# "Token exchange successful" - Successful token retrieval
# "Token validation failed" - Token issues
# "API call failed" - GitHub API errors
```

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
- Server uses HTTP transport with Streamable SSE
- Supports tools (OAuth authentication required)
- Prompts and sampling features are documented but not yet implemented
- Tools provide OAuth authentication errors with structured metadata per MCP spec

### Future Enhancements
- Add support for other OAuth providers
- Implement rate limiting
- Add caching for API responses
- Support for multiple concurrent users
- Web-based OAuth callback handler
- Token persistence across restarts

---

*Last Updated: 2025-11-03*
*Version: 1.1*
