# MCP OAuth Server - Authorization Guide

**Version:** 1.0  
**Last Updated:** 2025-10-25  
**MCP Specification:** 2025-06-18

---

## Table of Contents

1. [Overview](#overview)
2. [Authorization Flow](#authorization-flow)
3. [For Developers: Using the Server](#for-developers-using-the-server)
4. [For Integrators: Client Implementation](#for-integrators-client-implementation)
5. [Configuration Reference](#configuration-reference)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)

---

## Overview

This MCP server implements **OAuth 2.1 with PKCE** for secure authentication with third-party services (GitHub by default). The server acts as an **OAuth Resource Server** per MCP Specification 2025-06-18.

### Key Authorization Features

- ✅ **RFC 8414**: OAuth Authorization Server Metadata for client autodiscovery
- ✅ **RFC 8707**: Resource Indicators for token scoping
- ✅ **RFC 7636**: PKCE (Proof Key for Code Exchange) for enhanced security
- ✅ **MCP 2025-06-18**: Compliant error responses and metadata exposure

### Authorization vs Authentication

- **Authentication**: Verifying who you are (handled by OAuth provider like GitHub)
- **Authorization**: Determining what you can access (managed by this MCP server)

This server validates OAuth tokens to authorize access to protected tools and resources.

---

## Authorization Flow

### High-Level Flow Diagram

```
┌─────────┐         ┌──────────┐         ┌─────────┐
│   MCP   │         │   MCP    │         │  GitHub │
│  Client │         │  Server  │         │  OAuth  │
└────┬────┘         └────┬─────┘         └────┬────┘
     │                   │                     │
     │ 1. Initialize     │                     │
     │   (discover auth) │                     │
     ├──────────────────>│                     │
     │                   │                     │
     │ 2. Server info    │                     │
     │   + auth metadata │                     │
     │<──────────────────┤                     │
     │                   │                     │
     │ 3. Call protected │                     │
     │    tool           │                     │
     ├──────────────────>│                     │
     │                   │                     │
     │ 4. Error: Auth    │                     │
     │    required       │                     │
     │    (with OAuth    │                     │
     │     endpoints)    │                     │
     │<──────────────────┤                     │
     │                   │                     │
     │ 5. OAuth flow     │                     │
     ├───────────────────┼────────────────────>│
     │                   │                     │
     │ 6. Access token   │                     │
     │<──────────────────┼─────────────────────┤
     │                   │                     │
     │ 7. Retry with     │                     │
     │    token          │                     │
     ├──────────────────>│                     │
     │                   │                     │
     │ 8. Success!       │                     │
     │<──────────────────┤                     │
```

### Step-by-Step Flow

#### Step 1: Server Initialization

When your MCP client connects to the server, it receives authorization metadata:

```json
{
  "serverInfo": {
    "name": "mcp-oauth-server",
    "version": "0.1.0"
  }
}
```

The server logs OAuth configuration including:
- Authorization endpoint
- Token endpoint
- Supported scopes
- Grant types (authorization_code, refresh_token)
- PKCE methods (S256)

#### Step 2: Calling a Protected Tool

When you call a tool that requires authentication (e.g., `get_github_user_info`):

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_github_user_info",
    "arguments": {
      "include_repos": true,
      "repo_limit": 10
    }
  }
}
```

#### Step 3: Authorization Error Response

If not authenticated, the server returns a **structured error** with OAuth metadata:

```json
{
  "error": {
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
}
```

This structured error enables MCP clients to **automatically** discover and initiate OAuth flows.

#### Step 4: OAuth Authorization

**For Manual Testing:**
1. Extract the `authorization_url` from the error
2. Open it in a browser
3. Authorize the application
4. Copy the authorization code from the callback URL
5. Exchange it for an access token using the `token_url`

**For Automated Clients:**
The client can parse the error response and automatically initiate the OAuth flow.

#### Step 5: Using the Access Token

After obtaining a token, configure your OAuth handler with it and retry the request. The server validates the token and grants access.

---

## For Developers: Using the Server

### Quick Start

1. **Set up OAuth credentials** (see [setup-auth-github.md](./setup-auth-github.md))

2. **Configure environment variables:**
   ```bash
   OAUTH_CLIENT_ID=your_github_client_id
   OAUTH_CLIENT_SECRET=your_github_client_secret
   OAUTH_SCOPES=read:user,repo
   ```

3. **Start the server:**
   ```bash
   python -m mcp_server.main
   ```

4. **Check the logs** for authorization metadata:
   ```
   INFO - OAuth is configured
   INFO - OAuth scopes: read:user
   INFO - OAuth Issuer: https://github.com
   INFO - Authorization Endpoint: https://github.com/login/oauth/authorize
   INFO - Token Endpoint: https://github.com/login/oauth/access_token
   INFO - Supported Grant Types: authorization_code, refresh_token
   INFO - PKCE Methods: S256
   ```

### Available Tools

#### `get_github_user_info` (Requires OAuth)

Fetches authenticated GitHub user information and repositories.

**Parameters:**
- `include_repos` (boolean, default: true): Include repository data
- `repo_limit` (integer, default: 10): Max repositories (1-100)

**Authorization Required:** Yes

**Example:**
```json
{
  "name": "get_github_user_info",
  "arguments": {
    "include_repos": true,
    "repo_limit": 5
  }
}
```

#### `analyze_code_with_llm` (No OAuth Required)

Uses MCP sampling to analyze code snippets.

**Parameters:**
- `code` (string, required): Code to analyze
- `analysis_type` (string): Type of analysis (explain, review, suggest_improvements, find_bugs, security_review)
- `max_tokens` (integer, default: 500): Max LLM response tokens

**Authorization Required:** No

---

## For Integrators: Client Implementation

### Discovering Authorization Metadata

The server provides RFC 8414 compliant authorization metadata. Access it via:

```python
from mcp_server.config import settings

metadata = settings.get_authorization_metadata()
print(metadata)
```

**Output:**
```json
{
  "issuer": "https://github.com",
  "authorization_endpoint": "https://github.com/login/oauth/authorize",
  "token_endpoint": "https://github.com/login/oauth/access_token",
  "scopes_supported": ["read:user"],
  "response_types_supported": ["code"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic"]
}
```

### Handling Authorization Errors

When your client receives error code `-32001`, extract OAuth metadata:

```python
def handle_auth_error(error_response):
    if error_response.get("code") == -32001:
        auth_data = error_response.get("data", {})
        
        # Extract OAuth endpoints
        auth_url = auth_data.get("authorization_url")
        token_url = auth_data.get("token_url")
        scopes = auth_data.get("scopes")
        
        # Initiate OAuth flow
        initiate_oauth_flow(auth_url, token_url, scopes)
```

### Implementing PKCE Flow

The server requires PKCE for all authorization code flows:

```python
import secrets
import hashlib
import base64

def generate_pkce_pair():
    """Generate code verifier and challenge for PKCE."""
    # Generate code verifier
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')
    
    # Generate code challenge
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge

# Use in authorization request
code_verifier, code_challenge = generate_pkce_pair()
auth_params = {
    "code_challenge": code_challenge,
    "code_challenge_method": "S256"
}
```

### Including Resource Indicators

Per RFC 8707, include the resource parameter in token requests:

```python
token_params = {
    "grant_type": "authorization_code",
    "code": authorization_code,
    "code_verifier": code_verifier,
    "resource": "https://api.github.com"  # Resource indicator
}
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OAUTH_CLIENT_ID` | OAuth client ID | - | Yes |
| `OAUTH_CLIENT_SECRET` | OAuth client secret | - | Yes |
| `OAUTH_AUTHORIZATION_URL` | Authorization endpoint | GitHub URL | No |
| `OAUTH_TOKEN_URL` | Token endpoint | GitHub URL | No |
| `OAUTH_SCOPES` | Comma-separated scopes | read:user | No |
| `OAUTH_ISSUER` | OAuth issuer URL | https://github.com | No |
| `OAUTH_GRANT_TYPES_SUPPORTED` | Supported grant types | authorization_code,refresh_token | No |
| `OAUTH_CODE_CHALLENGE_METHODS_SUPPORTED` | PKCE methods | S256 | No |
| `OAUTH_RESPONSE_TYPES_SUPPORTED` | Response types | code | No |
| `OAUTH_TOKEN_ENDPOINT_AUTH_METHODS` | Token auth methods | client_secret_post,client_secret_basic | No |

### Configuration Example

**.env file:**
```bash
# Required
OAUTH_CLIENT_ID=your_client_id_here
OAUTH_CLIENT_SECRET=your_client_secret_here

# Optional - GitHub defaults
OAUTH_AUTHORIZATION_URL=https://github.com/login/oauth/authorize
OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
OAUTH_SCOPES=read:user,repo
OAUTH_ISSUER=https://github.com

# OAuth Metadata (usually defaults are fine)
OAUTH_GRANT_TYPES_SUPPORTED=authorization_code,refresh_token
OAUTH_CODE_CHALLENGE_METHODS_SUPPORTED=S256
OAUTH_RESPONSE_TYPES_SUPPORTED=code
OAUTH_TOKEN_ENDPOINT_AUTH_METHODS=client_secret_post,client_secret_basic
```

---

## Troubleshooting

### Error: "OAuth is not configured"

**Symptom:** Server returns error about missing OAuth configuration

**Solution:**
1. Check that `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET` are set
2. Verify `.env` file exists and is loaded
3. Check environment variable names (case-sensitive)

**Verify configuration:**
```bash
python -c "from mcp_server.config import settings; print(settings.is_oauth_configured())"
```

### Error: "Authentication required" (-32001)

**Symptom:** Tool calls return error code -32001

**Solution:** This is expected for unauthenticated requests. Follow the OAuth flow:

1. Extract OAuth metadata from error response
2. Use the `authorization_url` to get authorization code
3. Exchange code for access token at `token_url`
4. Configure OAuth handler with the token
5. Retry the request

### Error: Invalid authorization code

**Symptom:** Token exchange fails with invalid code error

**Solution:**
- Authorization codes expire quickly (usually 10 minutes)
- Codes can only be used once
- Request a new authorization code

### Error: Invalid PKCE verifier

**Symptom:** Token exchange fails with PKCE error

**Solution:**
- Ensure you're using the same `code_verifier` used to generate the `code_challenge`
- Verify PKCE method is S256
- Check that verifier wasn't modified (URL encoding issues)

### Server not exposing authorization metadata

**Symptom:** Can't find OAuth endpoints

**Solution:**
1. Check server logs on startup for authorization info
2. Verify OAuth is configured (see above)
3. Call `settings.get_authorization_metadata()` to retrieve metadata

---

## Security Best Practices

### 1. Protect Client Credentials

- **Never commit** `OAUTH_CLIENT_SECRET` to version control
- Use environment variables or secure secret management
- Rotate credentials if exposed

### 2. Use PKCE Always

- PKCE is **required** for this server
- Prevents authorization code interception attacks
- Use S256 method (SHA-256)

### 3. Validate Resource Indicators

- Always include the `resource` parameter in token requests
- Ensures tokens are scoped to specific resources
- Prevents token misuse across different APIs

### 4. Implement Token Refresh

- Access tokens expire (GitHub: typically 8 hours)
- Use refresh tokens to obtain new access tokens
- Store refresh tokens securely

### 5. Minimize Scopes

- Request only the scopes you need
- For read-only access, use `read:user` not `user`
- Review GitHub's scope documentation

### 6. Secure Token Storage

- Never log access tokens
- Don't expose tokens in error messages
- Use secure storage mechanisms (keyring, vault)

### 7. Validate Redirect URIs

- Configure exact redirect URIs in GitHub OAuth app
- Don't use wildcards
- Use HTTPS in production

### 8. Monitor Token Usage

- Log authorization attempts
- Monitor for unusual patterns
- Implement rate limiting if needed

---

## Advanced Topics

### Custom OAuth Providers

To use a different OAuth provider (not GitHub):

1. Update environment variables:
   ```bash
   OAUTH_ISSUER=https://your-provider.com
   OAUTH_AUTHORIZATION_URL=https://your-provider.com/oauth/authorize
   OAUTH_TOKEN_URL=https://your-provider.com/oauth/token
   OAUTH_SCOPES=your_required_scopes
   ```

2. Update the resource URI if needed:
   ```python
   oauth_handler = OAuthHandler(resource_uri="https://your-api.com")
   ```

### Token Refresh Flow

Example of refreshing an access token:

```python
from mcp_server.oauth_handler import OAuthHandler

oauth_handler = OAuthHandler()
oauth_handler.refresh_token = "your_refresh_token"

# Refresh the access token
new_token = await oauth_handler.refresh_access_token()

print(f"New access token: {new_token['access_token']}")
```

### Logging Authorization Events

The server logs authorization events at different levels:

- `INFO`: Successful authorization metadata loading
- `WARNING`: Authentication required (user not authenticated)
- `ERROR`: OAuth configuration missing or invalid

Enable debug logging for detailed OAuth flow information:
```bash
LOG_LEVEL=DEBUG python -m mcp_server.main
```

---

## Related Documentation

- [GitHub OAuth Setup Guide](./setup-auth-github.md) - Step-by-step GitHub OAuth app creation
- [MCP Authorization Analysis](./MCP_AUTHORIZATION_ANALYSIS.md) - Technical deep dive
- [Authorization Flow Summary](./AUTHORIZATION_FLOW_SUMMARY.md) - Quick reference
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) - Official spec

---

## Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/issues)
- Check existing documentation
- Review the troubleshooting section above

---

**Last Updated:** 2025-10-25  
**Version:** 1.0  
**MCP Specification Compliance:** 2025-06-18
