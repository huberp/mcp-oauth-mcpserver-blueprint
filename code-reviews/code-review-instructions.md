# Code Review Instructions

This document provides comprehensive guidelines for conducting in-depth code reviews of the mcp-oauth-mcpserver-blueprint project.

## Purpose

Code reviews serve to:
- Identify areas of improvement across the codebase
- Create actionable tasks for incremental enhancement
- Maintain code quality and security standards
- Track technical debt and improvement opportunities
- Guide development priorities

## Review Process

### 1. Preparation

**Before Starting**:
- Ensure you have a clean clone of the repository
- Run all tests to establish baseline: `pytest`
- Check test coverage: `pytest --cov=src/mcp_server --cov-report=term-missing`
- Review recent commits and change history
- Understand the project's current state and goals

### 2. Comprehensive Analysis

Analyze the following categories:

#### A. Architecture & Code Organization
- Package structure and separation of concerns
- Use of design patterns (dependency injection, composition)
- Module separation (server, handlers, models, API clients)
- Code organization and modularity
- FastMCP framework usage

#### B. Security
- OAuth 2.1 implementation and PKCE
- Token storage and handling
- Input validation and sanitization
- Secrets management (.env, environment variables)
- CORS configuration (if applicable)
- Rate limiting and abuse prevention
- MCP protocol security best practices

#### C. Testing
- Test coverage across all modules
- Test quality (unit, integration, edge cases)
- Test organization and maintainability
- Mock usage and test isolation (respx, pytest-mock)
- Async test handling (pytest-asyncio)
- TDD compliance

#### D. Error Handling & Logging
- Exception propagation and handling
- Structured logging implementation
- Log levels and context
- Error messages (client vs server)
- Request tracing and correlation

#### E. API Design (MCP Protocol)
- MCP specification 2025-06-18 compliance
- Protocol version handling
- Tool and prompt definitions
- Request/response validation
- Error formatting (JSON-RPC)
- OAuth metadata exposure (RFC 8414)
- Resource indicators (RFC 8707)

#### F. Configuration Management
- Environment-based configuration (pydantic-settings)
- Secrets handling
- Default values
- Validation of required fields
- Configuration documentation

#### G. Observability
- Logging best practices
- Health check implementation (if applicable)
- Audit trails for OAuth operations
- Debug/verbose mode support

#### H. CI/CD & DevOps
- GitHub Actions workflow configuration
- Build automation
- Test automation
- Deployment strategy
- Container security (Docker)
- MCP Inspector integration

#### I. Documentation
- Code comments and docstrings (Google-style)
- README completeness
- API documentation (MCP tools/prompts)
- Deployment guides
- Architecture documentation
- OAuth setup guides

#### J. Code Quality
- Python conventions and idioms (PEP 8)
- Code duplication
- Function size and complexity
- Naming conventions
- Type hints completeness (mypy)
- Package dependencies

#### K. Performance
- Algorithm efficiency
- Resource usage
- Async/await patterns
- HTTP client connection pooling
- Token caching strategies

### 3. Issue Creation

For each area of improvement identified:

**Issue Template**:
```markdown
## Description
[Clear description of the issue or improvement needed]

## Goals
- [Specific, measurable goal 1]
- [Specific, measurable goal 2]

## Files to modify
- `path/to/file1.py`
- `path/to/file2.py`

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests added/updated
- [ ] Documentation updated

---
**Estimated Effort**: [Small/Medium/Large]
**Priority**: [High/Medium/Low]
**Category**: [Testing/Security/Enhancement/etc.]
```

**Issue Guidelines**:
1. **Focused**: Each issue addresses one specific improvement
2. **Actionable**: Clear steps and acceptance criteria
3. **Scoped**: Can be completed by a single coding agent
4. **Testable**: Includes verification criteria
5. **Documented**: Explains why and how

### 4. Prioritization

**Priority Levels**:

- **High**: Security vulnerabilities, critical bugs, major quality issues
- **Medium**: Code quality improvements, feature enhancements, moderate technical debt
- **Low**: Nice-to-have improvements, optimizations, cosmetic changes

**Effort Estimation**:

- **Small**: 1-2 days (< 200 lines of code)
- **Medium**: 3-5 days (200-500 lines of code)
- **Large**: 1-2 weeks (> 500 lines of code)

### 5. Documentation

Create the following documents:

1. **README.md**: Navigation guide for the review
2. **CODE_REVIEW_SUMMARY.md**: Detailed findings and analysis
3. **CODE_REVIEW_ISSUES.md**: All issues with full details
4. **NEXT_STEPS.md**: Implementation roadmap
5. **QUICK_START_ISSUES.md**: Quick guide for creating GitHub issues

### 6. Roadmap Creation

Organize issues into implementation phases:

**Phase 1: Security & Critical** (Week 1)
- Close security gaps
- Fix critical bugs
- Address high-priority quality issues

**Phase 2: Testing & Quality** (Week 2)
- Increase test coverage
- Improve test quality
- Fix quality issues

**Phase 3: Code Quality** (Week 3)
- Refactor duplications
- Improve maintainability
- Update documentation

**Phase 4: Observability** (Week 4)
- Enhance monitoring
- Improve logging
- Add metrics (if applicable)

**Phase 5: Features & Enhancements** (Ongoing)
- New features
- Optimizations
- Nice-to-have improvements

## Best Practices

### Do's ✅

- **Be specific**: Provide exact file paths and line numbers where relevant
- **Be constructive**: Focus on improvements, not criticism
- **Be actionable**: Each issue should be implementable
- **Be thorough**: Cover all aspects of the codebase
- **Be objective**: Base findings on standards and best practices
- **Include examples**: Show code samples when helpful
- **Provide context**: Explain why something is an issue

### Don'ts ❌

- **Don't be vague**: Avoid general statements without specifics
- **Don't nitpick**: Focus on meaningful improvements
- **Don't assume**: Verify your findings by running tests
- **Don't ignore strengths**: Acknowledge what's working well
- **Don't create huge issues**: Keep issues focused and scoped
- **Don't skip verification**: Always validate your assessment

## Tools to Use

### Analysis Tools

```bash
# Test coverage
pytest --cov=src/mcp_server --cov-report=term-missing
pytest --cov=src/mcp_server --cov-report=html

# Code statistics
find . -name "*.py" ! -path "./venv/*" ! -path "./.venv/*" | xargs wc -l

# Find TODOs and FIXMEs
grep -r "TODO\|FIXME" --include="*.py" src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/ tests/

# Code formatting check
black --check src/ tests/

# Security scanning (if available)
bandit -r src/
```

### MCP-Specific Tools

```bash
# Test MCP server capabilities
npx @modelcontextprotocol/inspector --cli --method tools/list python3 -m mcp_server.main

# Test prompts
npx @modelcontextprotocol/inspector --cli --method prompts/list python3 -m mcp_server.main

# Test resources (if applicable)
npx @modelcontextprotocol/inspector --cli --method resources/list python3 -m mcp_server.main
```

### Validation

Always validate findings:
1. Run the full test suite
2. Check test coverage reports
3. Review actual code behavior
4. Verify security assumptions
5. Test critical paths manually
6. Validate MCP protocol compliance

## Output Format

### Grading Scale

- **A (Excellent)**: Exceptional quality, minimal improvements needed
- **B+ (Very Good)**: Strong fundamentals, some enhancements recommended
- **B (Good)**: Solid codebase, several improvements needed
- **C (Acceptable)**: Functional but needs significant work
- **D (Poor)**: Major issues, substantial refactoring required

### Summary Structure

```markdown
## Overall Grade: [A/B+/B/C/D]

### Strengths
- [Strength 1]
- [Strength 2]

### Areas for Improvement
- [Area 1]
- [Area 2]

### Metrics
- Files analyzed: X
- Lines of code: Y
- Test coverage: Z%
- Issues identified: N
```

## Review Frequency

- **Major reviews**: Quarterly or before major releases
- **Focused reviews**: After significant features
- **Security reviews**: Before production deployment
- **Ad-hoc reviews**: When requested or after incidents

## Follow-up

After creating issues:
1. Create a GitHub Project or Milestone
2. Assign issues to team members or coding agents
3. Track implementation progress
4. Re-review after significant improvements
5. Update grades and metrics

---

## Example Review Checklist

Use this checklist to ensure comprehensive coverage:

- [ ] All source files analyzed
- [ ] Test coverage measured
- [ ] Security patterns reviewed (OAuth 2.1, PKCE, token handling)
- [ ] Error handling examined
- [ ] MCP protocol compliance verified
- [ ] Configuration reviewed
- [ ] Observability assessed
- [ ] CI/CD pipelines examined
- [ ] Documentation verified
- [ ] Code quality evaluated (type hints, formatting)
- [ ] Performance considerations noted
- [ ] Issues prioritized
- [ ] Roadmap created
- [ ] Documentation complete

---

## Python/MCP-Specific Considerations

### Python Best Practices
- Use of type hints (PEP 484)
- Async/await patterns
- Context managers
- List/dict comprehensions
- Dataclasses or Pydantic models
- Exception hierarchies

### MCP Protocol
- Compliance with MCP spec 2025-06-18 (LATEST)
- Tool registration and schemas
- Prompt templates
- Resource handling
- Sampling support
- OAuth integration as Resource Server

### FastMCP Framework
- Proper use of FastMCP decorators
- Server configuration
- Tool and prompt registration
- Error handling patterns

### OAuth 2.1
- PKCE implementation
- State parameter validation
- Token refresh logic
- Secure token storage
- Authorization code flow

---

**Version**: 1.0  
**Last Updated**: 2025-10-26  
**Maintained by**: Development Team
