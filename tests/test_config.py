"""Tests for configuration module."""

from mcp_server.config import Settings


def test_settings_initialization() -> None:
    """Test settings can be initialized with environment variables."""
    settings = Settings()
    assert settings.oauth_client_id == "test_client_id"
    assert settings.oauth_client_secret == "test_client_secret"
    assert settings.server_name == "mcp-oauth-server"


def test_oauth_scopes_list() -> None:
    """Test OAuth scopes are parsed correctly."""
    settings = Settings(oauth_scopes="read:user,repo,admin:org")
    scopes = settings.oauth_scopes_list
    assert len(scopes) == 3
    assert "read:user" in scopes
    assert "repo" in scopes
    assert "admin:org" in scopes


def test_oauth_scopes_with_spaces() -> None:
    """Test OAuth scopes are trimmed correctly."""
    settings = Settings(oauth_scopes=" read:user , repo , admin:org ")
    scopes = settings.oauth_scopes_list
    assert len(scopes) == 3
    assert all(s.strip() == s for s in scopes)


def test_is_oauth_configured_true() -> None:
    """Test OAuth configuration check returns True when configured."""
    settings = Settings(oauth_client_id="test_id", oauth_client_secret="test_secret")
    assert settings.is_oauth_configured() is True


def test_is_oauth_configured_false() -> None:
    """Test OAuth configuration check returns False when not configured."""
    settings = Settings(oauth_client_id="", oauth_client_secret="")
    assert settings.is_oauth_configured() is False


def test_settings_defaults() -> None:
    """Test default settings values."""
    settings = Settings(oauth_client_id="test", oauth_client_secret="test")
    assert settings.environment == "test"
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.api_timeout == 30


def test_get_authorization_metadata() -> None:
    """Test authorization metadata generation."""
    settings = Settings(
        oauth_client_id="test_id",
        oauth_client_secret="test_secret",
        oauth_scopes="read:user,repo",
        oauth_issuer="https://github.com",
        oauth_authorization_url="https://github.com/login/oauth/authorize",
        oauth_token_url="https://github.com/login/oauth/access_token",
    )

    metadata = settings.get_authorization_metadata()

    # Check required fields
    assert metadata["issuer"] == "https://github.com"
    assert metadata["authorization_endpoint"] == "https://github.com/login/oauth/authorize"
    assert metadata["token_endpoint"] == "https://github.com/login/oauth/access_token"

    # Check scopes
    assert "scopes_supported" in metadata
    assert "read:user" in metadata["scopes_supported"]
    assert "repo" in metadata["scopes_supported"]

    # Check grant types
    assert "grant_types_supported" in metadata
    assert "authorization_code" in metadata["grant_types_supported"]
    assert "refresh_token" in metadata["grant_types_supported"]

    # Check PKCE support
    assert "code_challenge_methods_supported" in metadata
    assert "S256" in metadata["code_challenge_methods_supported"]

    # Check response types
    assert "response_types_supported" in metadata
    assert "code" in metadata["response_types_supported"]

    # Check token endpoint auth methods
    assert "token_endpoint_auth_methods_supported" in metadata
    assert len(metadata["token_endpoint_auth_methods_supported"]) > 0


def test_get_authorization_metadata_defaults() -> None:
    """Test authorization metadata with default values."""
    settings = Settings(oauth_client_id="test", oauth_client_secret="test")
    metadata = settings.get_authorization_metadata()

    # Should have all required RFC 8414 fields
    assert "issuer" in metadata
    assert "authorization_endpoint" in metadata
    assert "token_endpoint" in metadata
    assert "scopes_supported" in metadata
    assert "response_types_supported" in metadata
    assert "grant_types_supported" in metadata
    assert "code_challenge_methods_supported" in metadata
    assert "token_endpoint_auth_methods_supported" in metadata
