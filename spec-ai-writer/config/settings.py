"""Configuration management for spec-ai-writer."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # LLM API Keys
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")

    # AWS Credentials (for Bedrock)
    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")
    aws_region: str = Field(default="ap-northeast-1", description="AWS region")
    bedrock_model_id: str = Field(
        default="global.anthropic.claude-haiku-4-5-20251001-v1:0",
        description="Bedrock model ID (e.g., global.anthropic.claude-haiku-4-5-20251001-v1:0)"
    )

    # spec-ai-writer Settings
    default_llm_provider: str = Field(
        default="claude",
        description="Default LLM provider (claude, openai, bedrock)"
    )
    data_dir: str = Field(
        default="./data",
        description="Data directory for project files"
    )
    auto_git_commit: bool = Field(
        default=True,
        description="Automatically commit generated files to Git"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM temperature for generation"
    )

    # Authentication
    api_key: str = Field(
        default="",
        description="API key for endpoint authentication. If empty, auth is disabled."
    )

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def get_data_path(self) -> Path:
        """Get the data directory as a Path object."""
        return Path(self.data_dir).expanduser().resolve()

    def validate_llm_config(self) -> tuple[bool, list[str]]:
        """
        Validate that the necessary API keys are configured for the selected provider.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if self.default_llm_provider == "claude":
            if not self.anthropic_api_key:
                errors.append("ANTHROPIC_API_KEY is required for Claude provider")
        elif self.default_llm_provider == "openai":
            if not self.openai_api_key:
                errors.append("OPENAI_API_KEY is required for OpenAI provider")
        elif self.default_llm_provider == "bedrock":
            if not self.aws_access_key_id or not self.aws_secret_access_key:
                errors.append("AWS credentials are required for Bedrock provider")
        else:
            errors.append(
                f"Invalid LLM provider: {self.default_llm_provider}. "
                "Must be one of: claude, openai, bedrock"
            )

        return len(errors) == 0, errors


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance, creating it if necessary."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment/config file."""
    global _settings
    _settings = Settings()
    return _settings
