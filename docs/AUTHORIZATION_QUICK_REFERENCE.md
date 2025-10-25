# MCP OAuth Server - Authorization Quick Reference

**Quick access guide for authorization features implemented in MCP Specification 2025-06-18 compliance.**

---

## Quick Links

- 📖 [Complete Authorization Guide](./AUTHORIZATION_GUIDE.md)
- 🔧 [GitHub OAuth Setup](./setup-auth-github.md)
- 📊 [Technical Analysis](./MCP_AUTHORIZATION_ANALYSIS.md)
- 📋 [Executive Summary](./AUTHORIZATION_FLOW_SUMMARY.md)

---

## At a Glance

### What Changed?

✅ **RFC 8414 Authorization Metadata** - Server now exposes OAuth endpoints  
✅ **Structured Error Responses** - JSON-RPC errors with OAuth metadata  
✅ **Client Autodiscovery** - Clients can automatically find OAuth configuration  
✅ **MCP 2025-06-18 Compliance** - Full spec compliance

### Configuration

**New Environment Variables:**
```bash
# OAuth Authorization Server Metadata (RFC 8414)
OAUTH_ISSUER=https://github.com
OAUTH_GRANT_TYPES_SUPPORTED=authorization_code,refresh_token
OAUTH_CODE_CHALLENGE_METHODS_SUPPORTED=S256
```

### Code Examples

**Get Authorization Metadata:**
```python
from mcp_server.config import settings

metadata = settings.get_authorization_metadata()
print(metadata["authorization_endpoint"])
# Output: https://github.com/login/oauth/authorize
```

**Handle Authorization Errors:**
```python
from mcp_server.oauth_handler import OAuthHandler

oauth_handler = OAuthHandler()
error_response = oauth_handler.get_authorization_error_response()

# Returns:
# {
#   "code": -32001,
#   "message": "Authentication required",
#   "data": {
#     "type": "oauth2",
#     "authorization_url": "...",
#     "token_url": "...",
#     "scopes": [...],
#     "code_challenge_method": "S256"
#   }
# }
```

---

## Standards Compliance

| Standard | Description | Status |
|----------|-------------|--------|
| RFC 8414 | OAuth Authorization Server Metadata | ✅ Implemented |
| RFC 8707 | Resource Indicators for OAuth 2.0 | ✅ Implemented |
| RFC 7636 | PKCE for OAuth 2.0 | ✅ Implemented |
| MCP 2025-06-18 | MCP Authorization Specification | ✅ Compliant |

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| -32001 | Authentication required | Extract OAuth metadata from error and initiate OAuth flow |
| -32000 | OAuth not configured | Set OAUTH_CLIENT_ID and OAUTH_CLIENT_SECRET |

---

## Common Tasks

### Task: Check if OAuth is Configured
```python
from mcp_server.config import settings

if settings.is_oauth_configured():
    print("OAuth is ready!")
else:
    print("Please configure OAuth credentials")
```

### Task: Start Server and View Auth Config
```bash
python -m mcp_server.main
# Check logs for:
# INFO - OAuth Issuer: https://github.com
# INFO - Authorization Endpoint: ...
# INFO - Token Endpoint: ...
```

### Task: Get Authorization URL for Manual Testing
```python
from mcp_server.oauth_handler import OAuthHandler

oauth_handler = OAuthHandler()
auth_url, state, code_verifier = oauth_handler.get_authorization_url()

print(f"Visit: {auth_url}")
print(f"Save code_verifier: {code_verifier}")
```

---

## Testing

**Run Authorization Tests:**
```bash
# Test authorization metadata
pytest tests/test_config.py::test_get_authorization_metadata -v

# Test error responses
pytest tests/test_oauth_handler.py::test_get_authorization_error_response -v

# Run all tests
pytest
```

---

## Integration Checklist

When integrating with this server:

- [ ] Read the [Authorization Guide](./AUTHORIZATION_GUIDE.md)
- [ ] Configure OAuth app in GitHub
- [ ] Set environment variables
- [ ] Test authorization metadata retrieval
- [ ] Implement error handling for -32001 errors
- [ ] Test PKCE flow
- [ ] Verify resource indicators in token requests
- [ ] Test token refresh

---

## Need Help?

1. **Authorization Guide**: [docs/AUTHORIZATION_GUIDE.md](./AUTHORIZATION_GUIDE.md)
2. **GitHub OAuth Setup**: [docs/setup-auth-github.md](./setup-auth-github.md)
3. **Technical Deep Dive**: [docs/MCP_AUTHORIZATION_ANALYSIS.md](./MCP_AUTHORIZATION_ANALYSIS.md)
4. **Open an Issue**: [GitHub Issues](https://github.com/huberp/mcp-oauth-mcpserver-blueprint/issues)

---

**Last Updated:** 2025-10-25  
**Version:** 1.0
