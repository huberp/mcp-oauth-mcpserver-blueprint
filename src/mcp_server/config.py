"""Configuration management for MCP OAuth Server."""


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OAuth Configuration
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_authorization_url: str = "https://github.com/login/oauth/authorize"
    oauth_token_url: str = "https://github.com/login/oauth/access_token"
    oauth_scopes: str = "read:user"

    # API Configuration
    api_base_url: str = "https://api.github.com"
    api_timeout: int = 30

    # Server Configuration
    server_name: str = "mcp-oauth-server"
    server_version: str = "0.1.0"
    log_level: str = "INFO"

    # Development Settings
    environment: str = "development"
    debug: bool = False

    @property
    def oauth_scopes_list(self) -> list[str]:
        """Parse OAuth scopes from comma-separated string."""
        return [s.strip() for s in self.oauth_scopes.split(",") if s.strip()]

    def is_oauth_configured(self) -> bool:
        """Check if OAuth credentials are configured."""
        return bool(self.oauth_client_id and self.oauth_client_secret)


# Global settings instance
settings = Settings()
