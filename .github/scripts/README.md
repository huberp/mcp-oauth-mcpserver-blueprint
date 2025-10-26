# GitHub Actions Scripts

This directory contains Python scripts used by GitHub Actions workflows.

## create-issues.py

Parses `code-reviews/*/CODE_REVIEW_ISSUES.md` files and creates GitHub issues.

### Usage

The script is designed to be run by the `create-code-review-issues.yml` workflow, but can also be run manually:

```bash
# Dry run (preview mode)
DRY_RUN=true START_ISSUE=1 END_ISSUE=5 python3 .github/scripts/create-issues.py

# Create issues for real
DRY_RUN=false START_ISSUE=1 END_ISSUE=24 GITHUB_TOKEN=<token> GITHUB_REPOSITORY=owner/repo python3 .github/scripts/create-issues.py
```

### Environment Variables

- `DRY_RUN`: Set to `true` to preview without creating issues (default: `true`)
- `START_ISSUE`: First issue number to process (default: `1`)
- `END_ISSUE`: Last issue number to process (default: `24`)
- `GITHUB_TOKEN`: GitHub API token (required when not in dry-run mode)
- `GITHUB_REPOSITORY`: Repository in format `owner/repo` (required when not in dry-run mode)

### Features

- Parses CODE_REVIEW_ISSUES.md format with Category, Priority, Effort fields
- Auto-generates labels based on category and priority
- Creates labels with appropriate colors if they don't exist
- Supports batch creation with configurable ranges
- Dry-run mode for safe testing

### Dependencies

- `PyGithub`: For GitHub API interaction

```bash
pip install PyGithub
```
