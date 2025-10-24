# Combining Dependabot PRs

This document explains how to use the automated workflows for combining Dependabot pull requests into a single PR.

## Overview

Dependabot can create multiple PRs for dependency updates, which can be time-consuming to review and merge individually. The workflows in this repository automate the process of combining these PRs into a single PR, making it easier to manage dependency updates.

## Workflows

### 1. Combine Dependency PRs (`.github/workflows/combine-dependency-prs.yml`)

This workflow combines multiple Dependabot PRs into a single PR.

**Features:**
- Only combines PRs that have passed all CI checks (SUCCESS status)
- Supports filtering by dependency type (python, docker, github-actions)
- Provides detailed logging and error handling
- Groups PRs by type in the combined PR description
- Adds informative comments to source PRs

**Trigger:** Manual (workflow_dispatch)

**Usage:**

1. Go to the "Actions" tab in GitHub
2. Select "Combine Dependency PRs" workflow
3. Click "Run workflow"
4. Configure the following inputs:
   - **Branch Name** (default: `combined-dependency-updates`): Name for the combined branch
   - **Delete Stale Branch** (default: `true`): Whether to delete an existing combined branch
   - **Include Types** (default: `python,docker,github-actions`): Comma-separated list of dependency types to include

**Requirements for PRs to be Combined:**

A PR must meet ALL of the following criteria:
- Has the `dependencies` label (automatically added by Dependabot)
- Has at least one of the requested dependency type labels (`python`, `docker`, or `github-actions`)
- Title starts with `chore(deps)` or `chore:`
- All CI checks have passed (status is SUCCESS)

**Example:**

```bash
# Combine all dependency types
Include Types: python,docker,github-actions

# Combine only Python dependencies
Include Types: python

# Combine only Docker and GitHub Actions dependencies
Include Types: docker,github-actions
```

### 2. Cleanup Combined PRs (`.github/workflows/cleanup-combined-prs.yml`)

This workflow automatically runs when a combined dependency PR is merged and cleans up the source PRs.

**Features:**
- Automatically closes source PRs
- Deletes source PR branches
- Adds informative comments to closed PRs
- Deletes the combined PR branch
- Provides detailed summary of cleanup actions

**Trigger:** Automatic (when a PR with title starting with `chore(deps): Combined dependency updates` is merged to `main` or `develop`)

**What It Does:**

1. Extracts PR numbers from the merged combined PR description
2. Closes each source PR with a comment
3. Deletes each source PR's branch
4. Deletes the combined PR's branch
5. Provides a summary of actions taken

## Workflow Process

### Step-by-Step Example

1. **Dependabot creates PRs**
   - PR #10: Update pytest from 7.4.0 to 7.4.3 (python)
   - PR #11: Update httpx from 0.25.0 to 0.25.2 (python)
   - PR #12: Update Dockerfile base image (docker)

2. **CI checks run on each PR**
   - All tests pass ✅
   - Linting passes ✅
   - Docker build succeeds ✅
   - Status: SUCCESS ✅

3. **Manually trigger "Combine Dependency PRs" workflow**
   - Workflow checks each PR
   - Only PRs with SUCCESS status are included
   - Creates a new branch `combined-dependency-updates`
   - Merges all eligible PRs into the combined branch
   - Creates a new PR with a combined description

4. **Review the combined PR**
   - Review the combined changes
   - CI checks run on the combined PR
   - Verify all tests pass

5. **Merge the combined PR**
   - Once approved and all checks pass, merge the combined PR

6. **Automatic cleanup**
   - "Cleanup Combined PRs" workflow triggers automatically
   - Source PRs (#10, #11, #12) are closed
   - Source branches are deleted
   - Combined branch is deleted

## Best Practices

### When to Use

✅ **Good use cases:**
- Multiple Dependabot PRs waiting for review
- All PRs have passed CI checks
- Updates are minor version bumps or patches
- You want to reduce PR review overhead

❌ **When NOT to use:**
- PRs have failing tests or CI checks
- Major version updates that need individual review
- PRs with merge conflicts
- Security updates that need separate review

### Tips

1. **Run regularly**: Consider running the workflow weekly after Dependabot creates its PRs
2. **Check CI status**: Always verify that the combined PR passes all CI checks before merging
3. **Review changes**: Even though PRs are combined, still review the changes
4. **Start small**: If unsure, start by combining only one dependency type (e.g., only `python`)
5. **Monitor for conflicts**: If PRs have merge conflicts, they will be excluded from the combined PR

### Handling Conflicts

If some PRs cannot be merged due to conflicts:
- They will be listed in the combined PR description under "Merge Conflicts"
- These PRs will remain open and need to be handled separately
- The combined PR will include all PRs that could be merged successfully

## Troubleshooting

### No eligible PRs found

**Problem:** Workflow fails with "No eligible PRs found to combine"

**Solutions:**
- Verify PRs have the `dependencies` label
- Check that PRs have the correct dependency type labels
- Ensure PRs have passed all CI checks (SUCCESS status)
- Verify PR titles start with `chore(deps)` or `chore:`

### Branch already exists

**Problem:** Workflow fails because combined branch already exists

**Solutions:**
- Set "Delete Stale Branch" to `true` when running the workflow
- Manually delete the existing combined branch before running
- Use a different branch name

### PRs not closing automatically

**Problem:** Source PRs don't close after merging combined PR

**Solutions:**
- Verify the combined PR title starts with `chore(deps): Combined dependency updates`
- Check that the cleanup workflow has proper permissions
- Look at the cleanup workflow logs for errors

## Configuration

### Dependabot Labels

The workflows rely on labels set in `.github/dependabot.yml`:

```yaml
# Python dependencies
- package-ecosystem: "pip"
  labels:
    - "dependencies"
    - "python"

# GitHub Actions
- package-ecosystem: "github-actions"
  labels:
    - "dependencies"
    - "github-actions"

# Docker dependencies
- package-ecosystem: "docker"
  labels:
    - "dependencies"
    - "docker"
```

### Workflow Permissions

Both workflows require these permissions:
- `contents: write` - Create/delete branches
- `pull-requests: write` - Create and close PRs
- `issues: write` - Add comments and labels

These are automatically provided by the `GITHUB_TOKEN`.

## Examples

### Example 1: Combine All Python Dependencies

```yaml
Include Types: python
```

This will combine all open Dependabot PRs for Python dependencies that have passed CI checks.

### Example 2: Combine Docker and GitHub Actions

```yaml
Include Types: docker,github-actions
```

This will combine Docker and GitHub Actions dependency updates, but exclude Python dependencies.

### Example 3: Custom Branch Name

```yaml
Branch Name: deps-update-2024-10
Include Types: python,docker,github-actions
```

This creates a combined PR on a custom branch name.

## Security Considerations

- The workflows only combine PRs that have **passed all CI checks**
- Each PR is individually validated before being included
- The combined PR also runs through CI checks before merging
- Source PRs are only closed after the combined PR is successfully merged
- You can always review the combined PR before merging

## References

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Script Action](https://github.com/actions/github-script)

---

*Last Updated: 2024-10-24*
