"""Tests for repository analysis tool."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import Context
from fastmcp.server.auth import AccessToken

from mcp_server.server import mcp


async def call_analyze_repository(*args, **kwargs):
    """Helper to call the analyze_repository tool function."""
    # Get the tool function from the FastMCP server
    tools = await mcp.get_tools()
    analyze_tool = tools.get("analyze_repository")
    if analyze_tool is None:
        raise ValueError("analyze_repository tool not found")

    # Call the tool function directly
    return await analyze_tool.fn(*args, **kwargs)


@pytest.fixture
def mock_oauth_token():
    """Create mock OAuth token for testing."""
    return AccessToken(
        token="test_token_12345",
        client_id="test_client_id",
        scopes=["read:user", "repo"],
        expires_at=None,
        claims={
            "login": "testuser",
            "name": "Test User",
            "email": "test@example.com"
        }
    )


@pytest.fixture
def mock_context():
    """Create mock Context for testing."""
    context = MagicMock(spec=Context)
    context.info = AsyncMock()
    context.sample = AsyncMock()

    # Mock the sample response
    sample_response = MagicMock()
    sample_response.text = "This is a test analysis result from the LLM."
    context.sample.return_value = sample_response

    return context


@pytest.fixture
def mock_repo_data():
    """Mock GitHub repository data."""
    return {
        "full_name": "testuser/test-repo",
        "description": "A test repository",
        "language": "Python",
        "stargazers_count": 10,
        "forks_count": 5,
        "topics": ["python", "testing"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.fixture
def mock_languages():
    """Mock GitHub repository languages."""
    return {
        "Python": 1000,
        "JavaScript": 500,
    }


@pytest.mark.asyncio
async def test_analyze_repository_success(
    mock_oauth_token, mock_context, mock_repo_data, mock_languages
):
    """Test successful repository analysis."""
    with patch('mcp_server.server.get_access_token', return_value=mock_oauth_token), \
         patch('mcp_server.server.api_client') as mock_api_client:

        # Setup API client mocks
        mock_api_client.get_repository.return_value = mock_repo_data
        mock_api_client.get_readme.return_value = "# Test Repository\nThis is a test."
        mock_api_client.get_repository_languages.return_value = mock_languages

        # Call the tool
        result = await call_analyze_repository(
            repo_owner="testuser",
            repo_name="test-repo",
            analysis_type="overview",
            ctx=mock_context
        )

        # Verify the result
        result_data = json.loads(result)
        assert result_data["repository"] == "testuser/test-repo"
        assert result_data["analysis_type"] == "overview"
        assert result_data["analysis"] == "This is a test analysis result from the LLM."
        assert "GitHub API" in result_data["data_sources"]

        # Verify API calls were made
        mock_api_client.get_repository.assert_called_once_with(mock_oauth_token, "testuser", "test-repo")
        mock_api_client.get_readme.assert_called_once_with(mock_oauth_token, "testuser", "test-repo")
        mock_api_client.get_repository_languages.assert_called_once_with(mock_oauth_token, "testuser", "test-repo")

        # Verify context calls
        mock_context.info.assert_called()
        mock_context.sample.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_repository_no_auth():
    """Test repository analysis without authentication."""
    with patch('mcp_server.server.get_access_token', return_value=None):
        with pytest.raises(ValueError, match="OAuth authentication required"):
            await call_analyze_repository("owner", "repo", ctx=MagicMock())


@pytest.mark.asyncio
async def test_analyze_repository_no_context(mock_oauth_token):
    """Test repository analysis without context."""
    with patch('mcp_server.server.get_access_token', return_value=mock_oauth_token):
        with pytest.raises(ValueError, match="Context is required for sampling capability"):
            await call_analyze_repository("owner", "repo")


@pytest.mark.asyncio
async def test_analyze_repository_different_types(
    mock_oauth_token, mock_context, mock_repo_data, mock_languages
):
    """Test different analysis types."""
    with patch('mcp_server.server.get_access_token', return_value=mock_oauth_token), \
         patch('mcp_server.server.api_client') as mock_api_client:

        # Setup API client mocks
        mock_api_client.get_repository.return_value = mock_repo_data
        mock_api_client.get_readme.return_value = ""
        mock_api_client.get_repository_languages.return_value = mock_languages

        # Test different analysis types
        for analysis_type in ["tech_stack", "architecture", "security"]:
            result = await call_analyze_repository(
                repo_owner="testuser",
                repo_name="test-repo",
                analysis_type=analysis_type,
                ctx=mock_context
            )

            result_data = json.loads(result)
            assert result_data["analysis_type"] == analysis_type


@pytest.mark.asyncio
async def test_analyze_repository_api_error(mock_oauth_token, mock_context):
    """Test repository analysis with API error."""
    with patch('mcp_server.server.get_access_token', return_value=mock_oauth_token), \
         patch('mcp_server.server.api_client') as mock_api_client:

        # Setup API client to raise an error
        mock_api_client.get_repository.side_effect = Exception("API Error")

        with pytest.raises(ValueError, match="Repository analysis failed: API Error"):
            await call_analyze_repository(
                repo_owner="testuser",
                repo_name="test-repo",
                ctx=mock_context
            )
