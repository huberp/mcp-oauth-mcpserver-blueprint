# Quick Start Guide - Creating GitHub Issues

This guide helps you quickly create GitHub issues from the code review findings.

## Overview

This code review identified **24 issues** that should be created as GitHub issues for tracking and assignment.

## Using the Shell Script

The repository includes a helper script for creating issues:

```bash
cd code-reviews
./create-review-issues.sh
```

**Note**: The script requires GitHub CLI (`gh`) to be installed and authenticated.

## Manual Issue Creation

If you prefer to create issues manually or the script is not available, use the templates below.

### Quick Reference

| Priority | Count | Issues |
|----------|-------|--------|
| High | 5 | #1, #2, #3, #4, #5 |
| Medium | 11 | #6, #7, #8, #9, #10, #11, #12, #13, #14, #15, #16 |
| Low | 8 | #17, #18, #19, #20, #21, #22, #23, #24 |

## Issue Templates

### High Priority Issues (Create First)

#### Issue #1: Increase Test Coverage to >80%

```markdown
**Title**: Increase Test Coverage to >80%

**Labels**: testing, high-priority, medium-effort

**Description**:
Current test coverage is 58%, with `server.py` at only 30% and `main.py` at 0%. Need comprehensive tests for all modules to reach project target of >80% coverage.

**Goals**:
- Achieve >80% overall test coverage
- Reach 100% coverage on critical modules (server.py, main.py)
- Add tests for all OAuth routes, MCP tools, and prompts
- Cover edge cases and error scenarios

**Files to Modify**:
- `tests/test_server.py` (create)
- `tests/test_main.py` (create)
- `tests/conftest.py` (enhance fixtures)
- `tests/test_api_client.py` (add edge cases)
- `tests/test_oauth_handler.py` (add edge cases)

**Acceptance Criteria**:
- [ ] Overall coverage ≥ 80%
- [ ] server.py coverage ≥ 90%
- [ ] main.py coverage ≥ 80%
- [ ] All OAuth routes tested
- [ ] All MCP tools tested
- [ ] All MCP prompts tested
- [ ] Session cleanup logic tested
- [ ] Error scenarios tested
- [ ] All tests passing with no regressions
- [ ] Coverage report generated in CI/CD

**Estimated Effort**: Medium (3-5 days)
**Priority**: High
**Phase**: 2
```

---

#### Issue #2: Fix All Linting Errors

```markdown
**Title**: Fix All Linting Errors

**Labels**: code-quality, high-priority, small-effort, good-first-issue

**Description**:
Ruff reports 37 linting errors including whitespace issues (19 auto-fixable), unused imports, import sorting, and exception chaining problems.

**Goals**:
- Fix all 37 linting errors
- Ensure code passes `ruff check` without errors
- Maintain consistency with project style guidelines
- Ensure code passes `black --check`

**Files to Modify**:
- `src/mcp_server/config.py` (whitespace)
- `src/mcp_server/main.py` (whitespace)
- `src/mcp_server/server.py` (whitespace, unused import, import order, exception chaining)

**Acceptance Criteria**:
- [ ] All 37 ruff errors fixed
- [ ] `ruff check src/ tests/` passes with no errors
- [ ] `black --check src/ tests/` passes
- [ ] No trailing whitespace in any file
- [ ] All imports properly sorted
- [ ] Exception chaining uses `raise ... from`
- [ ] No unused imports
- [ ] All tests still passing after changes

**Quick Fix**:
```bash
ruff check --fix src/ tests/
# Then manually fix exception chaining and remove unused imports
```

**Estimated Effort**: Small (1-2 days)
**Priority**: High
**Phase**: 1
```

---

#### Issue #3: Implement Persistent Session Storage

```markdown
**Title**: Implement Persistent Session Storage

**Labels**: security, high-priority, medium-effort, infrastructure

**Description**:
OAuth sessions currently stored in in-memory dictionary, which is lost on restart and not suitable for production. This is a security risk and prevents scaling.

**Goals**:
- Replace in-memory session storage with persistent storage
- Support multiple server instances
- Add session expiry and cleanup
- Maintain security (encrypt sensitive data)

**Files to Modify**:
- `src/mcp_server/session_manager.py` (create)
- `src/mcp_server/server.py` (refactor session handling)
- `pyproject.toml` (add redis dependency)
- `.env.example` (add session storage config)
- `docker-compose.yml` (add Redis service)
- `tests/test_session_manager.py` (create)

**Acceptance Criteria**:
- [ ] Session storage abstracted to SessionManager class
- [ ] Redis backend implemented
- [ ] Sessions encrypted with secret key
- [ ] Automatic session expiry (configurable TTL)
- [ ] Background cleanup task implemented
- [ ] Support for multiple server instances
- [ ] Tests for session manager with >90% coverage
- [ ] Documentation updated with Redis setup
- [ ] Migration path from old sessions handled

**Estimated Effort**: Medium (3-5 days)
**Priority**: High
**Phase**: 1
```

---

#### Issue #4: Add Token Expiry Validation and Refresh

```markdown
**Title**: Add Token Expiry Validation and Refresh

**Labels**: security, high-priority, medium-effort, oauth

**Description**:
Access tokens are not validated for expiry, and there's no automatic refresh mechanism. This could lead to API failures and poor user experience.

**Goals**:
- Store token expiry time with access token
- Validate token expiry before API requests
- Automatically refresh expired tokens
- Handle refresh token expiry gracefully

**Files to Modify**:
- `src/mcp_server/oauth_handler.py` (add expiry tracking)
- `src/mcp_server/api_client.py` (add refresh logic)
- `tests/test_oauth_handler.py` (add expiry tests)
- `tests/test_api_client.py` (add refresh tests)

**Acceptance Criteria**:
- [ ] Token expiry time stored with access token
- [ ] `is_token_expired()` method implemented
- [ ] Automatic token refresh before API requests
- [ ] Refresh token rotation handled
- [ ] Graceful handling of refresh token expiry
- [ ] Tests for token expiry validation
- [ ] Tests for automatic refresh
- [ ] Documentation updated with token lifecycle

**Estimated Effort**: Medium (3-5 days)
**Priority**: High
**Phase**: 1
```

---

#### Issue #5: Add Comprehensive Input Validation

```markdown
**Title**: Add Comprehensive Input Validation

**Labels**: security, high-priority, small-effort, validation

**Description**:
Tool parameters lack comprehensive validation. repo_limit should enforce 1-100 range, username should be validated, and other parameters need bounds checking.

**Goals**:
- Add validation for all tool parameters
- Provide clear error messages for invalid inputs
- Use Pydantic models for input validation
- Document valid input ranges

**Files to Modify**:
- `src/mcp_server/server.py` (add validation to tools)
- `src/mcp_server/models.py` (create, add Pydantic models)
- `tests/test_server.py` (add validation tests)

**Acceptance Criteria**:
- [ ] All tool parameters validated
- [ ] repo_limit enforced to 1-100 range
- [ ] max_tokens enforced to 100-2000 range
- [ ] username validated (alphanumeric, hyphens, max 39 chars)
- [ ] Clear error messages for invalid inputs
- [ ] Pydantic models for structured validation
- [ ] Tests for all validation scenarios
- [ ] Documentation updated with valid ranges

**Estimated Effort**: Small (1-2 days)
**Priority**: High
**Phase**: 1
```

---

### Medium Priority Issues

For medium priority issues (#6-#16), use this compact format:

```bash
# Use GitHub CLI to create issues quickly:
gh issue create --title "Implement Structured Logging" \
  --label "observability,medium-priority,medium-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #6"

gh issue create --title "Add Specific Exception Handling" \
  --label "error-handling,medium-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #7"

gh issue create --title "Implement Rate Limiting" \
  --label "security,medium-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #8"

gh issue create --title "Enhance Sampling Tool Implementation" \
  --label "feature,medium-priority,medium-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #9"

gh issue create --title "Add OAuth Configuration Validators" \
  --label "configuration,medium-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #10"

gh issue create --title "Implement Metrics and Monitoring" \
  --label "observability,medium-priority,medium-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #11"

gh issue create --title "Add API Documentation" \
  --label "documentation,medium-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #12"

gh issue create --title "Add Audit Logging" \
  --label "security,observability,medium-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #13"

gh issue create --title "Improve Error Messages" \
  --label "error-handling,medium-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #14"

gh issue create --title "Add Integration Tests" \
  --label "testing,medium-priority,medium-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #15"

gh issue create --title "Extract OAuth Routes Module" \
  --label "refactoring,medium-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #16"
```

---

### Low Priority Issues

For low priority issues (#17-#24), batch create:

```bash
# Low priority issues - create with lower urgency
gh issue create --title "Add Security Scanning to CI/CD" \
  --label "cicd,security,low-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #17"

gh issue create --title "Implement HTTP Client Connection Pooling" \
  --label "performance,low-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #18"

gh issue create --title "Add Response Caching" \
  --label "performance,low-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #19"

gh issue create --title "Enhance Health Check Endpoint" \
  --label "observability,low-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #20"

gh issue create --title "Optimize Docker Image" \
  --label "devops,low-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #21"

gh issue create --title "Add Troubleshooting Documentation" \
  --label "documentation,low-priority,small-effort,good-first-issue" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #22"

gh issue create --title "Add Contributing Guide" \
  --label "documentation,low-priority,small-effort,good-first-issue" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #23"

gh issue create --title "Extract HTML Templates" \
  --label "refactoring,low-priority,small-effort" \
  --body "See code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md Issue #24"
```

---

## Creating a GitHub Project

Organize issues in a GitHub Project for better tracking:

```bash
# Create project
gh project create --title "Code Review Implementation" \
  --body "Implementation of code review findings from 2025-10-26"

# Add issues to project (after creating issues above)
# This requires knowing the issue numbers
gh project item-add <PROJECT_ID> --url https://github.com/<owner>/<repo>/issues/<issue_number>
```

---

## Recommended Labels

Create these labels for better organization:

```bash
# Priority labels
gh label create high-priority --color "d73a4a" --description "High priority issue"
gh label create medium-priority --color "fbca04" --description "Medium priority issue"
gh label create low-priority --color "0e8a16" --description "Low priority issue"

# Effort labels
gh label create small-effort --color "c5def5" --description "1-2 days effort"
gh label create medium-effort --color "5319e7" --description "3-5 days effort"
gh label create large-effort --color "000000" --description "1-2 weeks effort"

# Category labels
gh label create security --color "d73a4a" --description "Security related"
gh label create testing --color "1d76db" --description "Testing related"
gh label create documentation --color "0075ca" --description "Documentation"
gh label create performance --color "fbca04" --description "Performance optimization"
gh label create observability --color "d4c5f9" --description "Logging, metrics, monitoring"
gh label create refactoring --color "ededed" --description "Code refactoring"
gh label create cicd --color "bfd4f2" --description "CI/CD related"
gh label create oauth --color "f9d0c4" --description "OAuth related"
```

---

## Issue Assignment Strategy

### Phase 1 (Week 1)
Assign all high-priority issues to core team:
- #2 (Linting) → Junior developer (good first task)
- #3 (Sessions) → Senior developer (infrastructure)
- #4 (Token Expiry) → Mid-level developer (OAuth experience)
- #5 (Validation) → Junior developer
- #8 (Rate Limiting) → Mid-level developer

### Phase 2 (Week 2)
Focus on testing:
- #1 (Coverage) → QA + developers
- #7 (Exceptions) → Mid-level developer
- #15 (Integration) → Senior developer
- #14 (Error Messages) → Junior developer

### Phase 3-5
Distribute based on skills and availability

---

## Tracking Progress

### GitHub Project Views

Create custom views in your project:

1. **By Phase**
   - Group by: Custom field "Phase"
   - Sort by: Priority

2. **By Priority**
   - Filter: High priority
   - Sort by: Created date

3. **By Effort**
   - Group by: Effort label
   - Filter: Not closed

4. **Current Sprint**
   - Filter: Iteration = Current
   - Sort by: Priority

### Automation

Set up GitHub Actions automation:

```yaml
# .github/workflows/issue-management.yml
name: Issue Management

on:
  issues:
    types: [opened, labeled]

jobs:
  auto-assign:
    runs-on: ubuntu-latest
    steps:
      - name: Assign based on labels
        if: contains(github.event.issue.labels.*.name, 'good-first-issue')
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.addAssignees({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              assignees: ['junior-dev-username']
            });
```

---

## Issue Templates

For consistent issue creation, add to `.github/ISSUE_TEMPLATE/`:

### code-review-issue.md
```markdown
---
name: Code Review Issue
about: Issue from code review
title: '[CODE REVIEW] '
labels: code-review
assignees: ''
---

**From Code Review**: 2025-10-26
**Issue Number**: #
**Priority**: 
**Effort**: 
**Phase**: 

**Description**:


**Goals**:
- 
- 

**Files to Modify**:
- 

**Acceptance Criteria**:
- [ ] 
- [ ] 

**See**: code-reviews/2025-10-26-comprehensive-review/CODE_REVIEW_ISSUES.md for full details
```

---

## Quick Commands Reference

```bash
# List all issues from this review
gh issue list --label "code-review"

# Check status of high-priority issues
gh issue list --label "high-priority" --state all

# Close completed issue
gh issue close <issue-number> --comment "Completed as part of Phase 1"

# Add issue to milestone
gh issue edit <issue-number> --milestone "v0.2.0"

# Update issue
gh issue edit <issue-number> --add-label "in-progress"
```

---

## Next Steps

1. ✅ Review [CODE_REVIEW_ISSUES.md](CODE_REVIEW_ISSUES.md) for full details
2. ✅ Create labels if they don't exist
3. ✅ Create all high-priority issues first (#1-#5)
4. ✅ Create a GitHub Project for tracking
5. ✅ Create medium and low priority issues
6. ✅ Assign issues based on team availability
7. ✅ Start Phase 1 implementation

---

**Document Version**: 1.0  
**Last Updated**: October 26, 2025  
**Total Issues to Create**: 24
