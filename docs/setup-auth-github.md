# GitHub OAuth Setup Guide for MCP OAuth Server

This guide walks you through the complete process of setting up GitHub OAuth authentication for the MCP OAuth Server, from creating a GitHub OAuth App to testing the authentication flow in your MCP host.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: GitHub OAuth App Setup](#part-1-github-oauth-app-setup)
3. [Part 2: Server Configuration](#part-2-server-configuration)
4. [Part 3: MCP Host Configuration](#part-3-mcp-host-configuration)
5. [Part 4: Testing the OAuth Flow](#part-4-testing-the-oauth-flow)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)

## Prerequisites

Before you begin, ensure you have:

- A GitHub account (required for creating OAuth Apps)
- Python 3.12 or higher installed
- Docker (optional, for containerized deployment)
- An MCP host application (e.g., Visual Studio Code with MCP extension)
- Basic understanding of OAuth 2.1 and authorization flows

## Part 1: GitHub OAuth App Setup

### Step 1: Navigate to GitHub Developer Settings

1. Log in to your GitHub account
2. Click on your profile picture in the top-right corner
3. Select **Settings** from the dropdown menu
4. Scroll down in the left sidebar and click **Developer settings** (near the bottom)
5. In the left sidebar, click **OAuth Apps**

**Direct URL**: https://github.com/settings/developers

### Step 2: Create a New OAuth App

1. Click the **New OAuth App** button (or **Register a new application** if this is your first app)

2. Fill in the application details:

   **Application name**
   ```
   MCP OAuth Server - Local Development
   ```
   (You can use any name you prefer. This will be shown to users during authorization)

   **Homepage URL**
   ```
   http://localhost:8080
   ```
   (This is the base URL where your server will be running locally)

   **Application description** (Optional)
   ```
   MCP server with OAuth 2.1 authentication for secure GitHub API access
   ```

   **Authorization callback URL** (Critical!)
   ```
   http://localhost:8080/callback
   ```
   ⚠️ **Important**: This URL must match exactly what your server expects. The default configuration uses `http://localhost:8080/callback`.

3. Click **Register application**

### Step 3: Save Your OAuth Credentials

After creating the app, you'll see your OAuth App page with important credentials:

1. **Client ID**: This is automatically generated and visible immediately
   - Example format: `Iv1.a1b2c3d4e5f6g7h8`
   - Copy this value - you'll need it for server configuration

2. **Client Secret**: Click the **Generate a new client secret** button
   - ⚠️ **Critical**: This secret is only shown once! Copy it immediately
   - If you lose it, you'll need to generate a new one
   - Keep this secret secure - never commit it to version control

3. **Save both values** in a secure location (password manager recommended)

### Step 4: Configure OAuth Scopes (Optional but Recommended)

The MCP OAuth Server uses specific GitHub API scopes. While you can't configure these in the GitHub UI (they're requested by the application), you should understand what they mean:

**Default Scopes Used by MCP OAuth Server:**

- `read:user` - Read basic user profile information
  - Includes: username, name, bio, avatar, location, company
  - Does NOT include email address (unless public)

**Additional Scopes You Might Want:**

- `user:email` - Access user's email addresses
- `repo` - Full control of private repositories (if you need to access private repos)
- `public_repo` - Access public repositories only
- `read:org` - Read organization data

To modify scopes, you'll need to update the server configuration (see Part 2).

## Part 2: Server Configuration

### Step 1: Set Up the Project

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/huberp/n-eight-n.git
   cd n-eight-n
   ```

2. **Run the setup script**:

   **Linux/macOS:**
   ```bash
   ./scripts/setup.sh
   ```

   **Windows:**
   ```powershell
   .\scripts\setup.ps1
   ```

   This script will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Copy `.env.example` to `.env`

### Step 2: Configure Environment Variables

1. **Open the `.env` file** in your project root directory:
   ```bash
   nano .env
   # or use your preferred editor: code .env, vim .env, etc.
   ```

2. **Update the OAuth credentials** with values from Part 1:

   ```bash
   # OAuth Configuration
   OAUTH_CLIENT_ID=Iv1.a1b2c3d4e5f6g7h8
   OAUTH_CLIENT_SECRET=your_actual_client_secret_here
   OAUTH_AUTHORIZATION_URL=https://github.com/login/oauth/authorize
   OAUTH_TOKEN_URL=https://github.com/login/oauth/access_token
   OAUTH_SCOPES=read:user
   ```

3. **Customize OAuth scopes** (if needed):

   For basic user info only:
   ```bash
   OAUTH_SCOPES=read:user
   ```

   For user info and email:
   ```bash
   OAUTH_SCOPES=read:user,user:email
   ```

   For user info and repository access:
   ```bash
   OAUTH_SCOPES=read:user,repo
   ```

   ⚠️ **Note**: Multiple scopes are comma-separated, no spaces.

4. **Configure other settings** (optional):

   ```bash
   # API Configuration
   API_BASE_URL=https://api.github.com
   API_TIMEOUT=30

   # Server Configuration
   SERVER_NAME=mcp-oauth-server
   LOG_LEVEL=INFO

   # Development Settings
   ENVIRONMENT=development
   DEBUG=false
   ```

5. **Save and close** the `.env` file

### Step 3: Verify Configuration

Run the configuration validation:

```bash
# Activate virtual environment if not already activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run a quick test
python -c "from mcp_server.config import settings; print(f'OAuth configured: {settings.is_oauth_configured()}')"
```

Expected output:
```
OAuth configured: True
```

If you see `False`, double-check that both `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET` are set correctly in your `.env` file.

### Step 4: Run Tests (Optional but Recommended)

Verify that the server components work correctly:

**Linux/macOS:**
```bash
./scripts/test.sh
```

**Windows:**
```powershell
.\scripts\test.ps1
```

All tests should pass. If any fail, check your configuration.

## Part 3: MCP Host Configuration

### Option A: Docker Deployment (Recommended for Production)

#### Step 1: Build Docker Image

**Linux/macOS:**
```bash
./scripts/build-docker.sh
```

**Windows:**
```powershell
.\scripts\build-docker.ps1
```

This creates a Docker image tagged as `mcp-oauth-server:latest`.

#### Step 2: Configure MCP Host (VS Code)

1. Open your MCP settings file:
   - **VS Code**: Settings → Extensions → MCP → Edit in settings.json
   - Or directly edit: `~/.config/Code/User/settings.json` (Linux/macOS) or `%APPDATA%\Code\User\settings.json` (Windows)

2. Add the MCP server configuration:

   ```json
   {
     "mcp": {
       "servers": {
         "mcp-oauth-server": {
           "command": "docker",
           "args": [
             "run",
             "--rm",
             "--env-file",
             "/absolute/path/to/your/n-eight-n/.env",
             "-i",
             "mcp-oauth-server:latest"
           ],
           "description": "MCP OAuth Server with GitHub authentication"
         }
       }
     }
   }
   ```

   ⚠️ **Important**: Replace `/absolute/path/to/your/n-eight-n/.env` with the actual absolute path to your `.env` file.

#### Step 3: Test Docker Container (Optional)

Before configuring the MCP host, test the container manually:

```bash
docker run --env-file .env -i mcp-oauth-server:latest
```

The server should start without errors. Press `Ctrl+C` to stop.

### Option B: Local Development (Without Docker)

#### Step 1: Ensure Virtual Environment is Active

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

#### Step 2: Configure MCP Host (VS Code)

1. Open your MCP settings file (same as above)

2. Add the MCP server configuration:

   ```json
   {
     "mcp": {
       "servers": {
         "mcp-oauth-server": {
           "command": "/absolute/path/to/venv/bin/python",
           "args": ["-m", "mcp_server.main"],
           "env": {
             "OAUTH_CLIENT_ID": "Iv1.a1b2c3d4e5f6g7h8",
             "OAUTH_CLIENT_SECRET": "your_client_secret_here",
             "OAUTH_AUTHORIZATION_URL": "https://github.com/login/oauth/authorize",
             "OAUTH_TOKEN_URL": "https://github.com/login/oauth/access_token",
             "OAUTH_SCOPES": "read:user",
             "API_BASE_URL": "https://api.github.com",
             "LOG_LEVEL": "INFO"
           },
           "description": "MCP OAuth Server with GitHub authentication"
         }
       }
     }
   }
   ```

   ⚠️ **Important**: 
   - Replace `/absolute/path/to/venv/bin/python` with your actual Python path
   - Find it with: `which python` (Linux/macOS) or `where python` (Windows)
   - Replace OAuth credentials with your actual values

#### Step 3: Test Local Server (Optional)

Test the server manually before connecting from MCP host:

**Linux/macOS:**
```bash
./scripts/run.sh
```

**Windows:**
```powershell
.\scripts\run.ps1
```

The server should start and wait for input (it uses stdio transport). Press `Ctrl+C` to stop.

## Part 4: Testing the OAuth Flow

Now that everything is configured, let's test the complete OAuth authentication flow.

### Step 1: Start Your MCP Host

1. **Restart VS Code** (or your MCP host) to load the new configuration
2. Open the **Command Palette** (Ctrl+Shift+P / Cmd+Shift+P)
3. Verify the MCP server appears in the list of available servers

### Step 2: Trigger OAuth Authentication

There are two ways to trigger authentication:

#### Method 1: Using the Prompt

1. In your MCP host (e.g., Copilot Chat in VS Code), send a message:
   ```
   Use the github_user_summary prompt to analyze my GitHub profile
   ```

2. If not authenticated, the server will respond with OAuth instructions including:
   - Authorization URL
   - State parameter (for CSRF protection)
   - Code verifier (for PKCE)

#### Method 2: Using the Tool Directly

1. In your MCP host, send a message:
   ```
   Use the get_github_user_info tool to fetch my GitHub profile
   ```

2. The server will provide the same OAuth instructions if not authenticated.

### Step 3: Complete OAuth Authorization

When you receive the OAuth instructions:

1. **Copy the authorization URL** from the response
   - It will look like: `https://github.com/login/oauth/authorize?client_id=...`

2. **Open the URL in your web browser**
   - You'll be redirected to GitHub's authorization page

3. **Review the requested permissions**
   - The app will request access to specific scopes (e.g., `read:user`)
   - Verify this is the app you created in Part 1

4. **Click "Authorize [Your App Name]"**
   - If you're not logged in, you'll be prompted to log in first

5. **You'll be redirected to the callback URL**
   - URL format: `http://localhost:8080/callback?code=AUTHORIZATION_CODE&state=STATE_VALUE`
   - ⚠️ **The page will show an error** - this is expected! The server isn't running a web server
   - **What matters is the URL** - you need to copy the `code` parameter

### Step 4: Exchange Authorization Code for Token

The OAuth flow in the current implementation requires manual token exchange (this is for demonstration purposes).

1. **Copy the authorization code** from the callback URL
   - Look for `?code=...` in the URL
   - Example: `gho_16C7e42F292c6912E7710c838347Ae178B4a`

2. **Also save the code_verifier and state** from step 2
   - These were provided in the OAuth instructions

3. **Use the code to authenticate** (implementation-specific):
   - In a production setup, this would be automated
   - For now, you would need to call the `exchange_code_for_token` method programmatically

### Step 5: Verify Authentication

Once authenticated (either manually or through an automated callback handler):

1. **Retry your original request**:
   ```
   Use the get_github_user_info tool to fetch my GitHub profile
   ```

2. **Expected response**: JSON data with your GitHub profile
   ```json
   {
     "login": "your-username",
     "name": "Your Name",
     "bio": "Your bio",
     "public_repos": 42,
     "followers": 123,
     "following": 45,
     "repositories": [
       {
         "name": "repo-name",
         "description": "Repo description",
         "language": "Python",
         "stars": 10,
         "forks": 2
       }
     ]
   }
   ```

3. **Success!** You've completed the OAuth flow 🎉

## Troubleshooting

### Problem: "OAuth is not configured" Error

**Symptoms**: Server responds with error about missing OAuth configuration

**Solutions**:
1. Verify `.env` file exists and contains correct credentials
2. Check that environment variables are loaded:
   ```bash
   python -c "from mcp_server.config import settings; print(settings.oauth_client_id)"
   ```
3. Restart your MCP host after changing `.env`
4. For Docker, ensure `--env-file` path is absolute and correct

### Problem: "Invalid client_id" During Authorization

**Symptoms**: GitHub shows error page during authorization step

**Solutions**:
1. Verify Client ID matches exactly (no extra spaces)
2. Check that OAuth App is active in GitHub settings
3. Ensure you're using the correct GitHub account

### Problem: Callback URL Mismatch

**Symptoms**: "The redirect_uri MUST match the registered callback URL"

**Solutions**:
1. Check GitHub OAuth App settings: callback URL should be `http://localhost:8080/callback`
2. Verify no typos in the callback URL
3. Ensure you're using `http://` not `https://` for local development
4. Check that port 8080 is not in use by another service

### Problem: Token Exchange Fails

**Symptoms**: Error during token exchange with authorization code

**Solutions**:
1. Verify code_verifier matches the one generated with code_challenge
2. Check that authorization code hasn't expired (they're single-use and time-limited)
3. Ensure Client Secret is correct and hasn't been regenerated
4. Verify redirect_uri used in exchange matches the one in authorization

### Problem: "Insufficient Scopes" Error

**Symptoms**: API calls fail with 403 or scope-related errors

**Solutions**:
1. Check requested scopes in `.env` file (`OAUTH_SCOPES`)
2. Verify scopes match what your tools need
3. Re-authorize the application if scopes changed
4. GitHub scope format: `read:user,repo` (comma-separated, no spaces)

### Problem: Server Won't Start

**Symptoms**: MCP host shows connection error or timeout

**Solutions**:
1. Test server manually: `./scripts/run.sh` (should start without errors)
2. Check Python version: `python --version` (must be 3.12+)
3. Verify all dependencies installed: `pip list | grep -E 'fastmcp|authlib|httpx'`
4. Check logs in MCP host for detailed error messages
5. For Docker: verify image was built successfully: `docker images | grep mcp-oauth-server`

### Problem: Rate Limiting

**Symptoms**: "API rate limit exceeded" errors from GitHub

**Solutions**:
1. Authenticated requests have higher limits (5,000/hour vs 60/hour)
2. Wait for rate limit to reset (shown in error response)
3. Implement caching for frequently accessed data
4. Check rate limit status:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.github.com/rate_limit
   ```

### Getting Additional Help

If you're still experiencing issues:

1. **Check server logs** for detailed error messages
   - Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging
   - For Docker: `docker logs <container-id>`

2. **Verify OAuth flow manually** using curl:
   ```bash
   # Test authorization endpoint
   curl "https://github.com/login/oauth/authorize?client_id=YOUR_CLIENT_ID&scope=read:user"
   
   # Test token endpoint
   curl -X POST https://github.com/login/oauth/access_token \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "code=YOUR_AUTH_CODE" \
     -H "Accept: application/json"
   ```

3. **Review GitHub OAuth documentation**:
   - https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps

4. **Open an issue** on the project repository with:
   - Your environment (OS, Python version, Docker version)
   - Sanitized logs (remove secrets!)
   - Steps to reproduce the issue

## Security Best Practices

### Protecting Your Credentials

1. **Never commit credentials to version control**
   - `.env` should be in `.gitignore`
   - Use `.env.example` as a template without real credentials
   - Never share `.env` file publicly

2. **Use environment-specific credentials**
   - Development: Use a separate OAuth App
   - Production: Use different credentials with restricted scopes
   - Testing: Consider using separate test accounts

3. **Rotate secrets regularly**
   - Generate new Client Secret periodically
   - Revoke old secrets after updating
   - Update `.env` and restart services

### OAuth Security

1. **Always use PKCE** (Proof Key for Code Exchange)
   - Prevents authorization code interception
   - Already implemented in this server
   - Required for OAuth 2.1

2. **Validate state parameter**
   - Prevents CSRF attacks
   - Check state in callback matches original
   - Already implemented in this server

3. **Use HTTPS in production**
   - `http://localhost` is OK for development
   - Production must use `https://` for callback URLs
   - Update GitHub OAuth App settings accordingly

4. **Limit OAuth scopes**
   - Request only the minimum required scopes
   - Review scope requirements regularly
   - Users can see and revoke access anytime

### Token Management

1. **Store tokens securely**
   - Never log tokens
   - Don't store in plain text files
   - Consider encrypted storage for production
   - Implement token persistence carefully

2. **Implement token refresh**
   - Access tokens expire
   - Use refresh tokens to get new access tokens
   - Handle token expiration gracefully
   - Already implemented via `refresh_access_token()`

3. **Revoke tokens when done**
   - Allow users to disconnect
   - Revoke tokens on logout
   - GitHub users can revoke at: https://github.com/settings/applications

### Application Security

1. **Keep dependencies updated**
   - Regularly run `pip list --outdated`
   - Update security-critical libraries promptly
   - Monitor security advisories

2. **Input validation**
   - Validate all user inputs
   - Sanitize data before API calls
   - Check API response formats

3. **Error handling**
   - Don't expose sensitive info in errors
   - Log errors securely (no credentials)
   - Provide user-friendly error messages

4. **Rate limiting**
   - Implement request throttling
   - Cache frequently accessed data
   - Respect GitHub API rate limits

## Advanced Configuration

### Using Custom Callback URLs

If you need to use a different callback URL (e.g., different port or hostname):

1. **Update GitHub OAuth App**:
   - Go to https://github.com/settings/developers
   - Edit your OAuth App
   - Change "Authorization callback URL" to your desired URL

2. **Update server configuration**:
   - Modify `oauth_handler.py` if needed
   - Update the `redirect_uri` parameter in `get_authorization_url()` and `exchange_code_for_token()`

3. **Update environment variables** (if using custom domain):
   ```bash
   # Add to .env if you implement custom callback handling
   OAUTH_CALLBACK_URL=http://yourdomain.com:8080/callback
   ```

### Implementing Automated Callback Handler

For production use, you'll want to automate the callback handling:

1. **Add a web server** to handle OAuth callbacks
2. **Implement the `/callback` endpoint** to:
   - Receive authorization code
   - Validate state parameter
   - Exchange code for token automatically
   - Store token securely
   - Return success page to user

3. **Example implementation** (conceptual):
   ```python
   from fastapi import FastAPI, Request
   
   app = FastAPI()
   
   @app.get("/callback")
   async def oauth_callback(code: str, state: str):
       # Validate state
       # Exchange code for token
       # Store token
       return {"message": "Authentication successful!"}
   ```

### Multiple OAuth Providers

To support multiple OAuth providers (GitHub, Google, etc.):

1. **Create separate OAuth handlers** for each provider
2. **Configure multiple OAuth Apps** with respective providers
3. **Update environment variables** with provider-specific credentials
4. **Modify server.py** to handle provider selection

## Next Steps

Now that you have GitHub OAuth authentication working:

1. **Explore available tools and prompts**:
   - `github_user_summary` - Analyze GitHub profiles
   - `get_github_user_info` - Fetch user data and repositories

2. **Customize scopes** for your use case:
   - Add `user:email` to access email addresses
   - Add `repo` for private repository access
   - Add `read:org` for organization data

3. **Build new tools** using the authenticated API client:
   - Check `src/mcp_server/api_client.py` for examples
   - Follow the pattern for new GitHub API endpoints
   - Register tools in `src/mcp_server/server.py`

4. **Deploy to production**:
   - Use HTTPS callback URLs
   - Implement automated callback handling
   - Set up token persistence
   - Configure monitoring and logging

5. **Contribute back**:
   - Report issues or bugs
   - Suggest improvements
   - Share your custom tools
   - Submit pull requests

## References

### Documentation

- **MCP Specification**: https://modelcontextprotocol.io/
- **OAuth 2.1**: https://oauth.net/2.1/
- **PKCE (RFC 7636)**: https://tools.ietf.org/html/rfc7636
- **Resource Indicators (RFC 8707)**: https://tools.ietf.org/html/rfc8707
- **GitHub OAuth**: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps

### GitHub Resources

- **Create OAuth App**: https://github.com/settings/developers
- **OAuth Scopes**: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
- **API Documentation**: https://docs.github.com/en/rest
- **Rate Limits**: https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api
- **Authorized Applications**: https://github.com/settings/applications (view/revoke access)

### Project Resources

- **Repository**: https://github.com/huberp/n-eight-n
- **Issues**: https://github.com/huberp/n-eight-n/issues
- **Main README**: See `README.md` in project root
- **Implementation Details**: See `docs/RESEARCH.md`

---

**Last Updated**: 2025-10-23  
**Version**: 1.0.0  
**Author**: MCP OAuth Server Team

For questions or issues with this guide, please open an issue on GitHub.
