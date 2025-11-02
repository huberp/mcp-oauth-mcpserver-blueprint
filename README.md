# MCP OAuth Server

A production-ready Model Context Protocol (MCP) server with OAuth 2.1 authentication support, built with Python and FastMCP.

[![CI](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/workflows/CI/badge.svg)](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/actions/workflows/ci.yml)
[![Tests](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/workflows/Tests/badge.svg)](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/actions/workflows/test.yml)
[![MCP Tester](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/workflows/MCP%20Tester/badge.svg)](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/actions/workflows/mcp-tester.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Codecov](https://codecov.io/gh/huberp/mcp-oauth-mcpserver-blueprint/branch/main/graph/badge.svg)](https://codecov.io/gh/huberp/mcp-oauth-mcpserver-blueprint)
[![Release](https://img.shields.io/github/v/release/huberp/mcp-oauth-mcpserver-blueprint)](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/releases)

## Overview

This MCP server demonstrates secure OAuth 2.1 authentication with PKCE (Proof Key for Code Exchange) for accessing third-party APIs. It's designed to run locally in MCP hosts like Visual Studio Code and can be deployed as a Docker container.

**Transport**: This server uses HTTP transport (Streamable HTTP with SSE) per MCP Specification 2025-06-18. For migration details from stdio, see [HTTP Transport Guide](docs/HTTP_TRANSPORT_GUIDE.md).

### Key Features

- **HTTP Transport**: Streamable HTTP with Server-Sent Events (SSE) per MCP Spec 2025-06-18
- **OAuth 2.1 Authentication**: Full implementation with PKCE support for secure authentication
- **RFC 8414 Authorization Metadata**: Server exposes OAuth metadata for client autodiscovery
- **RFC 8707 Resource Indicators**: Implements resource indicators for enhanced token security
- **Structured Error Responses**: JSON-RPC errors with OAuth metadata enable client automation
- **MCP Protocol Compliance**: Follows the latest MCP specification (2025-06-18)
- **OAuth Resource Server**: Classified as OAuth Resource Server per MCP spec
- **MCP Sampling Support**: Demonstrates client sampling capability for LLM-powered code analysis
- **Structured Tool Output**: Tools support structured output schemas for type safety
- **Prompt Template**: Reusable prompt for GitHub user analysis with enhanced metadata
- **Tool Integration**: Custom tools for fetching GitHub user data and analyzing code with LLMs
- **Docker Support**: Containerized deployment with best practices
- **Comprehensive Testing**: Full test coverage with pytest
- **Type Safety**: Complete type hints with mypy validation
- **Production Ready**: Logging, error handling, and configuration management

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MCP Host (VS Code)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │       AI Assistant (with Sampling Support)          │    │
│  └────────────┬──────────────────┬────────────────────┘    │
│               │ MCP Protocol     │ Sampling Requests       │
└───────────────┼──────────────────┼──────────────────────────┘
                │                  │
                ▼                  │
┌─────────────────────────────────┼────────────────────────────┐
│           Docker Container (MCP │Server)                      │
│                                 │                            │
│  ┌──────────────────────────────▼──────────────────────┐   │
│  │  MCP Server (FastMCP)                                │   │
│  │  - GitHubProvider (OAuth 2.1 with PKCE)              │   │
│  │  - GitHub API Client                                 │   │
│  │  - Prompt: github_user_summary                       │   │
│  │  - Tool: get_github_user_info (OAuth)                │   │
│  │  - Tool: analyze_code_with_llm (Sampling)            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         GitHub OAuth & API (HTTPS)                           │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.12
- Docker (optional, for containerized deployment)
- GitHub OAuth App credentials (for full functionality)

### 1. Clone the Repository

```bash
git clone https://github.com/huberp/mcp-oauth-mcpserver-blueprint.git
cd mcp-oauth-mcpserver-blueprint
```

### 2. Setup Environment

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
- Install all dependencies
- Create a `.env` file from the template

### 3. Configure OAuth Credentials

📖 **For detailed setup instructions, see [GitHub OAuth Setup Guide](docs/setup-auth-github.md)**

Edit `.env` file with your GitHub OAuth App credentials:

```bash
OAUTH_CLIENT_ID=your_github_client_id
OAUTH_CLIENT_SECRET=your_github_client_secret
OAUTH_AUTHORIZATION_URL=https://github.com/login/oauth/authorize
OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
OAUTH_SCOPES=read:user,repo
```

**Quick Start - Creating a GitHub OAuth App:**
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - Application name: MCP OAuth Server (or your preferred name)
   - Homepage URL: http://localhost:8000
   - Authorization callback URL: http://localhost:8000/oauth/callback
4. Copy the Client ID and generate a Client Secret

💡 **Need help?** Check the [comprehensive setup guide](docs/setup-auth-github.md) for step-by-step instructions, troubleshooting, and testing.

### 4. Run Tests

**Linux/macOS:**
```bash
./scripts/test.sh
```

**Windows:**
```powershell
.\scripts\test.ps1
```

### 5. Run the Server

The server can be run in two modes:

**Background Mode (recommended for development):**

Starts the server in the background and writes a PID file for easy management.

**Linux/macOS:**
```bash
./scripts/run.sh
```

**Windows:**
```powershell
.\scripts\run.ps1
```

**Foreground Mode (for debugging):**

Runs the server in the current terminal window. Press Ctrl+C to stop.

**Linux/macOS:**
```bash
./scripts/run.sh --foreground
```

**Windows:**
```powershell
.\scripts\run.ps1 -Foreground
```

**Stopping the Background Server:**

**Linux/macOS:**
```bash
./scripts/stop.sh
```

**Windows:**
```powershell
.\scripts\stop.ps1
```

The server will be available at:
- MCP endpoint: `http://localhost:8000/mcp`
- OAuth authorization: `http://localhost:8000/oauth/authorize`
- Health check: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`
- Server info: `http://localhost:8000/info`

## Docker Deployment

### Build Docker Image

**Linux/macOS:**
```bash
./scripts/build-docker.sh
```

**Windows:**
```powershell
.\scripts\build-docker.ps1
```

### Run with Docker Compose (Recommended)

For development with automatic environment loading and easy management:

```bash
docker-compose up
```

The server will be available at `http://localhost:8000/mcp`.

### Run with Docker (Production)

For production deployments or manual control:

```bash
docker run --env-file .env -p 8000:8000 mcp-oauth-server:latest
```

**Note**: Port mapping (`-p 8000:8000`) is required to access the HTTP server from your host machine.

## Usage

### Available Components

#### Prompt: `github_user_summary`

Generates a comprehensive summary of a GitHub user's profile and repositories.

**Parameters:**
- `username` (optional): GitHub username to analyze (defaults to authenticated user)

**Example usage in MCP host:**
```
Use the github_user_summary prompt to analyze my GitHub profile
```

#### Tool: `get_github_user_info`

Fetches authenticated GitHub user information and repositories using OAuth.

**Parameters:**
- `include_repos` (boolean, default: true): Whether to include repository data
- `repo_limit` (integer, default: 10): Maximum number of repositories to fetch (1-100)

**Returns:**
- User profile information (login, name, bio, followers, etc.)
- Repository list with details (name, description, language, stars, forks)

**Example usage in MCP host:**
```
Use the get_github_user_info tool to fetch my GitHub profile and top 10 repositories
```

#### Tool: `analyze_code_with_llm` (Requires Sampling Capability)

Uses MCP sampling to analyze code snippets with the help of a language model. This tool demonstrates the MCP sampling capability by requesting the client's language model to analyze code or provide insights.

**Parameters:**
- `code` (string, required): Code snippet or data to analyze
- `analysis_type` (string, default: "explain"): Type of analysis to perform
  - `explain`: Explain what the code does
  - `review`: Review the code and provide feedback
  - `suggest_improvements`: Suggest improvements for the code
  - `find_bugs`: Analyze for potential bugs or issues
  - `security_review`: Review for security vulnerabilities
- `max_tokens` (integer, default: 500): Maximum tokens for the LLM response (100-2000)

**Requirements:**
- Client must support the MCP `sampling` capability
- No OAuth authentication required

**Returns:**
- Analysis result with model information
- Insights based on the selected analysis type

**Example usage in MCP host:**
```
Use the analyze_code_with_llm tool to explain this code:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Note:** This tool will return an error if the client does not support sampling. Supported clients include Claude Desktop and VS Code with MCP support.

### HTTP Endpoints

The server provides additional HTTP endpoints for monitoring and information:

#### `/health` - Health Check

Health check endpoint for monitoring server status.

**Method:** GET

**Response:**
```json
{
  "status": "healthy",
  "server": "mcp-oauth-server",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "timestamp": "2025-11-01T10:51:40.812895Z"
}
```

**Use cases:**
- Kubernetes/Docker health checks
- Monitoring tools
- Load balancer health checks

#### `/metrics` - Server Metrics

Metrics endpoint providing tool call statistics and operational data.

**Method:** GET

**Response:**
```json
{
  "server": "mcp-oauth-server",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "tool_calls": {
    "total": 42,
    "by_tool": {
      "get_user_info": 15,
      "get_github_user_info": 27
    }
  },
  "timestamp": "2025-11-01T10:51:40.817726Z"
}
```

**Use cases:**
- Performance monitoring
- Usage analytics
- Debugging tool usage patterns

#### `/info` - Server Information

Information endpoint providing comprehensive server metadata.

**Method:** GET

**Response:**
```json
{
  "server": {
    "name": "mcp-oauth-server",
    "version": "0.1.0",
    "environment": "production",
    "debug": false
  },
  "github": {
    "repository": "huberp/mcp-oauth-mcpserver-blueprint",
    "url": "https://github.com/huberp/mcp-oauth-mcpserver-blueprint"
  },
  "oauth": {
    "configured": true,
    "provider": "GitHub",
    "scopes": ["read:user", "repo"]
  },
  "http": {
    "host": "0.0.0.0",
    "port": 8000,
    "path": "/mcp"
  },
  "api": {
    "base_url": "https://api.github.com",
    "timeout": 30
  },
  "timestamp": "2025-11-01T10:51:40.815391Z"
}
```

**Use cases:**
- Service discovery
- Configuration verification
- Diagnostics and troubleshooting

### MCP Host Configuration (VS Code)

**Note**: This server uses HTTP transport (Streamable HTTP with SSE) per MCP Specification 2025-06-18. For migration details, see [HTTP Transport Guide](docs/HTTP_TRANSPORT_GUIDE.md).

Add this to your MCP settings in VS Code (`.vscode/mcp.json` or your MCP configuration file):

```json
{
  "mcpServers": {
    "mcp-oauth-server": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Important**: The server must be running before the MCP client connects. Start the server with:

```bash
# Using scripts (recommended)
./scripts/run.sh

# Or with Docker
docker-compose up
```

## MCP Server Testing

This repository includes automated testing of the MCP server using the MCP Inspector CLI. The workflow runs on every push and pull request, validating that the server correctly reports its available prompts and tools.

### MCP Tester Workflow

The `mcp-tester.yml` workflow:
- Uses `@modelcontextprotocol/inspector` CLI to test the MCP server
- Lists all available tools and prompts
- Generates a summary table in the workflow results
- Runs automatically on pushes to main, develop, and copilot/** branches

**View test results:** Check the workflow summary in GitHub Actions to see a table of all prompts and tools reported by the MCP server.

**Manual testing with MCP Inspector:**

The server now uses HTTP transport, so you need to start the server first before testing with the inspector.

**Option 1: Quick Start (Automatic Server Start)**

**Linux/macOS:**
```bash
./runlocal/run-inspector.sh --start-server
```

**Windows:**
```powershell
.\runlocal\run-inspector.ps1 -StartServer
```

**Option 2: Manual Server Management**

**Linux/macOS:**
```bash
# 1. Start the server in background
./scripts/run.sh

# 2. Run the inspector (configured for HTTP transport)
./runlocal/run-inspector.sh

# 3. Stop the server when done
./scripts/stop.sh
```

**Windows:**
```powershell
# 1. Start the server in background
.\scripts\run.ps1

# 2. Run the inspector (configured for HTTP transport)
.\runlocal\run-inspector.ps1

# 3. Stop the server when done
.\scripts\stop.ps1
```

**Configuration Files:**
- `runlocal/config.json` - MCP Inspector configuration (HTTP transport)
- `.vscode/mcp.json` - VS Code MCP client configuration (HTTP transport)

Both configurations connect to `http://localhost:8000/mcp` by default.

## Development

### Project Structure

```
.
├── src/mcp_server/          # Main application code
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── api_client.py        # GitHub API client
│   ├── server.py            # MCP server implementation
│   └── main.py              # Application entry point
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_config.py       # Configuration tests
│   ├── test_api_client.py   # API client tests
│   └── test_sampling.py     # Sampling capability tests
├── scripts/                 # Utility scripts
│   ├── setup.sh/ps1         # Environment setup
│   ├── test.sh/ps1          # Run tests
│   ├── run.sh/ps1           # Run server
│   └── build-docker.sh/ps1  # Build Docker image
├── docs/                    # Documentation
│   ├── RESEARCH.md          # Research and implementation notes
│   ├── setup-auth-github.md # GitHub OAuth setup guide
│   ├── AUTHORIZATION_GUIDE.md # Complete authorization guide
│   ├── AUTHORIZATION_QUICK_REFERENCE.md # Quick reference
│   ├── AUTHORIZATION_FLOW_SUMMARY.md # Authorization flow summary
│   ├── HTTP_TRANSPORT_GUIDE.md # HTTP transport migration guide
│   ├── MCP_AUTHORIZATION_ANALYSIS.md # Technical analysis
│   ├── IMPLEMENTATION_SUMMARY.md # Implementation summary
│   ├── SPEC_UPDATE_2025-06-18.md # MCP spec update notes
│   └── sampling.md          # Sampling feature documentation
├── runlocal/                # Local development tools
│   ├── config.json          # MCP Inspector configuration
│   ├── run-inspector.sh     # Inspector runner (Linux/macOS)
│   └── run-inspector.ps1    # Inspector runner (Windows)
├── .github/
│   ├── workflows/           # GitHub Actions CI/CD
│   │   ├── ci.yml          # Main CI pipeline
│   │   ├── test.yml        # Comprehensive test suite
│   │   └── mcp-tester.yml  # MCP server validation
│   └── copilot-instructions.md # Copilot guidelines
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Docker Compose configuration
├── pyproject.toml           # Python project configuration
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Running Tests

The project includes comprehensive unit tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mcp_server

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Code Quality

#### Automated Code Quality (Recommended)

We use pre-commit hooks to automatically enforce code quality standards:

```bash
# Install pre-commit (one-time setup)
pip install pre-commit
pre-commit install

# Pre-commit will now run automatically on git commit
# To manually run on all files:
pre-commit run --all-files
```

The pre-commit hooks include:
- **Ruff**: Linting and formatting (replaces Black + Flake8 + isort)
- **mypy**: Type checking
- **Standard checks**: Trailing whitespace, end-of-file, YAML/JSON/TOML validation
- **Security**: Private key detection
- **Docker**: Dockerfile linting
- **Shell**: Shell script validation

#### VS Code Integration

For the best development experience in VS Code:

1. **Install recommended extensions** (VS Code will prompt you):
   - `charliermarsh.ruff` - Ruff linter and formatter
   - `ms-python.python` - Python support
   - Other helpful extensions listed in `.vscode/extensions.json`

2. **Automatic formatting on save** is already configured in `.vscode/settings.json`

3. **EditorConfig** support: Install the EditorConfig extension for consistent formatting across all editors

#### Manual Code Quality Checks

If you prefer not to use pre-commit hooks:

```bash
# Format code with Ruff
ruff format src/ tests/

# Lint and auto-fix with Ruff
ruff check --fix src/ tests/

# Type checking
mypy src/

# Run all quality checks
./scripts/test.sh  # or test.ps1 on Windows
```

**Note**: Ruff replaces Black, Flake8, isort, and other tools with a single, faster linter and formatter.

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OAUTH_CLIENT_ID` | OAuth client ID | - | Yes |
| `OAUTH_CLIENT_SECRET` | OAuth client secret | - | Yes |
| `OAUTH_AUTHORIZATION_URL` | OAuth authorization endpoint | https://github.com/login/oauth/authorize | No |
| `OAUTH_TOKEN_URL` | OAuth token endpoint | https://github.com/login/oauth/access_token | No |
| `OAUTH_SCOPES` | Comma-separated OAuth scopes | read:user | No |
| `OAUTH_REDIRECT_URI` | OAuth callback URL | http://localhost:8000/oauth/callback | No |
| `OAUTH_ISSUER` | OAuth issuer URL (RFC 8414) | https://github.com | No |
| `OAUTH_GRANT_TYPES_SUPPORTED` | Supported grant types | authorization_code,refresh_token | No |
| `OAUTH_CODE_CHALLENGE_METHODS_SUPPORTED` | PKCE methods supported | S256 | No |
| `OAUTH_RESPONSE_TYPES_SUPPORTED` | OAuth response types | code | No |
| `OAUTH_TOKEN_ENDPOINT_AUTH_METHODS` | Token endpoint auth methods | client_secret_post,client_secret_basic | No |
| `API_BASE_URL` | API base URL | https://api.github.com | No |
| `API_TIMEOUT` | API request timeout (seconds) | 30 | No |
| `SERVER_NAME` | MCP server name | mcp-oauth-server | No |
| `SERVER_VERSION` | Server version | 0.1.0 | No |
| `SERVER_HOST` | HTTP server host | 0.0.0.0 | No |
| `SERVER_PORT` | HTTP server port | 8000 | No |
| `SERVER_PATH` | MCP endpoint path | /mcp | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `ENVIRONMENT` | Environment name | development | No |
| `DEBUG` | Enable debug mode | false | No |

## Authorization

This server implements **OAuth 2.1 with PKCE** and follows MCP Specification 2025-06-18 for authorization.

### Key Authorization Features

- ✅ **RFC 8414 Compliance**: Exposes authorization server metadata for client autodiscovery
- ✅ **RFC 8707 Resource Indicators**: Tokens scoped to specific resources
- ✅ **RFC 7636 PKCE**: Proof Key for Code Exchange for enhanced security
- ✅ **Structured Error Responses**: JSON-RPC errors with OAuth metadata for client automation

### Authorization Flow

When a client calls a protected tool without authentication, the server returns a structured error response:

```json
{
  "code": -32001,
  "message": "Authentication required",
  "data": {
    "type": "oauth2",
    "grant_type": "authorization_code",
    "authorization_url": "https://github.com/login/oauth/authorize",
    "token_url": "https://github.com/login/oauth/access_token",
    "scopes": ["read:user"],
    "code_challenge_method": "S256",
    "resource": "https://api.github.com"
  }
}
```

This enables MCP clients to automatically discover OAuth endpoints and initiate authentication flows.

### Getting Authorization Metadata

The server exposes RFC 8414 compliant authorization metadata:

```python
from mcp_server.config import settings

metadata = settings.get_authorization_metadata()
# Returns: issuer, authorization_endpoint, token_endpoint,
#          scopes_supported, grant_types_supported, etc.
```

### For Developers

📖 **Complete Authorization Guide**: See [docs/AUTHORIZATION_GUIDE.md](docs/AUTHORIZATION_GUIDE.md) for:
- Detailed authorization flow diagrams
- Step-by-step OAuth implementation
- Client integration examples
- Troubleshooting common issues
- Security best practices

**Quick Links:**
- [Authorization Guide](docs/AUTHORIZATION_GUIDE.md) - Complete developer guide
- [GitHub OAuth Setup](docs/setup-auth-github.md) - OAuth app configuration
- [Technical Analysis](docs/MCP_AUTHORIZATION_ANALYSIS.md) - Deep dive into implementation

## Security Considerations

- **OAuth 2.1 with PKCE**: Prevents authorization code interception attacks (RFC 7636)
- **Resource Indicators (RFC 8707)**: Tokens are scoped to specific resources, preventing token misuse
- **Authorization Metadata (RFC 8414)**: Clients can discover OAuth endpoints securely
- **Structured Error Responses**: OAuth errors follow MCP spec with machine-readable metadata
- **No Hardcoded Secrets**: All credentials managed via environment variables
- **Non-root Docker User**: Containers run as non-privileged user
- **Token Management**: Secure storage and automatic refresh of access tokens
- **Minimal Dependencies**: Reduces attack surface
- **HTTPS Only**: All external communication uses secure protocols

📖 **Security Best Practices**: See the [Authorization Guide](docs/AUTHORIZATION_GUIDE.md#security-best-practices) for detailed security recommendations.

## Troubleshooting

### OAuth Authentication Issues

If you encounter OAuth authentication errors:

1. **Verify Credentials**: Ensure your OAuth credentials in `.env` are correct
2. **Check Callback URL**: The callback URL in your OAuth app must match
3. **Inspect Scopes**: Verify required OAuth scopes are configured
4. **Token Expiry**: Tokens expire; use the refresh flow to get new tokens
5. **Authorization Metadata**: Check server logs for OAuth configuration on startup

📖 **Detailed Troubleshooting**: See [Authorization Guide - Troubleshooting](docs/AUTHORIZATION_GUIDE.md#troubleshooting) for:
- Error code explanations
- Step-by-step resolution guides
- Common configuration issues
- PKCE troubleshooting

### Server Connection Issues

1. **Port Conflicts**: Ensure no other service is using the required ports
2. **Docker Issues**: Check Docker logs: `docker-compose logs -f`
3. **Environment Variables**: Verify `.env` file is loaded correctly

### Test Failures

```bash
# Run tests with verbose output
pytest -v

# Run a specific test
pytest tests/test_config.py::test_oauth_scopes_list -v

# Skip slow tests
pytest -m "not slow"
```

## Contributing

We welcome contributions from the community! Please see our [Contributing Guide](CONTRIBUTING.md) for detailed information on:

- Code of Conduct
- Development setup and workflow
- Code style and testing requirements
- Pull request process
- Commit message guidelines

**Quick Start for Contributors:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our [code standards](CONTRIBUTING.md#code-style-and-standards)
4. Run tests: `./scripts/test.sh`
5. Commit your changes: `git commit -m 'feat: Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

For detailed guidelines, please read [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

### MCP Specification
- [Official MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [MCP Documentation](https://modelcontextprotocol.io/docs/sdk)

### OAuth Resources
- [OAuth 2.1 Specification](https://oauth.net/2.1/)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)

### Python Libraries
- [FastMCP Documentation](https://fastmcp.wiki/)
- [Authlib Documentation](https://docs.authlib.org/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Support

For issues, questions, or contributions, please:
- Open an issue on [GitHub](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/issues)
- Check the [GitHub OAuth Setup Guide](docs/setup-auth-github.md) for authentication setup
- Check the [documentation](docs/RESEARCH.md) for detailed implementation notes

## Acknowledgments

- Model Context Protocol team for the excellent specification
- FastMCP for the high-level Python implementation
- Authlib for robust OAuth support
- The open-source community for inspiration and best practices
