# Code Review Issues - October 26, 2025

This document contains all 24 actionable issues identified in the comprehensive code review, organized by priority and category.

## Table of Contents

**High Priority (5 issues)**
1. [Increase Test Coverage to >80%](#issue-1-increase-test-coverage-to-80)
2. [Fix All Linting Errors](#issue-2-fix-all-linting-errors)
3. [Implement Persistent Session Storage](#issue-3-implement-persistent-session-storage)
4. [Add Token Expiry Validation and Refresh](#issue-4-add-token-expiry-validation-and-refresh)
5. [Add Comprehensive Input Validation](#issue-5-add-comprehensive-input-validation)

**Medium Priority (11 issues)**
6. [Implement Structured Logging](#issue-6-implement-structured-logging)
7. [Add Specific Exception Handling](#issue-7-add-specific-exception-handling)
8. [Implement Rate Limiting](#issue-8-implement-rate-limiting)
9. [Enhance Sampling Tool Implementation](#issue-9-enhance-sampling-tool-implementation)
10. [Add OAuth Configuration Validators](#issue-10-add-oauth-configuration-validators)
11. [Implement Metrics and Monitoring](#issue-11-implement-metrics-and-monitoring)
12. [Add API Documentation](#issue-12-add-api-documentation)
13. [Add Audit Logging](#issue-13-add-audit-logging)
14. [Improve Error Messages](#issue-14-improve-error-messages)
15. [Add Integration Tests](#issue-15-add-integration-tests)
16. [Extract OAuth Routes Module](#issue-16-extract-oauth-routes-module)

**Low Priority (8 issues)**
17. [Add Security Scanning to CI/CD](#issue-17-add-security-scanning-to-cicd)
18. [Implement HTTP Client Connection Pooling](#issue-18-implement-http-client-connection-pooling)
19. [Add Response Caching](#issue-19-add-response-caching)
20. [Enhance Health Check Endpoint](#issue-20-enhance-health-check-endpoint)
21. [Optimize Docker Image](#issue-21-optimize-docker-image)
22. [Add Troubleshooting Documentation](#issue-22-add-troubleshooting-documentation)
23. [Add Contributing Guide](#issue-23-add-contributing-guide)
24. [Extract HTML Templates](#issue-24-extract-html-templates)

---

## High Priority Issues

### Issue 1: Increase Test Coverage to >80%

**Category**: Testing  
**Priority**: High  
**Effort**: Medium (3-5 days)

#### Description
Current test coverage is 58%, with `server.py` at only 30% and `main.py` at 0%. Need comprehensive tests for all modules to reach project target of >80% coverage.

#### Goals
- Achieve >80% overall test coverage
- Reach 100% coverage on critical modules (server.py, main.py)
- Add tests for all OAuth routes, MCP tools, and prompts
- Cover edge cases and error scenarios

#### Files to Modify
- `tests/test_server.py` (create)
- `tests/test_main.py` (create)
- `tests/conftest.py` (enhance fixtures)
- `tests/test_api_client.py` (add edge cases)
- `tests/test_oauth_handler.py` (add edge cases)

#### Acceptance Criteria
- [ ] Overall coverage ≥ 80%
- [ ] server.py coverage ≥ 90%
- [ ] main.py coverage ≥ 80%
- [ ] All OAuth routes tested (/oauth/authorize, /oauth/callback, metadata)
- [ ] All MCP tools tested (get_github_user_info, analyze_code_with_llm)
- [ ] All MCP prompts tested (github_user_summary)
- [ ] Session cleanup logic tested
- [ ] Error scenarios tested (expired sessions, invalid state, etc.)
- [ ] All tests passing with no regressions
- [ ] Coverage report generated in CI/CD

#### Implementation Notes
```python
# Example tests needed:

# tests/test_server.py
async def test_oauth_authorize_redirect():
    """Test OAuth authorization endpoint redirects correctly."""
    # Test authorization URL generation
    # Verify session creation
    # Check state and code_verifier stored

async def test_oauth_callback_success():
    """Test successful OAuth callback."""
    # Mock token exchange
    # Verify token storage
    # Check HTML response

async def test_oauth_callback_expired_session():
    """Test OAuth callback with expired session."""
    # Test session expiry logic
    # Verify error response

async def test_get_github_user_info_authenticated():
    """Test GitHub user info tool when authenticated."""
    # Mock API responses
    # Verify data structure
    # Check all fields

async def test_get_github_user_info_not_authenticated():
    """Test GitHub user info tool error when not authenticated."""
    # Verify structured error response
    # Check OAuth metadata in error

# tests/test_main.py
def test_main_startup():
    """Test main function starts server."""
    # Mock asyncio.run
    # Verify server configuration

def test_main_keyboard_interrupt():
    """Test graceful shutdown on Ctrl+C."""
    # Mock KeyboardInterrupt
    # Verify clean exit
```

---

### Issue 2: Fix All Linting Errors

**Category**: Code Quality  
**Priority**: High  
**Effort**: Small (1-2 days)

#### Description
Ruff reports 37 linting errors including whitespace issues (19 auto-fixable), unused imports, import sorting, and exception chaining problems.

#### Goals
- Fix all 37 linting errors
- Ensure code passes `ruff check` without errors
- Maintain consistency with project style guidelines
- Ensure code passes `black --check`

#### Files to Modify
- `src/mcp_server/config.py` (whitespace)
- `src/mcp_server/main.py` (whitespace)
- `src/mcp_server/server.py` (whitespace, unused import, import order, exception chaining)

#### Acceptance Criteria
- [ ] All 37 ruff errors fixed
- [ ] `ruff check src/ tests/` passes with no errors
- [ ] `black --check src/ tests/` passes
- [ ] No trailing whitespace in any file
- [ ] All imports properly sorted
- [ ] Exception chaining uses `raise ... from`
- [ ] No unused imports
- [ ] All tests still passing after changes

#### Implementation Notes
```bash
# Quick fix for auto-fixable issues
ruff check --fix src/ tests/

# Manual fixes needed:
# 1. Remove unused import: secrets in server.py line 5
# 2. Fix exception chaining in server.py line 170:
#    raise ValueError(error_msg) from e

# 3. Organize imports in server.py (use ruff's --fix)
```

---

### Issue 3: Implement Persistent Session Storage

**Category**: Security  
**Priority**: High  
**Effort**: Medium (3-5 days)

#### Description
OAuth sessions currently stored in in-memory dictionary (`oauth_sessions`), which is lost on restart and not suitable for production. This is a security risk and prevents scaling.

#### Goals
- Replace in-memory session storage with persistent storage
- Support multiple server instances
- Add session expiry and cleanup
- Maintain security (encrypt sensitive data)

#### Files to Modify
- `src/mcp_server/session_manager.py` (create)
- `src/mcp_server/server.py` (refactor session handling)
- `pyproject.toml` (add redis or database dependency)
- `.env.example` (add session storage config)
- `docker-compose.yml` (add Redis service)
- `tests/test_session_manager.py` (create)

#### Acceptance Criteria
- [ ] Session storage abstracted to SessionManager class
- [ ] Redis backend implemented (with fallback to in-memory for dev)
- [ ] Sessions encrypted with secret key
- [ ] Automatic session expiry (configurable TTL)
- [ ] Background cleanup task implemented
- [ ] Support for multiple server instances
- [ ] Tests for session manager with >90% coverage
- [ ] Documentation updated with Redis setup
- [ ] Migration path from old sessions handled gracefully

#### Implementation Notes
```python
# src/mcp_server/session_manager.py

from abc import ABC, abstractmethod
from typing import Any
import json
from datetime import datetime, timedelta

class SessionManager(ABC):
    """Abstract session manager interface."""
    
    @abstractmethod
    async def create_session(self, state: str, data: dict[str, Any], ttl: int) -> None:
        """Create a new session."""
        pass
    
    @abstractmethod
    async def get_session(self, state: str) -> dict[str, Any] | None:
        """Get session data."""
        pass
    
    @abstractmethod
    async def delete_session(self, state: str) -> None:
        """Delete a session."""
        pass

class RedisSessionManager(SessionManager):
    """Redis-based session storage."""
    
    def __init__(self, redis_url: str, encryption_key: str):
        self.redis_url = redis_url
        self.encryption_key = encryption_key
    
    async def create_session(self, state: str, data: dict[str, Any], ttl: int) -> None:
        # Encrypt and store in Redis with TTL
        pass

class InMemorySessionManager(SessionManager):
    """In-memory session storage (for development)."""
    
    def __init__(self):
        self.sessions: dict[str, dict[str, Any]] = {}
```

---

### Issue 4: Add Token Expiry Validation and Refresh

**Category**: Security  
**Priority**: High  
**Effort**: Medium (3-5 days)

#### Description
Access tokens are not validated for expiry, and there's no automatic refresh mechanism. This could lead to API failures and poor user experience.

#### Goals
- Store token expiry time with access token
- Validate token expiry before API requests
- Automatically refresh expired tokens
- Handle refresh token expiry gracefully

#### Files to Modify
- `src/mcp_server/oauth_handler.py` (add expiry tracking)
- `src/mcp_server/api_client.py` (add refresh logic)
- `tests/test_oauth_handler.py` (add expiry tests)
- `tests/test_api_client.py` (add refresh tests)

#### Acceptance Criteria
- [ ] Token expiry time stored with access token
- [ ] `is_token_expired()` method implemented
- [ ] Automatic token refresh before API requests
- [ ] Refresh token rotation handled
- [ ] Graceful handling of refresh token expiry (re-authentication flow)
- [ ] Tests for token expiry validation
- [ ] Tests for automatic refresh
- [ ] Documentation updated with token lifecycle

#### Implementation Notes
```python
# src/mcp_server/oauth_handler.py

from datetime import datetime, timedelta

class OAuthHandler:
    def __init__(self, resource_uri: str | None = None) -> None:
        # ... existing code ...
        self.token_expires_at: datetime | None = None
    
    async def exchange_code_for_token(self, code: str, code_verifier: str, redirect_uri: str) -> dict[str, Any]:
        token = await client.fetch_token(...)
        
        self.access_token = token.get("access_token")
        self.refresh_token = token.get("refresh_token")
        
        # Store expiry time
        expires_in = token.get("expires_in", 3600)  # Default 1 hour
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        return token
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired."""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at
    
    async def ensure_valid_token(self) -> None:
        """Ensure we have a valid access token, refreshing if needed."""
        if not self.access_token:
            raise ValueError("Not authenticated")
        
        if self.is_token_expired():
            if not self.refresh_token:
                raise ValueError("Token expired and no refresh token available")
            await self.refresh_access_token()

# src/mcp_server/api_client.py

async def get_user_info(self) -> dict[str, Any]:
    # Ensure token is valid before making request
    await self.oauth_handler.ensure_valid_token()
    
    headers = self.oauth_handler.get_auth_headers()
    # ... rest of implementation
```

---

### Issue 5: Add Comprehensive Input Validation

**Category**: Security  
**Priority**: High  
**Effort**: Small (1-2 days)

#### Description
Tool parameters lack comprehensive validation. `repo_limit` should enforce 1-100 range, `username` should be validated, and other parameters need bounds checking.

#### Goals
- Add validation for all tool parameters
- Provide clear error messages for invalid inputs
- Use Pydantic models for input validation
- Document valid input ranges

#### Files to Modify
- `src/mcp_server/server.py` (add validation to tools)
- `src/mcp_server/models.py` (create, add Pydantic models)
- `tests/test_server.py` (add validation tests)

#### Acceptance Criteria
- [ ] All tool parameters validated
- [ ] repo_limit enforced to 1-100 range
- [ ] max_tokens enforced to 100-2000 range
- [ ] username validated (alphanumeric, hyphens, max 39 chars)
- [ ] Clear error messages for invalid inputs
- [ ] Pydantic models for structured validation
- [ ] Tests for all validation scenarios
- [ ] Documentation updated with valid ranges

#### Implementation Notes
```python
# src/mcp_server/models.py

from pydantic import BaseModel, Field, field_validator

class GetUserInfoParams(BaseModel):
    """Parameters for get_github_user_info tool."""
    
    include_repos: bool = Field(default=True, description="Include repository information")
    repo_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of repositories to fetch"
    )

class AnalyzeCodeParams(BaseModel):
    """Parameters for analyze_code_with_llm tool."""
    
    code: str = Field(min_length=1, description="Code snippet to analyze")
    analysis_type: str = Field(
        default="explain",
        description="Type of analysis"
    )
    max_tokens: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Maximum tokens for response"
    )
    
    @field_validator("analysis_type")
    @classmethod
    def validate_analysis_type(cls, v: str) -> str:
        valid_types = ["explain", "review", "suggest_improvements", "find_bugs", "security_review"]
        if v not in valid_types:
            raise ValueError(f"analysis_type must be one of: {', '.join(valid_types)}")
        return v

# src/mcp_server/server.py

@mcp.tool()
async def get_github_user_info(
    include_repos: bool = True,
    repo_limit: int = 10
) -> str:
    # Validate using Pydantic
    params = GetUserInfoParams(include_repos=include_repos, repo_limit=repo_limit)
    
    # Use validated params
    # ... rest of implementation
```

---

## Medium Priority Issues

### Issue 6: Implement Structured Logging

**Category**: Observability  
**Priority**: Medium  
**Effort**: Medium (3-5 days)

#### Description
Current logging is plain text format, making it hard to parse and analyze. Need structured JSON logging with correlation IDs for request tracing.

#### Goals
- Implement JSON-formatted structured logging
- Add correlation IDs for request tracing
- Include context in all log entries
- Make logs easily parseable by log aggregation tools

#### Files to Modify
- `src/mcp_server/logging_config.py` (create)
- `src/mcp_server/server.py` (add logging middleware)
- `src/mcp_server/main.py` (configure logging)
- `pyproject.toml` (add structlog dependency)
- `tests/test_logging.py` (create)

#### Acceptance Criteria
- [ ] structlog library integrated
- [ ] JSON log format for production
- [ ] Human-readable format for development
- [ ] Correlation ID added to all requests
- [ ] Context processors for common fields
- [ ] Log level configurable via environment
- [ ] Tests for logging configuration
- [ ] Documentation updated

#### Implementation Notes
```python
# src/mcp_server/logging_config.py

import structlog
from typing import Any

def configure_logging(environment: str = "development") -> None:
    """Configure structured logging."""
    
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if environment == "production":
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

---

### Issue 7: Add Specific Exception Handling

**Category**: Error Handling  
**Priority**: Medium  
**Effort**: Small (1-2 days)

#### Description
Several locations use generic `except Exception` which catches too broadly. Should catch specific exceptions for better error handling.

#### Goals
- Replace generic exception handlers with specific types
- Use `raise ... from` for exception chaining
- Improve error messages and context
- Ensure proper exception propagation

#### Files to Modify
- `src/mcp_server/server.py` (lines 167, 420)
- `tests/test_server.py` (add exception tests)

#### Acceptance Criteria
- [ ] No generic `except Exception` in production code
- [ ] All exception chains use `raise ... from`
- [ ] Specific exceptions caught (httpx.HTTPError, ValueError, etc.)
- [ ] Error context preserved in all cases
- [ ] Tests for specific exception scenarios
- [ ] Documentation of error handling patterns

#### Implementation Notes
```python
# Before (bad):
try:
    user_info = await api_client.get_user_info()
except Exception as e:
    error_msg = f"Error fetching GitHub user info: {str(e)}"
    logger.error(error_msg, exc_info=True)
    raise ValueError(error_msg)

# After (good):
try:
    user_info = await api_client.get_user_info()
except httpx.HTTPError as e:
    error_msg = f"GitHub API request failed: {str(e)}"
    logger.error(error_msg, exc_info=True)
    raise ValueError(error_msg) from e
except ValueError as e:
    # Re-raise authentication errors
    raise
except Exception as e:
    # Unexpected error
    error_msg = f"Unexpected error fetching user info: {str(e)}"
    logger.error(error_msg, exc_info=True)
    raise RuntimeError(error_msg) from e
```

---

### Issue 8: Implement Rate Limiting

**Category**: Security  
**Priority**: Medium  
**Effort**: Small (1-2 days)

#### Description
OAuth endpoints and API routes lack rate limiting, making them vulnerable to brute force attacks and abuse.

#### Goals
- Add rate limiting to OAuth endpoints
- Add rate limiting to MCP tools
- Configurable rate limits
- Clear error messages when rate limited

#### Files to Modify
- `src/mcp_server/server.py` (add rate limiting middleware)
- `pyproject.toml` (add slowapi dependency)
- `.env.example` (add rate limit configuration)
- `tests/test_rate_limiting.py` (create)

#### Acceptance Criteria
- [ ] Rate limiting on /oauth/authorize (10 requests/minute)
- [ ] Rate limiting on /oauth/callback (10 requests/minute)
- [ ] Rate limiting on MCP tools (100 requests/minute)
- [ ] 429 Too Many Requests status code returned
- [ ] Retry-After header included
- [ ] Rate limits configurable via environment
- [ ] Tests for rate limiting
- [ ] Documentation updated

#### Implementation Notes
```python
# Add to pyproject.toml:
# slowapi >= 0.1.9

# src/mcp_server/server.py

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Add to FastMCP app
mcp.app.state.limiter = limiter
mcp.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@mcp.custom_route("/oauth/authorize", methods=["GET"])
@limiter.limit("10/minute")
async def oauth_authorize(request: Request) -> RedirectResponse:
    # ... existing code
```

---

### Issue 9: Enhance Sampling Tool Implementation

**Category**: API Design  
**Priority**: Medium  
**Effort**: Medium (3-5 days)

#### Description
The `analyze_code_with_llm` tool currently returns placeholder text instead of actually using the MCP sampling API. Need to implement real sampling or provide a working workaround.

#### Goals
- Implement actual sampling API integration
- Or provide functional alternative using FastMCP patterns
- Update documentation with current limitations
- Add proper error handling

#### Files to Modify
- `src/mcp_server/server.py` (enhance analyze_code_with_llm)
- `tests/test_sampling.py` (enhance tests)
- `docs/sampling.md` (update documentation)

#### Acceptance Criteria
- [ ] Sampling tool works or has documented workaround
- [ ] Clear documentation of limitations
- [ ] Tests demonstrate functionality
- [ ] Error messages guide users appropriately
- [ ] Documentation updated with examples

#### Implementation Notes
```python
# Need to research FastMCP's sampling capabilities
# Options:
# 1. Use FastMCP's sampling API if available
# 2. Implement custom sampling mechanism
# 3. Document limitation and provide alternative workflow
# 4. Create tool that helps user construct sampling prompts
```

---

### Issue 10: Add OAuth Configuration Validators

**Category**: Configuration  
**Priority**: Medium  
**Effort**: Small (1-2 days)

#### Description
OAuth configuration lacks validation for redirect URI format, HTTPS endpoints, and other security requirements.

#### Goals
- Validate OAuth redirect URI matches pattern
- Ensure OAuth endpoints use HTTPS (except localhost)
- Validate port ranges
- Provide helpful error messages

#### Files to Modify
- `src/mcp_server/config.py` (add validators)
- `tests/test_config.py` (add validation tests)

#### Acceptance Criteria
- [ ] OAuth redirect URI validated
- [ ] OAuth endpoints validated for HTTPS
- [ ] Server port validated (1024-65535)
- [ ] Clear error messages for invalid configuration
- [ ] Tests for all validators
- [ ] Documentation updated

#### Implementation Notes
```python
# src/mcp_server/config.py

from pydantic import field_validator, HttpUrl
from urllib.parse import urlparse

class Settings(BaseSettings):
    # ... existing fields ...
    
    @field_validator("oauth_redirect_uri")
    @classmethod
    def validate_redirect_uri(cls, v: str) -> str:
        """Validate OAuth redirect URI format."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid redirect URI: {v}")
        if parsed.scheme not in ["http", "https"]:
            raise ValueError(f"Redirect URI must use http or https: {v}")
        return v
    
    @field_validator("oauth_authorization_url", "oauth_token_url")
    @classmethod
    def validate_oauth_endpoint(cls, v: str) -> str:
        """Validate OAuth endpoints use HTTPS (except localhost)."""
        parsed = urlparse(v)
        if parsed.hostname != "localhost" and parsed.scheme != "https":
            raise ValueError(f"OAuth endpoints must use HTTPS in production: {v}")
        return v
    
    @field_validator("server_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate server port range."""
        if not 1024 <= v <= 65535:
            raise ValueError(f"Server port must be between 1024 and 65535: {v}")
        return v
```

---

### Issue 11: Implement Metrics and Monitoring

**Category**: Observability  
**Priority**: Medium  
**Effort**: Medium (3-5 days)

#### Description
No metrics collection for request counts, latency, errors, or OAuth operations. Need Prometheus-compatible metrics for monitoring.

#### Goals
- Add request count metrics
- Add latency metrics
- Add error rate metrics
- Add OAuth-specific metrics
- Expose /metrics endpoint

#### Files to Modify
- `src/mcp_server/metrics.py` (create)
- `src/mcp_server/server.py` (add metrics middleware)
- `pyproject.toml` (add prometheus_client dependency)
- `tests/test_metrics.py` (create)

#### Acceptance Criteria
- [ ] Prometheus client library integrated
- [ ] Request count by endpoint
- [ ] Request latency histogram
- [ ] Error count by type
- [ ] OAuth success/failure metrics
- [ ] Active session count
- [ ] /metrics endpoint exposed
- [ ] Tests for metrics collection
- [ ] Grafana dashboard example (optional)

#### Implementation Notes
```python
# src/mcp_server/metrics.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Define metrics
request_count = Counter(
    "mcp_requests_total",
    "Total MCP requests",
    ["method", "endpoint", "status"]
)

request_latency = Histogram(
    "mcp_request_duration_seconds",
    "MCP request latency",
    ["method", "endpoint"]
)

oauth_operations = Counter(
    "oauth_operations_total",
    "OAuth operations",
    ["operation", "status"]
)

active_sessions = Gauge(
    "oauth_active_sessions",
    "Number of active OAuth sessions"
)

# src/mcp_server/server.py

from .metrics import request_count, request_latency, active_sessions

@mcp.custom_route("/metrics", methods=["GET"])
async def metrics(request: Request) -> Response:
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Add middleware to track metrics
@mcp.app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_latency.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

---

### Issue 12: Add API Documentation

**Category**: Documentation  
**Priority**: Medium  
**Effort**: Small (1-2 days)

#### Description
MCP tools and HTTP endpoints lack comprehensive API documentation. Need OpenAPI specification and usage examples.

#### Goals
- Create OpenAPI specification for HTTP endpoints
- Document all MCP tools with examples
- Document all MCP prompts with examples
- Add usage guide

#### Files to Modify
- `docs/api.md` (create)
- `docs/openapi.yaml` (create)
- `README.md` (add API documentation link)

#### Acceptance Criteria
- [ ] OpenAPI 3.0 specification complete
- [ ] All HTTP endpoints documented
- [ ] All MCP tools documented with examples
- [ ] All MCP prompts documented with examples
- [ ] Request/response examples provided
- [ ] Error responses documented
- [ ] Usage guide created

#### Implementation Notes
```yaml
# docs/openapi.yaml

openapi: 3.0.0
info:
  title: MCP OAuth Server API
  version: 0.1.0
  description: OAuth-enabled MCP server for GitHub integration

servers:
  - url: http://localhost:8000
    description: Local development server

paths:
  /oauth/authorize:
    get:
      summary: Initiate OAuth authorization flow
      description: Redirects to GitHub OAuth page with PKCE challenge
      responses:
        '302':
          description: Redirect to GitHub OAuth
          headers:
            Location:
              schema:
                type: string
              description: GitHub OAuth URL
  
  /oauth/callback:
    get:
      summary: OAuth callback endpoint
      description: Handles OAuth callback and exchanges code for token
      parameters:
        - name: code
          in: query
          required: true
          schema:
            type: string
          description: Authorization code from OAuth provider
        - name: state
          in: query
          required: true
          schema:
            type: string
          description: CSRF protection state parameter
      responses:
        '200':
          description: Successful authentication
          content:
            text/html:
              schema:
                type: string
        '400':
          description: Authentication failed

  /.well-known/oauth-authorization-server:
    get:
      summary: OAuth authorization server metadata
      description: RFC 8414 metadata endpoint
      responses:
        '200':
          description: OAuth server metadata
          content:
            application/json:
              schema:
                type: object
```

---

### Issue 13: Add Audit Logging

**Category**: Security/Observability  
**Priority**: Medium  
**Effort**: Small (1-2 days)

#### Description
No audit trail for OAuth operations, API usage, or security events. Need comprehensive audit logging for compliance and security.

#### Goals
- Log all OAuth operations (authorize, callback, token exchange)
- Log API usage per user
- Log security events (failed auth, rate limiting)
- Make audit logs searchable

#### Files to Modify
- `src/mcp_server/audit.py` (create)
- `src/mcp_server/server.py` (add audit logging)
- `tests/test_audit.py` (create)

#### Acceptance Criteria
- [ ] All OAuth operations logged
- [ ] API usage logged with user context
- [ ] Security events logged
- [ ] Audit logs in structured format
- [ ] Audit logs stored separately from application logs
- [ ] Audit log retention policy documented
- [ ] Tests for audit logging

#### Implementation Notes
```python
# src/mcp_server/audit.py

import structlog
from enum import Enum
from typing import Any

class AuditEventType(Enum):
    """Types of audit events."""
    OAUTH_AUTHORIZE = "oauth.authorize"
    OAUTH_CALLBACK = "oauth.callback"
    OAUTH_TOKEN_EXCHANGE = "oauth.token_exchange"
    OAUTH_TOKEN_REFRESH = "oauth.token_refresh"
    API_REQUEST = "api.request"
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    AUTH_FAILURE = "security.auth_failure"

audit_logger = structlog.get_logger("audit")

def log_audit_event(
    event_type: AuditEventType,
    user_id: str | None = None,
    details: dict[str, Any] | None = None
) -> None:
    """Log an audit event."""
    audit_logger.info(
        "audit_event",
        event_type=event_type.value,
        user_id=user_id,
        details=details or {}
    )

# src/mcp_server/server.py

from .audit import log_audit_event, AuditEventType

@mcp.custom_route("/oauth/callback", methods=["GET"])
async def oauth_callback(request: Request) -> HTMLResponse:
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    
    # Log audit event
    log_audit_event(
        AuditEventType.OAUTH_CALLBACK,
        details={"state": state, "has_code": bool(code)}
    )
    
    # ... rest of implementation
```

---

### Issue 14: Improve Error Messages

**Category**: Error Handling  
**Priority**: Medium  
**Effort**: Small (1-2 days)

#### Description
Some error messages are too technical for end users, while others are too vague for debugging. Need consistent, helpful error messages.

#### Goals
- Create error code system
- Separate user-facing and developer messages
- Provide actionable guidance in errors
- Standardize error format

#### Files to Modify
- `src/mcp_server/errors.py` (create)
- `src/mcp_server/server.py` (use error codes)
- `tests/test_errors.py` (create)

#### Acceptance Criteria
- [ ] Error code system implemented
- [ ] User-friendly error messages
- [ ] Developer-friendly debug info
- [ ] Actionable guidance in errors
- [ ] Consistent error format
- [ ] Error code documentation
- [ ] Tests for error scenarios

#### Implementation Notes
```python
# src/mcp_server/errors.py

from enum import Enum
from typing import Any

class ErrorCode(Enum):
    """Standard error codes."""
    AUTH_REQUIRED = "AUTH_001"
    OAUTH_NOT_CONFIGURED = "AUTH_002"
    TOKEN_EXPIRED = "AUTH_003"
    INVALID_STATE = "AUTH_004"
    RATE_LIMIT_EXCEEDED = "RATE_001"
    INVALID_INPUT = "VAL_001"
    API_ERROR = "API_001"

class MCPError(Exception):
    """Base MCP error with code and user message."""
    
    def __init__(
        self,
        code: ErrorCode,
        user_message: str,
        developer_message: str | None = None,
        details: dict[str, Any] | None = None
    ):
        self.code = code
        self.user_message = user_message
        self.developer_message = developer_message or user_message
        self.details = details or {}
        super().__init__(self.developer_message)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "error": {
                "code": self.code.value,
                "message": self.user_message,
                "details": self.details
            }
        }

# Example usage:
raise MCPError(
    code=ErrorCode.AUTH_REQUIRED,
    user_message="Please authenticate to use this feature.",
    developer_message="OAuth token not found in session",
    details={"authorization_url": auth_url}
)
```

---

### Issue 15: Add Integration Tests

**Category**: Testing  
**Priority**: Medium  
**Effort**: Medium (3-5 days)

#### Description
No integration tests for full OAuth flow, end-to-end API requests, or multi-component interactions. Need comprehensive integration testing.

#### Goals
- Test complete OAuth authorization flow
- Test MCP tool execution end-to-end
- Test error scenarios across components
- Test concurrent requests

#### Files to Modify
- `tests/integration/` (create directory)
- `tests/integration/test_oauth_flow.py` (create)
- `tests/integration/test_mcp_tools.py` (create)
- `tests/conftest.py` (add integration fixtures)
- `pyproject.toml` (add integration test markers)

#### Acceptance Criteria
- [ ] Full OAuth flow tested (authorize → callback → API request)
- [ ] MCP tools tested end-to-end
- [ ] Error scenarios tested across components
- [ ] Concurrent request handling tested
- [ ] Integration tests run in CI/CD
- [ ] Integration test documentation
- [ ] All integration tests passing

#### Implementation Notes
```python
# tests/integration/test_oauth_flow.py

import pytest
from httpx import AsyncClient

@pytest.mark.integration
async def test_full_oauth_flow(test_client: AsyncClient):
    """Test complete OAuth authorization flow."""
    
    # 1. Initiate authorization
    response = await test_client.get("/oauth/authorize", follow_redirects=False)
    assert response.status_code == 302
    location = response.headers["location"]
    assert "github.com/login/oauth/authorize" in location
    
    # Extract state from redirect URL
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(location)
    params = parse_qs(parsed.query)
    state = params["state"][0]
    
    # 2. Simulate callback with mock code
    with respx.mock:
        # Mock GitHub token endpoint
        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "test_token",
                    "token_type": "bearer",
                    "scope": "read:user"
                }
            )
        )
        
        callback_response = await test_client.get(
            f"/oauth/callback?code=test_code&state={state}"
        )
        assert callback_response.status_code == 200
        assert "successful" in callback_response.text.lower()
    
    # 3. Test API request with authenticated session
    with respx.mock:
        respx.get("https://api.github.com/user").mock(
            return_value=httpx.Response(
                200,
                json={"login": "testuser", "name": "Test User"}
            )
        )
        
        # This would require session handling in test client
        # ... implementation details
```

---

### Issue 16: Extract OAuth Routes Module

**Category**: Code Organization  
**Priority**: Medium  
**Effort**: Small (1-2 days)

#### Description
OAuth routes in `server.py` make the file quite large (468 lines). Extract to dedicated module for better organization.

#### Goals
- Create separate `oauth_routes.py` module
- Move all OAuth-related routes
- Keep server.py focused on MCP functionality
- Maintain all existing functionality

#### Files to Modify
- `src/mcp_server/oauth_routes.py` (create)
- `src/mcp_server/server.py` (refactor)
- `tests/test_oauth_routes.py` (create/update)

#### Acceptance Criteria
- [ ] OAuth routes extracted to oauth_routes.py
- [ ] server.py reduced in size
- [ ] All tests still passing
- [ ] No functionality broken
- [ ] Clean imports and dependencies
- [ ] Documentation updated

#### Implementation Notes
```python
# src/mcp_server/oauth_routes.py

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse

from .config import settings
from .oauth_handler import OAuthHandler
from .session_manager import SessionManager

def register_oauth_routes(
    app: FastMCP,
    oauth_handler: OAuthHandler,
    session_manager: SessionManager
) -> None:
    """Register OAuth-related routes."""
    
    @app.custom_route("/.well-known/oauth-authorization-server", methods=["GET"])
    async def oauth_metadata(request: Request) -> JSONResponse:
        """RFC 8414 Authorization Server Metadata endpoint."""
        metadata = settings.get_authorization_metadata()
        return JSONResponse(metadata)
    
    @app.custom_route("/oauth/authorize", methods=["GET"])
    async def oauth_authorize(request: Request) -> RedirectResponse:
        """OAuth authorization endpoint."""
        # ... implementation
    
    @app.custom_route("/oauth/callback", methods=["GET"])
    async def oauth_callback(request: Request) -> HTMLResponse:
        """OAuth callback endpoint."""
        # ... implementation

# src/mcp_server/server.py

from .oauth_routes import register_oauth_routes

# After creating mcp instance
register_oauth_routes(mcp, oauth_handler, session_manager)
```

---

## Low Priority Issues

### Issue 17: Add Security Scanning to CI/CD

**Category**: CI/CD  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
CI/CD pipeline lacks security scanning for Python code and Docker containers. Need automated vulnerability detection.

#### Goals
- Add Python security scanning (bandit, safety)
- Add container scanning (Trivy)
- Fail builds on critical vulnerabilities
- Generate security reports

#### Files to Modify
- `.github/workflows/security.yml` (create)
- `.github/workflows/ci.yml` (add security checks)
- `pyproject.toml` (add bandit configuration)

#### Acceptance Criteria
- [ ] Bandit scanning in CI/CD
- [ ] Safety dependency scanning
- [ ] Trivy container scanning
- [ ] Security reports as artifacts
- [ ] Builds fail on critical issues
- [ ] Security badge in README

---

### Issue 18: Implement HTTP Client Connection Pooling

**Category**: Performance  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
New HTTPX client created for each API request. Connection pooling would improve performance.

#### Goals
- Reuse HTTPX client instances
- Configure connection pool settings
- Measure performance improvement
- Document configuration

#### Files to Modify
- `src/mcp_server/api_client.py`
- `src/mcp_server/config.py` (add pool settings)
- `tests/test_api_client.py`

#### Acceptance Criteria
- [ ] Single HTTPX client per APIClient instance
- [ ] Connection pool configured
- [ ] Client properly closed on shutdown
- [ ] Tests updated
- [ ] Performance benchmarks

---

### Issue 19: Add Response Caching

**Category**: Performance  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
GitHub API responses could be cached to reduce API calls and improve response times.

#### Goals
- Cache user info responses
- Cache repository data
- Configurable TTL
- Cache invalidation strategy

#### Files to Modify
- `src/mcp_server/cache.py` (create)
- `src/mcp_server/api_client.py`
- `tests/test_cache.py` (create)

#### Acceptance Criteria
- [ ] Cache implementation with TTL
- [ ] User info cached for 5 minutes
- [ ] Repository data cached for 1 minute
- [ ] Cache-Control headers respected
- [ ] Tests for caching behavior

---

### Issue 20: Enhance Health Check Endpoint

**Category**: Observability  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
Current `/health` endpoint just returns "OK". Should check dependencies and provide detailed status.

#### Goals
- Check OAuth provider availability
- Check GitHub API availability
- Distinguish liveness vs readiness
- Provide detailed status

#### Files to Modify
- `src/mcp_server/server.py`
- `src/mcp_server/health.py` (create)
- `tests/test_health.py` (create)

#### Acceptance Criteria
- [ ] /health/live endpoint (liveness)
- [ ] /health/ready endpoint (readiness)
- [ ] Dependency checks included
- [ ] JSON response with details
- [ ] Tests for health checks

---

### Issue 21: Optimize Docker Image

**Category**: DevOps  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
Docker image could be smaller and more optimized. Consider Alpine base, multi-stage builds, and health checks.

#### Goals
- Reduce image size
- Add health check
- Multi-arch support
- Security hardening

#### Files to Modify
- `Dockerfile`
- `.github/workflows/docker.yml` (create)
- `docker-compose.yml`

#### Acceptance Criteria
- [ ] Image size reduced by >30%
- [ ] Health check in Dockerfile
- [ ] Multi-arch builds (amd64, arm64)
- [ ] Non-root user
- [ ] Security scanning passed

---

### Issue 22: Add Troubleshooting Documentation

**Category**: Documentation  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
Missing troubleshooting guide for common issues. Would help users debug problems independently.

#### Goals
- Common error scenarios
- Debug procedures
- FAQ section
- Log interpretation guide

#### Files to Modify
- `docs/TROUBLESHOOTING.md` (create)
- `README.md` (add link)

#### Acceptance Criteria
- [ ] Common errors documented
- [ ] Debug procedures provided
- [ ] FAQ section created
- [ ] Log examples included

---

### Issue 23: Add Contributing Guide

**Category**: Documentation  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
No CONTRIBUTING.md guide for developers who want to contribute to the project.

#### Goals
- Development setup guide
- Code style guidelines
- PR process
- Testing requirements

#### Files to Modify
- `CONTRIBUTING.md` (create)
- `README.md` (add link)

#### Acceptance Criteria
- [ ] Development setup documented
- [ ] Code style guide included
- [ ] PR guidelines provided
- [ ] Testing requirements clear

---

### Issue 24: Extract HTML Templates

**Category**: Code Organization  
**Priority**: Low  
**Effort**: Small (1-2 days)

#### Description
HTML templates are inline in `server.py`, making the code harder to read. Extract to separate template files.

#### Goals
- Move HTML to template files
- Use Jinja2 for templating
- Improve maintainability
- Support internationalization (future)

#### Files to Modify
- `src/mcp_server/templates/` (create directory)
- `src/mcp_server/templates/oauth_success.html` (create)
- `src/mcp_server/templates/oauth_error.html` (create)
- `src/mcp_server/server.py` (use templates)
- `pyproject.toml` (add jinja2 dependency)

#### Acceptance Criteria
- [ ] All HTML in template files
- [ ] Jinja2 rendering working
- [ ] Templates in templates/ directory
- [ ] Tests updated
- [ ] No functionality broken

---

## Summary

**Total Issues**: 24
- **High Priority**: 5 issues
- **Medium Priority**: 11 issues
- **Low Priority**: 8 issues

**Estimated Total Effort**: 
- High: 12-22 days
- Medium: 15-29 days
- Low: 8-16 days
- **Total: 35-67 days (7-13 weeks with 1 developer)**

See [NEXT_STEPS.md](NEXT_STEPS.md) for phased implementation roadmap.
