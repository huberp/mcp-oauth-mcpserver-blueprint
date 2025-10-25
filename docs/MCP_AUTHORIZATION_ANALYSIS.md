# MCP Authorization Specification Analysis and Implementation Guide

**Document Version:** 1.0  
**Date:** 2025-10-25  
**MCP Specification Version:** 2025-06-18  
**Author:** GitHub Copilot Agent

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [MCP Specification Understanding](#mcp-specification-understanding)
3. [RFC 8414 Mapping to MCP](#rfc-8414-mapping-to-mcp)
4. [Current Implementation Analysis](#current-implementation-analysis)
5. [Sequence Diagrams](#sequence-diagrams)
6. [Gaps and Deviations](#gaps-and-deviations)
7. [Implementation Todos](#implementation-todos)
8. [References](#references)

---

## Executive Summary

This document provides a comprehensive analysis of MCP (Model Context Protocol) authorization requirements per the 2025-06-18 specification and identifies gaps in the current implementation.

### Key Findings

**✅ What's Working:**
- OAuth 2.1 with PKCE correctly implemented
- RFC 8707 Resource Indicators already in place
- Token management and refresh logic solid
- Proper JSON-RPC communication via stdio

**❌ Critical Gaps:**
- No authorization server metadata exposure
- Missing proper error responses for unauthorized requests
- Server capabilities don't declare auth requirements
- No WWW-Authenticate equivalent for stdio transport

**Impact:** The server works but doesn't fully comply with MCP 2025-06-18 spec, making it harder for generic MCP clients to discover and use OAuth authentication properly.

---

## MCP Specification Understanding

### MCP Servers as OAuth Resource Servers

Per MCP Specification 2025-06-18, MCP servers are classified as **OAuth Resource Servers**, not Authorization Servers.

**What this means:**
- **Resource Server Role**: Validates access tokens issued by an external Authorization Server
- **No Token Issuance**: Does not issue tokens itself
- **Token Validation**: Verifies JWT tokens for user identity and authorization
- **Metadata Advertisement**: Must advertise the location of the Authorization Server

### Key Authorization Components

#### 1. Server Initialization with Capabilities

During the `initialize` handshake, servers must declare their capabilities including authorization requirements.

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": { "listChanged": true },
      "prompts": { "listChanged": true }
    },
    "serverInfo": {
      "name": "mcp-oauth-server",
      "version": "0.1.0"
    }
  }
}
```

**Missing:** Authorization metadata should be included here to help clients discover auth requirements.

#### 2. Resource Indicators (RFC 8707)

MCP clients must use Resource Indicators to specify which resource server the access token is intended for.

**Current Status:** ✅ Already implemented in `oauth_handler.py`

```python
# In exchange_code_for_token and refresh_access_token
resource=self.resource_uri,  # RFC 8707 Resource Indicator
```

#### 3. Unauthorized Request Handling

When a client requests a protected resource without proper authentication, the server must:
- Return an error (401 for HTTP, JSON-RPC error for stdio)
- Include metadata pointing to the authorization server
- Provide information on required scopes

**Current Status:** ❌ Returns plain text instructions, not structured error

#### 4. Authorization Server Metadata

Servers should expose or reference authorization server metadata that includes:
- Authorization endpoint
- Token endpoint
- Supported scopes
- Supported grant types
- Issuer identifier

**Current Status:** ❌ Not implemented

---

## RFC 8414 Mapping to MCP

### RFC 8414: OAuth 2.0 Authorization Server Metadata

RFC 8414 defines how OAuth clients can discover metadata about an Authorization Server via a well-known endpoint: `/.well-known/oauth-authorization-server`

### How RFC 8414 Maps to MCP

Since MCP servers use **stdio transport** (not HTTP), the mapping is conceptual:

| RFC 8414 Concept | MCP Implementation |
|------------------|-------------------|
| `.well-known/oauth-authorization-server` endpoint | Authorization metadata in server initialization response |
| HTTP GET request | Part of `initialize` result |
| JSON metadata document | Embedded in `serverInfo` or custom field |
| Authorization endpoint URL | Configured via environment variables |
| Token endpoint URL | Configured via environment variables |
| Scopes supported | Listed in server capabilities |

### Required Metadata Fields (per RFC 8414)

**Mandatory:**
- `issuer`: URL of the authorization server
- `authorization_endpoint`: URL for authorization requests
- `token_endpoint`: URL for token requests
- `response_types_supported`: e.g., `["code"]`
- `grant_types_supported`: e.g., `["authorization_code", "refresh_token"]`

**Recommended:**
- `scopes_supported`: List of supported OAuth scopes
- `token_endpoint_auth_methods_supported`: e.g., `["client_secret_basic", "client_secret_post"]`
- `code_challenge_methods_supported`: e.g., `["S256"]` (for PKCE)

### MCP Adaptation for Stdio Transport

Since MCP uses stdio (not HTTP), the metadata should be provided:
1. **During initialization**: Include auth server info in `serverInfo` or `capabilities`
2. **In error responses**: When unauthorized, include auth metadata in error details
3. **In configuration**: Document auth requirements in server documentation

---

## Current Implementation Analysis

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   MCP Host (VS Code)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │       AI Assistant / MCP Client                     │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │ stdio (JSON-RPC)                            │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│           MCP Server (Python/FastMCP)                        │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  server.py: MCP Protocol Handler                  │      │
│  │  - list_tools()                                   │      │
│  │  - call_tool()                                    │      │
│  │  - list_prompts()                                 │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  oauth_handler.py: OAuth 2.1 + PKCE              │      │
│  │  - get_authorization_url()                        │      │
│  │  - exchange_code_for_token() [RFC 8707 ✓]       │      │
│  │  - refresh_access_token() [RFC 8707 ✓]          │      │
│  │  - get_auth_headers()                            │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  api_client.py: GitHub API Client                │      │
│  │  - get_user_info()                                │      │
│  │  - get_user_repos()                               │      │
│  └──────────────────────────────────────────────────┘      │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS + OAuth Bearer Token
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         GitHub (Authorization Server + API)                  │
│  - OAuth Authorization Endpoint                              │
│  - OAuth Token Endpoint                                      │
│  - GitHub API (Resource Server)                              │
└─────────────────────────────────────────────────────────────┘
```

### Code Analysis

#### 1. `server.py` - MCP Server Implementation

**Current initialization:** Uses FastMCP's `Server` class
```python
server = Server(settings.server_name)
```

**Issues:**
- No custom `serverInfo` with auth metadata
- No auth capabilities declared
- Uses default FastMCP initialization

**Tool handling:**
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "get_github_user_info":
        return await handle_get_github_user_info(arguments)
```

**Unauthorized response (current):**
```python
if not oauth_handler.is_authenticated():
    auth_url, state, code_verifier = oauth_handler.get_authorization_url()
    instructions = f"""OAuth authentication required.
    
Please complete the following steps:
1. Open this URL in your browser: {auth_url}
...
"""
    return [TextContent(type="text", text=instructions)]
```

**Issues:**
- Returns plain text instructions
- Not a proper JSON-RPC error
- Doesn't include structured auth metadata

#### 2. `oauth_handler.py` - OAuth Implementation

**Strengths:**
- ✅ PKCE implementation correct
- ✅ RFC 8707 Resource Indicators included
- ✅ Token refresh logic solid

```python
# RFC 8707 Resource Indicator
token = await client.fetch_token(
    url=self.token_url,
    grant_type="authorization_code",
    code=code,
    code_verifier=code_verifier,
    redirect_uri=redirect_uri,
    resource=self.resource_uri,  # ✅ RFC 8707
)
```

**Missing:**
- No method to expose authorization server metadata
- No helper to create auth error responses

#### 3. `config.py` - Configuration

**Current config:**
```python
oauth_client_id: str = ""
oauth_client_secret: str = ""
oauth_authorization_url: str = "https://github.com/login/oauth/authorize"
oauth_token_url: str = "https://github.com/login/oauth/access_token"
oauth_scopes: str = "read:user"
```

**Missing:**
- No authorization server issuer URL
- No metadata about supported grant types
- No PKCE methods declaration

---

## Sequence Diagrams

### Current Flow (Partially Compliant)

```
┌────────┐                  ┌────────────┐                 ┌──────────┐
│  MCP   │                  │    MCP     │                 │  GitHub  │
│ Client │                  │   Server   │                 │  OAuth   │
└───┬────┘                  └─────┬──────┘                 └────┬─────┘
    │                             │                             │
    │ 1. initialize               │                             │
    ├────────────────────────────>│                             │
    │                             │                             │
    │ 2. initialize response      │                             │
    │    (capabilities, serverInfo)│                            │
    │<────────────────────────────┤                             │
    │                             │                             │
    │ 3. tools/list               │                             │
    ├────────────────────────────>│                             │
    │                             │                             │
    │ 4. tool list (with metadata)│                             │
    │<────────────────────────────┤                             │
    │                             │                             │
    │ 5. call_tool(get_github_user_info)                        │
    ├────────────────────────────>│                             │
    │                             │                             │
    │                             │ 6. Check auth               │
    │                             │    (not authenticated)      │
    │                             │                             │
    │ 7. text response with       │                             │
    │    OAuth URL and instructions│                            │
    │<────────────────────────────┤                             │
    │                             │                             │
    │ 8. User manually opens URL  │                             │
    ├─────────────────────────────┼────────────────────────────>│
    │                             │                             │
    │                             │     9. Authorize            │
    │<────────────────────────────┼─────────────────────────────┤
    │                             │                             │
    │ 10. User manually exchanges │                             │
    │     code for token          │                             │
    ├─────────────────────────────┼────────────────────────────>│
    │                             │                             │
    │                             │    11. Access token         │
    │<────────────────────────────┼─────────────────────────────┤
    │                             │                             │
    │ 12. retry call_tool         │                             │
    │     (with token)            │                             │
    ├────────────────────────────>│                             │
    │                             │                             │
    │                             │ 13. API call with token     │
    │                             ├────────────────────────────>│
    │                             │                             │
    │                             │ 14. User data               │
    │                             │<────────────────────────────┤
    │                             │                             │
    │ 15. tool response           │                             │
    │     (user data)             │                             │
    │<────────────────────────────┤                             │
    │                             │                             │
```

**Issues with current flow:**
- Step 7: Should be JSON-RPC error with auth metadata
- Step 8-11: Manual process, should be automated by client using metadata
- No auth metadata in initialize response (step 2)

### Proposed Compliant Flow

```
┌────────┐                  ┌────────────┐                 ┌──────────┐
│  MCP   │                  │    MCP     │                 │  GitHub  │
│ Client │                  │   Server   │                 │  OAuth   │
└───┬────┘                  └─────┬──────┘                 └────┬─────┘
    │                             │                             │
    │ 1. initialize               │                             │
    ├────────────────────────────>│                             │
    │                             │                             │
    │ 2. initialize response      │                             │
    │    WITH auth metadata       │                             │
    │    {                        │                             │
    │      serverInfo: {          │                             │
    │        authorization: {     │                             │
    │          server: "github",  │                             │
    │          endpoints: {...}   │                             │
    │        }                    │                             │
    │      }                      │                             │
    │    }                        │                             │
    │<────────────────────────────┤                             │
    │                             │                             │
    │ 3. tools/list               │                             │
    ├────────────────────────────>│                             │
    │                             │                             │
    │ 4. tool list                │                             │
    │    (tools marked requires_auth)                           │
    │<────────────────────────────┤                             │
    │                             │                             │
    │ 5. call_tool(get_github_user_info)                        │
    ├────────────────────────────>│                             │
    │                             │                             │
    │                             │ 6. Check auth               │
    │                             │    (not authenticated)      │
    │                             │                             │
    │ 7. JSON-RPC ERROR           │                             │
    │    {                        │                             │
    │      code: -32001,          │                             │
    │      message: "Unauthorized",│                            │
    │      data: {                │                             │
    │        authorization: {     │                             │
    │          type: "oauth2",    │                             │
    │          server: {...}      │                             │
    │        }                    │                             │
    │      }                      │                             │
    │    }                        │                             │
    │<────────────────────────────┤                             │
    │                             │                             │
    │ 8. Client extracts auth     │                             │
    │    metadata from error      │                             │
    │                             │                             │
    │ 9. Authorization request    │                             │
    │    (automated by client)    │                             │
    ├─────────────────────────────┼────────────────────────────>│
    │                             │                             │
    │                             │    10. User authorizes      │
    │<────────────────────────────┼─────────────────────────────┤
    │                             │                             │
    │ 11. Token request           │                             │
    │     (with resource indicator)                             │
    ├─────────────────────────────┼────────────────────────────>│
    │                             │                             │
    │                             │    12. Access token         │
    │<────────────────────────────┼─────────────────────────────┤
    │                             │                             │
    │ 13. retry call_tool         │                             │
    │     (with token in context) │                             │
    ├────────────────────────────>│                             │
    │                             │                             │
    │                             │ 14. Validate token          │
    │                             │                             │
    │                             │ 15. API call                │
    │                             ├────────────────────────────>│
    │                             │                             │
    │                             │ 16. User data               │
    │                             │<────────────────────────────┤
    │                             │                             │
    │ 17. tool response           │                             │
    │     (user data)             │                             │
    │<────────────────────────────┤                             │
    │                             │                             │
```

**Improvements in proposed flow:**
- Initialize response includes auth metadata
- Error response is structured JSON-RPC error
- Client can automatically discover auth endpoints
- Token management can be automated by client

---

## Gaps and Deviations

### Gap #1: No Authorization Metadata in Server Initialization

**Specification Requirement:**
> MCP servers should advertise the location of their preferred Authorization Server

**Current State:**
Server initialization only includes basic serverInfo:
```python
server = Server(settings.server_name)
```

**Deviation:**
- No auth metadata in initialize response
- Clients cannot discover auth requirements automatically
- Manual configuration required

**Impact:** HIGH - Prevents automatic OAuth flow discovery

### Gap #2: Improper Unauthorized Error Response

**Specification Requirement:**
> When unauthorized, servers should respond with proper error and auth metadata

**Current State:**
Returns text content with instructions:
```python
return [TextContent(type="text", text=instructions)]
```

**Deviation:**
- Not a JSON-RPC error
- No structured auth metadata
- Plain text instead of machine-readable format

**Impact:** HIGH - Prevents automated error handling

### Gap #3: Tool Authorization Requirements Not Exposed

**Specification Requirement:**
> Tools should declare their authorization requirements

**Current State:**
Tools have `_meta.requires_auth` but this isn't a standard MCP field:
```python
_meta={
    "version": "1.0.0",
    "author": "MCP OAuth Server",
    "requires_auth": True,  # Non-standard field
}
```

**Deviation:**
- Uses non-standard `_meta` field
- Not exposed in standard tool schema
- Clients can't programmatically detect auth requirements

**Impact:** MEDIUM - Reduces client discoverability

### Gap #4: No Authorization Server Configuration Metadata

**Specification Requirement:**
> Expose metadata about supported grant types, scopes, PKCE methods

**Current State:**
Configuration exists but not exposed:
```python
oauth_authorization_url: str = "https://github.com/login/oauth/authorize"
oauth_token_url: str = "https://github.com/login/oauth/access_token"
oauth_scopes: str = "read:user"
```

**Deviation:**
- Metadata not accessible to clients
- No declaration of supported features
- No issuer URL

**Impact:** MEDIUM - Limits interoperability

### Gap #5: Stdio Transport Limitations

**Note:** This is a fundamental architectural choice, not a bug.

**Specification Challenge:**
> MCP spec defines WWW-Authenticate header for HTTP transport

**Current State:**
Server uses stdio transport

**Consideration:**
- Stdio transport doesn't support HTTP headers
- Must adapt HTTP concepts to JSON-RPC
- Need equivalent error structure

**Impact:** LOW - Design choice, needs adaptation not fix

---

## Implementation Todos

### Phase 1: Authorization Metadata (High Priority)

#### Todo 1.1: Add Authorization Server Metadata to Config
**File:** `src/mcp_server/config.py`

**Changes:**
```python
# Add new fields
oauth_issuer: str = "https://github.com"
oauth_grant_types_supported: str = "authorization_code,refresh_token"
oauth_code_challenge_methods_supported: str = "S256"
oauth_response_types_supported: str = "code"
oauth_token_endpoint_auth_methods: str = "client_secret_post"

def get_authorization_metadata(self) -> dict[str, Any]:
    """Get RFC 8414 compliant authorization server metadata."""
    return {
        "issuer": self.oauth_issuer,
        "authorization_endpoint": self.oauth_authorization_url,
        "token_endpoint": self.oauth_token_url,
        "scopes_supported": self.oauth_scopes_list,
        "response_types_supported": [
            s.strip() for s in self.oauth_response_types_supported.split(",")
        ],
        "grant_types_supported": [
            s.strip() for s in self.oauth_grant_types_supported.split(",")
        ],
        "code_challenge_methods_supported": [
            s.strip() for s in self.oauth_code_challenge_methods_supported.split(",")
        ],
        "token_endpoint_auth_methods_supported": [
            s.strip() for s in self.oauth_token_endpoint_auth_methods.split(",")
        ],
    }
```

**Tests Required:**
- Test metadata generation
- Test configuration loading
- Validate RFC 8414 compliance

#### Todo 1.2: Expose Auth Metadata in Server Initialization
**File:** `src/mcp_server/server.py`

**Changes:**
```python
def create_mcp_server() -> tuple[Server, OAuthHandler, APIClient]:
    # Create server with custom initialization
    server = Server(settings.server_name)
    
    # Add authorization metadata to server capabilities
    # Note: This may require extending FastMCP or using custom fields
    
    # Option 1: Custom serverInfo field
    # Option 2: Add to capabilities
    # Option 3: Document in server description
```

**Research Needed:**
- Check if FastMCP supports custom serverInfo fields
- Determine best way to expose auth metadata
- Ensure MCP spec compliance

#### Todo 1.3: Add Authorization Error Helper
**File:** `src/mcp_server/oauth_handler.py`

**Changes:**
```python
def get_authorization_error_response(self) -> dict[str, Any]:
    """
    Generate standardized authorization error response.
    
    Returns JSON-RPC error structure with auth metadata.
    """
    return {
        "code": -32001,  # Custom error code for auth required
        "message": "Authentication required",
        "data": {
            "type": "oauth2",
            "authorization_url": self.authorization_url,
            "token_url": self.token_url,
            "scopes": self.scopes,
            "grant_type": "authorization_code",
            "code_challenge_method": "S256",
        }
    }
```

**Tests Required:**
- Test error response structure
- Validate all required fields present

### Phase 2: Error Handling (High Priority)

#### Todo 2.1: Update Tool Error Responses
**File:** `src/mcp_server/server.py`

**Changes:**
```python
async def handle_get_github_user_info(arguments: dict[str, Any]) -> list[TextContent]:
    # Check if authenticated
    if not oauth_handler.is_authenticated():
        # Instead of returning text instructions, raise proper error
        error_data = oauth_handler.get_authorization_error_response()
        
        # Format as structured error message
        error_message = json.dumps({
            "error": error_data,
            "instructions": "Please authenticate using the provided OAuth endpoints"
        }, indent=2)
        
        return [TextContent(type="text", text=error_message)]
```

**Better approach:** Research if FastMCP supports raising JSON-RPC errors directly

**Tests Required:**
- Test error format
- Verify client can parse error
- Test with MCP Inspector

### Phase 3: Documentation (Medium Priority)

#### Todo 3.1: Create Authorization Flow Documentation
**File:** `docs/AUTHORIZATION_FLOW.md`

**Content:**
- Complete authorization flow diagrams
- Step-by-step guide for clients
- Code examples for OAuth integration
- Troubleshooting guide

#### Todo 3.2: Update README
**File:** `README.md`

**Changes:**
- Add section on authorization
- Document auth metadata structure
- Update architecture diagram
- Add OAuth flow examples

#### Todo 3.3: Update RESEARCH.md
**File:** `docs/RESEARCH.md`

**Changes:**
- Document MCP 2025-06-18 changes
- Add RFC 8414 details
- Update implementation notes

### Phase 4: Testing (Medium Priority)

#### Todo 4.1: Add Authorization Metadata Tests
**File:** `tests/test_config.py`

**Tests:**
- Test `get_authorization_metadata()`
- Validate all required fields
- Test with different configurations

#### Todo 4.2: Add Authorization Error Tests
**File:** `tests/test_server.py` (new file)

**Tests:**
- Test error response structure
- Test unauthorized tool calls
- Validate error metadata

#### Todo 4.3: Integration Tests with MCP Inspector
**File:** `.github/workflows/mcp-tester.yml`

**Enhancement:**
- Test auth metadata exposure
- Validate error responses
- Test with mock OAuth server

### Phase 5: Optional Enhancements (Low Priority)

#### Todo 5.1: Token Validation
**File:** `src/mcp_server/oauth_handler.py`

**Enhancement:**
- Add JWT token validation
- Verify token signature
- Check token expiration
- Validate scopes

#### Todo 5.2: Authorization Server Discovery
**File:** `src/mcp_server/oauth_handler.py`

**Enhancement:**
- Fetch authorization server metadata dynamically
- Support multiple auth servers
- Cache metadata

#### Todo 5.3: Enhanced Tool Metadata
**File:** `src/mcp_server/server.py`

**Enhancement:**
- Add standard fields for auth requirements
- Document required scopes per tool
- Add auth examples to tool descriptions

---

## Summary and Recommendations

### Critical Actions Required

1. **Add authorization metadata to server initialization**
   - Allows clients to discover auth requirements
   - Enables automated OAuth flows
   - **Priority:** HIGH

2. **Implement proper error responses**
   - Structure errors as JSON-RPC
   - Include auth metadata in errors
   - **Priority:** HIGH

3. **Document authorization flows**
   - Create comprehensive guides
   - Add sequence diagrams
   - **Priority:** MEDIUM

4. **Add comprehensive tests**
   - Test all auth scenarios
   - Validate with MCP Inspector
   - **Priority:** MEDIUM

### What's Already Good

- ✅ OAuth 2.1 with PKCE implementation
- ✅ RFC 8707 Resource Indicators
- ✅ Token refresh logic
- ✅ Secure configuration management

### Estimated Effort

| Phase | Effort | Priority |
|-------|--------|----------|
| Phase 1: Authorization Metadata | 4-6 hours | HIGH |
| Phase 2: Error Handling | 3-4 hours | HIGH |
| Phase 3: Documentation | 3-4 hours | MEDIUM |
| Phase 4: Testing | 4-5 hours | MEDIUM |
| Phase 5: Optional Enhancements | 6-8 hours | LOW |

**Total:** 20-27 hours for complete implementation

### Next Steps

1. **Get approval from @huberp** on this analysis and implementation plan
2. **Start with Phase 1** - Add authorization metadata
3. **Implement Phase 2** - Fix error responses
4. **Complete testing** - Validate with MCP Inspector
5. **Update documentation** - Make it easy for users

---

## References

### MCP Specification
- [MCP Specification 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18)
- [MCP Authorization Guide](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [MCP Lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)

### OAuth Standards
- [RFC 8414: OAuth 2.0 Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)
- [RFC 8707: Resource Indicators for OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc8707)
- [RFC 7636: PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
- [OAuth 2.1](https://oauth.net/2.1/)

### Implementation Guides
- [Auth0 MCP Auth Guide](https://auth0.com/blog/mcp-specs-update-all-about-auth/)
- [Logto MCP Implementation Guide](https://blog.logto.io/mcp-auth-implementation-guide-2025-06-18)
- [Aaron Parecki: OAuth for MCP](https://aaronparecki.com/2025/04/03/15/oauth-for-model-context-protocol)

### Related Issues
- [MCP GitHub Issue #205: Treat MCP server as OAuth resource server](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/205)

---

**Document End**
