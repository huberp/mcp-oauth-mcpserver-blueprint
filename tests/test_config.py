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
