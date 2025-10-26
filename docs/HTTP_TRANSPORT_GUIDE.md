# HTTP Transport Migration Guide

## Overview

This document describes the migration from stdio transport to HTTP transport using Streamable HTTP with Server-Sent Events (SSE) in the MCP OAuth Server per MCP Specification 2025-06-18.

## What Changed

### Transport Layer
- **Before**: stdio transport (standard input/output)
- **After**: HTTP transport using Streamable HTTP/SSE per MCP Spec 2025-06-18

### Server Framework
- **Before**: `mcp.server.Server` from MCP SDK
- **After**: `FastMCP` from fastmcp library

### Access Method
- **Before**: Server spawned as subprocess, communicated via stdio
- **After**: Server runs as HTTP service on port 8000

## New Endpoints

### MCP Protocol Endpoint
- **URL**: `http://localhost:8000/mcp`
- **Method**: POST (Streamable HTTP)
- **Purpose**: Main MCP protocol endpoint for tool calls, prompts, etc.

### OAuth Authorization Flow
- **URL**: `http://localhost:8000/oauth/authorize`
- **Method**: GET
- **Purpose**: Initiate OAuth authorization flow, redirects to GitHub

### OAuth Callback
- **URL**: `http://localhost:8000/oauth/callback`
- **Method**: GET
- **Purpose**: Handle OAuth callback from GitHub, exchange code for token

### Authorization Metadata (RFC 8414)
- **URL**: `http://localhost:8000/.well-known/oauth-authorization-server`
- **Method**: GET
- **Purpose**: Provide OAuth server metadata for client autodiscovery

### Health Check
- **URL**: `http://localhost:8000/health`
- **Method**: GET
- **Purpose**: Health check endpoint for monitoring

## Running the Server

### Direct Execution
```bash
# Activate virtual environment
source venv/bin/activate

# Run server
python -m mcp_server.main
```

Server will start on `http://0.0.0.0:8000`

### Using Docker
```bash
# Build image
docker-compose build

# Run container
docker-compose up
```

Server will be accessible at `http://localhost:8000`

## Configuration

New environment variables for HTTP mode:

```bash
# HTTP Server Configuration
SERVER_HOST=0.0.0.0              # Listen address
SERVER_PORT=8000                  # HTTP port
SERVER_PATH=/mcp                  # MCP endpoint path
OAUTH_REDIRECT_URI=http://localhost:8000/oauth/callback  # OAuth callback URL
```

## OAuth Flow

### 1. Start Authorization
Navigate to: `http://localhost:8000/oauth/authorize`

This will:
1. Generate PKCE parameters
2. Store session with state and code_verifier
3. Redirect you to GitHub OAuth page

### 2. Authorize on GitHub
- Grant permissions to the application
- GitHub redirects back to callback URL

### 3. Callback Processing
Server receives callback at `/oauth/callback` and:
1. Validates state parameter
2. Retrieves code_verifier from session
3. Exchanges authorization code for access token
4. Stores access token for API requests
5. Shows success page

### 4. Use Authenticated Tools
Once authenticated, MCP tools that require OAuth will work:
- `get_github_user_info` - Fetches GitHub user data with OAuth token

## Client Integration

### Python Client Example
```python
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    # Connect to HTTP server
    async with Client(
        transport=StreamableHttpTransport(url="http://localhost:8000/mcp")
    ) as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        
        # Call a tool
        result = await client.call_tool("get_github_user_info", {
            "include_repos": True,
            "repo_limit": 5
        })
        print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### MCP Configuration Example
For MCP hosts that support HTTP transport:

```json
{
  "mcpServers": {
    "mcp-oauth-server": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

## Session Management

⚠️ **SECURITY WARNING**: The current implementation uses in-memory session storage which has significant security implications:

The server uses in-memory session storage for OAuth flow:

- **Storage**: In-memory dictionary (not persisted across restarts)
- **Expiry**: OAuth sessions expire after 10 minutes
- **Cleanup**: Automatic cleanup of expired sessions
- **⚠️ Security Risks**:
  - NOT suitable for production multi-instance deployments
  - Sessions lost on server restart
  - Potential for session fixation attacks
  - Risk of session hijacking in shared environments
  - No protection against concurrent access
- **Production**: For production use, you MUST implement:
  - Redis or similar for distributed session storage
  - Database-backed persistent storage with encryption
  - Secure, encrypted cookies for stateless sessions
  - Session invalidation mechanisms
  - Regular session rotation

## Security Considerations

### ⚠️ CRITICAL: HTTP vs HTTPS

**DO NOT USE IN PRODUCTION WITH HTTP ONLY**

The default configuration uses unencrypted HTTP which exposes severe security vulnerabilities:

- **🚨 OAuth Tokens Exposed**: Access tokens transmitted in cleartext over the network
- **🚨 Man-in-the-Middle Attacks**: Attackers can intercept OAuth flows and steal tokens
- **🚨 Session Hijacking**: Session cookies and state parameters can be captured
- **🚨 Authorization Code Interception**: PKCE protection bypassed if authorization code is intercepted

### OAuth Security
- ✅ PKCE (RFC 7636) implemented for all flows
- ✅ State parameter validated for CSRF protection
- ✅ Resource Indicators (RFC 8707) for token scoping
- ✅ Sessions expire automatically
- ⚠️ **CRITICAL**: All OAuth security is undermined without HTTPS/TLS

### HTTP Security
- ⚠️ **DEFAULT CONFIGURATION IS NOT SECURE FOR PRODUCTION**
- ⚠️ HTTP only (unencrypted) - tokens visible in network traffic
- ⚠️ No request authentication - anyone can access endpoints
- 🔒 **REQUIRED for production**:
  - **HTTPS with valid SSL/TLS certificates** (minimum TLS 1.2)
  - Configure proper CORS headers
  - Implement rate limiting
  - Add request authentication/authorization
  - Use a reverse proxy (nginx, Apache) with security headers
  - Implement Web Application Firewall (WAF)

### Session Storage
- ⚠️ In-memory storage NOT suitable for production
- ⚠️ Vulnerable to session fixation and hijacking
- 🔒 **REQUIRED for production**:
  - Use Redis or similar for distributed sessions
  - Encrypt session data at rest and in transit
  - Implement session invalidation on logout
  - Regular session rotation
  - Secure session ID generation

## Migration Checklist

If migrating existing code:

- [ ] Update client code to use HTTP transport
- [ ] Change connection URL from local script path to HTTP URL
- [ ] Update OAuth callback URL in GitHub OAuth App settings
- [ ] Test OAuth flow end-to-end
- [ ] Update deployment scripts for HTTP mode
- [ ] Configure firewall rules for port 8000
- [ ] Set up HTTPS/TLS for production
- [ ] Update monitoring to check HTTP health endpoint

## Troubleshooting

### Server Won't Start
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify environment variables are set correctly
- Check logs for error messages

### OAuth Flow Fails
- Verify `OAUTH_REDIRECT_URI` matches GitHub OAuth App settings
- Check that `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET` are correct
- Ensure server is accessible from your browser
- Check that sessions haven't expired (10 minute timeout)

### Tools Return Authentication Errors
- Complete OAuth flow first by visiting `/oauth/authorize`
- Check if token has expired (no automatic refresh in current implementation)
- Verify OAuth scopes include required permissions

## Differences from stdio Transport

| Aspect | stdio Transport | HTTP Transport |
|--------|----------------|----------------|
| Access | Subprocess spawn | HTTP requests |
| Session | Process-based | HTTP session-based |
| OAuth | Environment/manual | Web-based flow |
| Deployment | Local only | Network accessible |
| Scaling | One per client | Multiple clients |
| Discovery | Config file | URL + metadata endpoint |

## Future Enhancements

Planned improvements:

1. **Persistent Sessions**: Redis/database-backed sessions
2. **HTTPS Support**: Built-in TLS support
3. **Token Refresh**: Automatic token refresh before expiry
4. **Multiple Users**: Per-user token management
5. **OAuth Providers**: Support for additional OAuth providers beyond GitHub
6. **Rate Limiting**: Built-in rate limiting per client
7. **Metrics**: Prometheus metrics endpoint
8. **Admin UI**: Web-based administration interface

## References

- [MCP Specification 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/basic)
- [Streamable HTTP Transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http)
- [MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [FastMCP Documentation](https://gofastmcp.com)
- [RFC 8414: OAuth Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)
- [RFC 7636: PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
- [RFC 8707: Resource Indicators](https://datatracker.ietf.org/doc/html/rfc8707)
