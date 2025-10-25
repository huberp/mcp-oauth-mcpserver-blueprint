"""Configuration management for MCP OAuth Server."""

import os
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=os.getenv("SETTINGS_FILE", ".env"),
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

    # OAuth Authorization Server Metadata (RFC 8414)
    oauth_issuer: str = "https://github.com"
    oauth_grant_types_supported: str = "authorization_code,refresh_token"
    oauth_code_challenge_methods_supported: str = "S256"
    oauth_response_types_supported: str = "code"
    oauth_token_endpoint_auth_methods: str = "client_secret_post,client_secret_basic"

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

    def get_authorization_metadata(self) -> dict[str, Any]:
        """
        Get RFC 8414 compliant authorization server metadata.

        This metadata helps MCP clients discover OAuth endpoints and capabilities
        for automated authentication flows.

        Returns:
            Dictionary containing OAuth authorization server metadata
        """
        return {
            "issuer": self.oauth_issuer,
            "authorization_endpoint": self.oauth_authorization_url,
            "token_endpoint": self.oauth_token_url,
            "scopes_supported": self.oauth_scopes_list,
            "response_types_supported": [
                s.strip() for s in self.oauth_response_types_supported.split(",") if s.strip()
            ],
            "grant_types_supported": [
                s.strip() for s in self.oauth_grant_types_supported.split(",") if s.strip()
            ],
            "code_challenge_methods_supported": [
                s.strip()
                for s in self.oauth_code_challenge_methods_supported.split(",")
                if s.strip()
            ],
            "token_endpoint_auth_methods_supported": [
                s.strip()
                for s in self.oauth_token_endpoint_auth_methods.split(",")
                if s.strip()
            ],
        }


# Global settings instance
settings = Settings()
