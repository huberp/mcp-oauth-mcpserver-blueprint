"""Pytest configuration and fixtures."""

import os
from typing import Any

import pytest

# Set test environment variables before importing settings
os.environ["OAUTH_CLIENT_ID"] = "test_client_id"
os.environ["OAUTH_CLIENT_SECRET"] = "test_client_secret"
os.environ["OAUTH_AUTHORIZATION_URL"] = "https://test.example.com/oauth/authorize"
os.environ["OAUTH_TOKEN_URL"] = "https://test.example.com/oauth/token"
os.environ["API_BASE_URL"] = "https://api.test.example.com"
os.environ["ENVIRONMENT"] = "test"


@pytest.fixture
def mock_oauth_config() -> dict[str, str]:
    """Provide mock OAuth configuration."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "authorization_url": "https://test.example.com/oauth/authorize",
        "token_url": "https://test.example.com/oauth/token",
        "scopes": ["read:user", "repo"],
    }


@pytest.fixture
def mock_user_data() -> dict[str, Any]:
    """Provide mock GitHub user data."""
    return {
        "login": "testuser",
        "name": "Test User",
        "bio": "A test user",
        "public_repos": 42,
        "followers": 100,
        "following": 50,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_repo_data() -> list[dict[str, Any]]:
    """Provide mock GitHub repository data."""
    return [
        {
            "name": "test-repo-1",
            "description": "First test repository",
            "language": "Python",
            "stargazers_count": 10,
            "forks_count": 5,
            "updated_at": "2024-01-01T00:00:00Z",
            "html_url": "https://github.com/testuser/test-repo-1",
        },
        {
            "name": "test-repo-2",
            "description": "Second test repository",
            "language": "JavaScript",
            "stargazers_count": 20,
            "forks_count": 8,
            "updated_at": "2024-01-02T00:00:00Z",
            "html_url": "https://github.com/testuser/test-repo-2",
        },
    ]


@pytest.fixture
def mock_token_response() -> dict[str, Any]:
    """Provide mock OAuth token response."""
    return {
        "access_token": "test_access_token_12345",
        "token_type": "bearer",
        "scope": "read:user repo",
        "refresh_token": "test_refresh_token_67890",
    }
