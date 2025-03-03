# GitHub API Integration Rules

## Overview

This document provides guidelines for connecting to the GitHub API within the Vidst project, including common authentication issues and their solutions.

## Authentication Methods

### 1. GitHub CLI Authentication

The GitHub CLI (`gh`) is the recommended way to interact with GitHub from the command line. It provides a simple interface for common GitHub operations, including issue management, pull requests, and repository operations.

#### Setup Instructions

1. Install the GitHub CLI:

   ```bash
   # macOS
   brew install gh

   # Windows
   winget install --id GitHub.cli

   # Linux
   sudo apt install gh  # Debian/Ubuntu
   ```

2. Authenticate with GitHub:

   ```bash
   gh auth login
   ```

   Follow the prompts to complete authentication.

3. Verify authentication status:

   ```bash
   gh auth status
   ```

### 2. Personal Access Token (PAT)

For direct API calls or when using the GitHub CLI is not possible, you can use a Personal Access Token.

#### Setup Instructions

1. Generate a new token at [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Select the appropriate scopes (typically `repo`, `workflow`, and `read:org`)
3. Store the token securely

## Common Authentication Issues and Solutions

### Issue: "Bad credentials" Error (HTTP 401)

This error occurs when:

- The authentication token is invalid or expired
- The token doesn't have the required permissions
- Environment variables are conflicting with GitHub CLI authentication

#### Solution 1: Check for Environment Variable Conflicts

The GitHub CLI may not work correctly if the `GITHUB_TOKEN` environment variable is set but contains an invalid token.

```bash
# Check if GITHUB_TOKEN is set
echo $GITHUB_TOKEN

# Unset GITHUB_TOKEN if it exists and is causing issues
unset GITHUB_TOKEN
```

#### Solution 2: Switch GitHub Accounts

If you have multiple GitHub accounts configured:

```bash
# List configured accounts
gh auth status

# Switch to a specific account
gh auth switch -u USERNAME
```

#### Solution 3: Re-authenticate

If your token is expired or invalid:

```bash
# Re-authenticate with GitHub
gh auth login
```

### Issue: Permission Denied

This occurs when your token doesn't have the required permissions for the operation.

#### Solution

1. Check the required permissions for the operation
2. Generate a new token with the appropriate scopes
3. Update your authentication

## Working Solution for Vidst Project

The following sequence resolved authentication issues in the Vidst project:

```bash
# 1. Unset any existing GITHUB_TOKEN environment variable
unset GITHUB_TOKEN

# 2. Switch to the appropriate GitHub account
gh auth switch -u admarble

# 3. Verify authentication status
gh auth status

# 4. Now you can use GitHub CLI commands successfully
gh issue comment 118 --repo admarble/Vidst --body-file task7_summary.md
```

## Best Practices

1. **Never hardcode tokens** in your code or commit them to the repository
2. Use environment variables or secure credential storage for tokens
3. Regularly rotate your Personal Access Tokens
4. Use the minimum required permissions for each token
5. Prefer GitHub CLI over direct API calls when possible
6. Always verify authentication status before performing operations

## Troubleshooting Steps

If you encounter authentication issues:

1. Check your authentication status: `gh auth status`
2. Ensure no conflicting environment variables exist
3. Verify your token has the required permissions
4. Try re-authenticating if necessary
5. Check network connectivity to GitHub
6. Consult GitHub's status page for service disruptions

## References

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [Creating Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
