# MCP OAuth Server

A production-ready Model Context Protocol (MCP) server with OAuth 2.1 authentication support, built with Python and FastMCP.

[![CI](https://github.com/huberp/n-eight-n/workflows/CI/badge.svg)](https://github.com/huberp/n-eight-n/actions/workflows/ci.yml)
[![Tests](https://github.com/huberp/n-eight-n/workflows/Tests/badge.svg)](https://github.com/huberp/n-eight-n/actions/workflows/test.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This MCP server demonstrates secure OAuth 2.1 authentication with PKCE (Proof Key for Code Exchange) for accessing third-party APIs. It's designed to run locally in MCP hosts like Visual Studio Code and can be deployed as a Docker container.

### Key Features

- **OAuth 2.1 Authentication**: Full implementation with PKCE support for secure authentication
- **RFC 8707 Resource Indicators**: Implements resource indicators for enhanced token security
- **MCP Protocol Compliance**: Follows the latest MCP specification (2025-06-18)
- **OAuth Resource Server**: Classified as OAuth Resource Server per MCP spec
- **Structured Tool Output**: Tools support structured output schemas for type safety
- **Prompt Template**: Reusable prompt for GitHub user analysis with enhanced metadata
- **Tool Integration**: Custom tool for fetching GitHub user data via authenticated API calls
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
│  │              AI Assistant                           │    │
│  └───────────────────┬────────────────────────────────┘    │
│                      │ MCP Protocol                         │
└──────────────────────┼──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Docker Container (MCP Server)                      │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MCP Server (FastMCP)                                │   │
│  │  - OAuth 2.1 Handler (PKCE)                          │   │
│  │  - GitHub API Client                                 │   │
│  │  - Prompt: github_user_summary                       │   │
│  │  - Tool: get_github_user_info                        │   │
│  └─────────────────────────────────────────────────────┘   │
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
git clone https://github.com/huberp/n-eight-n.git
cd n-eight-n
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

Edit `.env` file with your GitHub OAuth App credentials:

```bash
OAUTH_CLIENT_ID=your_github_client_id
OAUTH_CLIENT_SECRET=your_github_client_secret
OAUTH_AUTHORIZATION_URL=https://github.com/login/oauth/authorize
OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
OAUTH_SCOPES=read:user,repo
```

**Creating a GitHub OAuth App:**
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - Application name: MCP OAuth Server (or your preferred name)
   - Homepage URL: http://localhost:8080
   - Authorization callback URL: http://localhost:8080/callback
4. Copy the Client ID and generate a Client Secret

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

**Linux/macOS:**
```bash
./scripts/run.sh
```

**Windows:**
```powershell
.\scripts\run.ps1
```

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

### Run with Docker Compose

```bash
docker-compose up
```

### Run with Docker

```bash
docker run --env-file .env -i mcp-oauth-server:latest
```

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

### MCP Host Configuration (VS Code)

Add this to your MCP settings in VS Code:

```json
{
  "mcpServers": {
    "mcp-oauth-server": {
      "command": "docker",
      "args": ["run", "--env-file", "/path/to/.env", "-i", "mcp-oauth-server:latest"]
    }
  }
}
```

Or for local development without Docker:

```json
{
  "mcpServers": {
    "mcp-oauth-server": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "env": {
        "OAUTH_CLIENT_ID": "your_client_id",
        "OAUTH_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

## Development

### Project Structure

```
.
├── src/mcp_server/          # Main application code
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── oauth_handler.py     # OAuth 2.1 implementation with PKCE
│   ├── api_client.py        # GitHub API client
│   ├── server.py            # MCP server implementation
│   └── main.py              # Application entry point
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_config.py       # Configuration tests
│   ├── test_oauth_handler.py # OAuth handler tests
│   └── test_api_client.py   # API client tests
├── scripts/                 # Utility scripts
│   ├── setup.sh/ps1         # Environment setup
│   ├── test.sh/ps1          # Run tests
│   ├── run.sh/ps1           # Run server
│   └── build-docker.sh/ps1  # Build Docker image
├── docs/                    # Documentation
│   └── RESEARCH.md          # Research and implementation notes
├── .github/
│   ├── workflows/           # GitHub Actions CI/CD
│   │   ├── ci.yml          # Main CI pipeline
│   │   └── test.yml        # Comprehensive test suite
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
pytest tests/test_oauth_handler.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Format code
black src/ tests/

# Run all quality checks
./scripts/test.sh  # or test.ps1 on Windows
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OAUTH_CLIENT_ID` | OAuth client ID | - | Yes |
| `OAUTH_CLIENT_SECRET` | OAuth client secret | - | Yes |
| `OAUTH_AUTHORIZATION_URL` | OAuth authorization endpoint | GitHub URL | No |
| `OAUTH_TOKEN_URL` | OAuth token endpoint | GitHub URL | No |
| `OAUTH_SCOPES` | Comma-separated OAuth scopes | read:user | No |
| `API_BASE_URL` | API base URL | https://api.github.com | No |
| `API_TIMEOUT` | API request timeout (seconds) | 30 | No |
| `SERVER_NAME` | MCP server name | mcp-oauth-server | No |
| `LOG_LEVEL` | Logging level | INFO | No |
| `ENVIRONMENT` | Environment name | development | No |

## Security Considerations

- **OAuth 2.1 with PKCE**: Prevents authorization code interception attacks
- **No Hardcoded Secrets**: All credentials managed via environment variables
- **Non-root Docker User**: Containers run as non-privileged user
- **Token Management**: Secure storage and automatic refresh of access tokens
- **Minimal Dependencies**: Reduces attack surface
- **HTTPS Only**: All external communication uses secure protocols

## Troubleshooting

### OAuth Authentication Issues

If you encounter OAuth authentication errors:

1. **Verify Credentials**: Ensure your OAuth credentials in `.env` are correct
2. **Check Callback URL**: The callback URL in your OAuth app must match
3. **Inspect Scopes**: Verify required OAuth scopes are configured
4. **Token Expiry**: Tokens expire; use the refresh flow to get new tokens

### Server Connection Issues

1. **Port Conflicts**: Ensure no other service is using the required ports
2. **Docker Issues**: Check Docker logs: `docker-compose logs -f`
3. **Environment Variables**: Verify `.env` file is loaded correctly

### Test Failures

```bash
# Run tests with verbose output
pytest -v

# Run a specific test
pytest tests/test_oauth_handler.py::test_generate_pkce_pair -v

# Skip slow tests
pytest -m "not slow"
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `./scripts/test.sh`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

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
- Open an issue on [GitHub](https://github.com/huberp/n-eight-n/issues)
- Check the [documentation](docs/RESEARCH.md) for detailed implementation notes

## Acknowledgments

- Model Context Protocol team for the excellent specification
- FastMCP for the high-level Python implementation
- Authlib for robust OAuth support
- The open-source community for inspiration and best practices
