#!/bin/bash
# Script to create GitHub issues from code review
# This script provides the commands to create all issues identified in the code review
#
# Usage:
#   ./create-review-issues.sh [review-date-directory]
#
# Example:
#   ./create-review-issues.sh 2025-10-26-comprehensive-review
#
# If no directory is specified, it will use the most recent review directory.

set -e

REPO="huberp/mcp-oauth-mcpserver-blueprint"
REVIEW_DIR="${1:-}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# If no review directory specified, find the most recent one
if [ -z "$REVIEW_DIR" ]; then
    REVIEW_DIR=$(ls -t "$SCRIPT_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}-' | head -1)
    if [ -z "$REVIEW_DIR" ]; then
        echo "Error: No review directory found and none specified."
        echo "Usage: $0 [review-date-directory]"
        exit 1
    fi
fi

echo "==================================="
echo "Code Review Issues - Creation Script"
echo "==================================="
echo ""
echo "Repository: $REPO"
echo "Review Directory: $REVIEW_DIR"
echo ""
echo "This script will create GitHub issues from the code review findings."
echo "Make sure you have GH_TOKEN set or are authenticated with gh CLI."
echo ""
echo "To authenticate with gh CLI, run: gh auth login"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Function to create issue
create_issue() {
    local title="$1"
    local body="$2"
    local labels="$3"
    
    echo "Creating issue: $title"
    echo "$body" | gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body-file - \
        --label "$labels"
    echo "✓ Issue created"
    echo ""
}

# Check if CODE_REVIEW_ISSUES.md exists
ISSUES_FILE="$SCRIPT_DIR/$REVIEW_DIR/CODE_REVIEW_ISSUES.md"
if [ ! -f "$ISSUES_FILE" ]; then
    echo "Error: Issues file not found: $ISSUES_FILE"
    echo ""
    echo "Please create the review directory and CODE_REVIEW_ISSUES.md file first."
    exit 1
fi

echo "==================================="
echo "Review Issues File Found"
echo "==================================="
echo ""
echo "Issues are defined in: $ISSUES_FILE"
echo ""
echo "This script template is ready for you to add issue creation commands."
echo "Follow the pattern below to add issues from your CODE_REVIEW_ISSUES.md:"
echo ""
echo "Example:"
echo '  create_issue \'
echo '      "Issue Title" \'
echo '      "## Description'
echo '  Detailed description here'
echo '  '
echo '  ## Goals'
echo '  - Goal 1'
echo '  - Goal 2'
echo '  '
echo '  ## Files to modify'
echo '  - \`src/file.py\`'
echo '  '
echo '  ## Acceptance Criteria'
echo '  - [ ] Criterion 1'
echo '  - [ ] Tests added'
echo '  '
echo '  **Estimated effort**: Medium'
echo '  **Priority**: High" \'
echo '      "enhancement,security,priority-high"'
echo ""
echo "==================================="
echo "Add your issue creation commands below this template"
echo "==================================="
echo ""

# Example issue (commented out)
# Uncomment and modify for actual use
# create_issue \
#     "Enhance error handling in OAuth handler" \
#     "## Description
# The OAuth handler has opportunities for improved error handling:
# 1. Network errors don't provide helpful context
# 2. Missing structured logging for OAuth operations
# 3. Token refresh failures not gracefully handled
# 
# ## Goals
# - Add structured logging for all OAuth operations
# - Improve error messages for token operations
# - Handle network failures gracefully
# 
# ## Files to modify
# - \`src/mcp_server/oauth_handler.py\`
# - Add tests in \`tests/test_oauth_handler.py\`
# 
# ## Acceptance Criteria
# - [ ] All OAuth operations log with context
# - [ ] Network errors handled gracefully
# - [ ] Tests validate error scenarios
# - [ ] No sensitive data in logs
# 
# **Estimated effort**: Medium
# **Priority**: High" \
#     "enhancement,security,priority-high"

echo "==================================="
echo "Script completed"
echo "==================================="
echo ""
echo "To create issues, edit this script and add create_issue calls"
echo "based on the issues in: $ISSUES_FILE"
echo ""
echo "For help, see: $SCRIPT_DIR/$REVIEW_DIR/QUICK_START_ISSUES.md"
