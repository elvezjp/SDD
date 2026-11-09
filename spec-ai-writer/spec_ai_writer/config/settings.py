"""Configuration management for spec-ai-writer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

SettingsSource = Literal["json", "env", "default"]


class Settings(BaseSettings):
    """Application settings.

    Loaded from environment variables / .env first (via pydantic_settings),
    then overlaid with data/settings.json written by the Web UI.
    """

    # --- Active provider ---
    default_llm_provider: str = Field(
        default="claude",
        description="Active LLM provider (claude/openai/openrouter/ollama/lmstudio/kimi/bedrock)",
    )

    # --- Claude ---
    anthropic_api_key: str = Field(
        default="", description="Anthropic API key (ANTHROPIC_API_KEY)"
    )
    claude_model: str = Field(
        default="claude-haiku-4-5-20251001",
        description="Claude model ID (CLAUDE_MODEL)",
    )

    # --- OpenAI ---
    openai_api_key: str = Field(
        default="", description="OpenAI API key (OPENAI_API_KEY)"
    )
    openai_model: str = Field(
        default="gpt-5-mini", description="OpenAI model ID (OPENAI_MODEL)"
    )

    # --- OpenRouter ---
    openrouter_api_key: str = Field(
        default="",
        description="OpenRouter API key (OPENROUTER_API_KEY). Falls back to OPENAI_API_KEY.",
    )
    openrouter_model: str = Field(
        default="nvidia/nemotron-3-ultra-550b-a55b:free",
        description="OpenRouter model ID (OPENROUTER_MODEL). Falls back to OPENAI_MODEL.",
    )

    # --- Ollama ---
    ollama_model: str = Field(
        default="gemma3:4b", description="Ollama model ID (OLLAMA_MODEL)"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Ollama base URL (OLLAMA_BASE_URL)",
    )

    # --- LM Studio ---
    lmstudio_model: str = Field(
        default="google/gemma-3-4b", description="LM Studio model ID (LMSTUDIO_MODEL)"
    )
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="LM Studio base URL (LMSTUDIO_BASE_URL)",
    )

    # --- Kimi ---
    kimi_api_key: str = Field(
        default="", description="Moonshot Kimi API key (KIMI_API_KEY)"
    )
    kimi_model: str = Field(
        default="kimi-k2.6", description="Kimi model ID (KIMI_MODEL)"
    )

    # --- AWS Bedrock ---
    aws_access_key_id: str = Field(default="", description="AWS Access Key ID")
    aws_secret_access_key: str = Field(default="", description="AWS Secret Access Key")
    aws_region: str = Field(default="ap-northeast-1", description="AWS region")
    bedrock_model_id: str = Field(
        default="global.anthropic.claude-haiku-4-5-20251001-v1:0",
        description="Bedrock model ID",
    )

    # --- Common generation params ---
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature"
    )
    effort: Literal["auto", "low", "medium", "high", "xhigh", "max"] = Field(
        default="auto",
        description="Reasoning effort. 'auto' sends nothing and uses the model's default.",
    )

    # --- App config ---
    data_dir: str = Field(default="./data", description="Data directory")
    auto_git_commit: bool = Field(
        default=True, description="Auto-commit generated files"
    )
    app_env: Literal["development", "production"] = Field(
        default="development",
        description="Application environment",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_data_path(self) -> Path:
        return Path(self.data_dir).expanduser().resolve()

    def validate_llm_config(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        p = self.default_llm_provider

        if p == "claude":
            if not self.anthropic_api_key:
                errors.append("ANTHROPIC_API_KEY is required for Claude provider")
        elif p == "openai":
            if not self.openai_api_key:
                errors.append(
                    "OPENAI_API_KEY is required for the official OpenAI endpoint"
                )
        elif p == "openrouter":
            if not (self.openrouter_api_key or self.openai_api_key):
                errors.append(
                    "OPENROUTER_API_KEY (or OPENAI_API_KEY) is required for OpenRouter"
                )
        elif p in ("ollama", "lmstudio"):
            pass  # No API key required
        elif p == "kimi":
            if not self.kimi_api_key:
                errors.append("KIMI_API_KEY is required for Kimi provider")
        elif p == "bedrock":
            if not self.aws_access_key_id or not self.aws_secret_access_key:
                errors.append("AWS credentials are required for Bedrock provider")
        else:
            errors.append(
                f"Unknown LLM provider: {p}. "
                "Supported: claude, openai, openrouter, ollama, lmstudio, kimi, bedrock"
            )

        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Fields writable from the Web UI (applied from settings.json overlay)
# ---------------------------------------------------------------------------

_OVERLAY_FIELDS: frozenset[str] = frozenset(
    {
        "default_llm_provider",
        "temperature",
        "effort",
        # Claude
        "anthropic_api_key",
        "claude_model",
        # OpenAI
        "openai_api_key",
        "openai_model",
        # OpenRouter
        "openrouter_api_key",
        "openrouter_model",
        # Ollama
        "ollama_model",
        "ollama_base_url",
        # LM Studio
        "lmstudio_model",
        "lmstudio_base_url",
        # Kimi
        "kimi_api_key",
        "kimi_model",
        # Bedrock
        "aws_access_key_id",
        "aws_secret_access_key",
        "aws_region",
        "bedrock_model_id",
    }
)


def _nested_to_flat(json_data: dict[str, Any]) -> dict[str, Any]:
    """Translate nested settings.json format to flat Settings field names."""
    flat: dict[str, Any] = {}

    if "active_provider" in json_data:
        flat["default_llm_provider"] = json_data["active_provider"]
    if "temperature" in json_data:
        flat["temperature"] = json_data["temperature"]
    if "effort" in json_data:
        flat["effort"] = json_data["effort"]

    providers = json_data.get("providers", {})

    def _pick(src: dict[str, Any], key: str, dst: str) -> None:
        if key in src:
            flat[dst] = src[key]

    claude = providers.get("claude", {})
    _pick(claude, "api_key", "anthropic_api_key")
    _pick(claude, "model", "claude_model")

    openai = providers.get("openai", {})
    _pick(openai, "api_key", "openai_api_key")
    _pick(openai, "model", "openai_model")

    openrouter = providers.get("openrouter", {})
    _pick(openrouter, "api_key", "openrouter_api_key")
    _pick(openrouter, "model", "openrouter_model")

    ollama = providers.get("ollama", {})
    _pick(ollama, "model", "ollama_model")
    _pick(ollama, "base_url", "ollama_base_url")

    lmstudio = providers.get("lmstudio", {})
    _pick(lmstudio, "model", "lmstudio_model")
    _pick(lmstudio, "base_url", "lmstudio_base_url")

    kimi = providers.get("kimi", {})
    _pick(kimi, "api_key", "kimi_api_key")
    _pick(kimi, "model", "kimi_model")

    bedrock = providers.get("bedrock", {})
    _pick(bedrock, "model", "bedrock_model_id")
    _pick(bedrock, "aws_access_key_id", "aws_access_key_id")
    _pick(bedrock, "aws_secret_access_key", "aws_secret_access_key")
    _pick(bedrock, "aws_region", "aws_region")

    return flat


# ---------------------------------------------------------------------------
# Global settings instance + source tracking
# ---------------------------------------------------------------------------

_settings: Optional[Settings] = None
# Maps flat field name → "json" | "env" | "default"
_sources: dict[str, SettingsSource] = {}


def _compute_sources(
    base: Settings,
    overlay_fields: set[str],
) -> dict[str, SettingsSource]:
    """Build a source map after overlay application.

    Fields changed by the overlay are "json"; fields that differ from the
    pydantic default (i.e. came from env/.env) are "env"; the rest are
    "default".
    """
    sources: dict[str, SettingsSource] = {}
    for name, field_info in type(base).model_fields.items():
        if name in overlay_fields:
            sources[name] = "json"
        else:
            default = field_info.default
            sources[name] = "env" if getattr(base, name) != default else "default"
    return sources


def _apply_overlay(settings: Settings) -> set[str]:
    """Apply data/settings.json onto *settings* in place.

    Returns the set of field names that were actually changed by the overlay.
    Runs migration from legacy llm_settings.json first if needed.
    """
    from spec_ai_writer.config.settings_file import (
        load_settings,
        migrate_legacy_settings,
    )

    migrate_legacy_settings()
    json_data = load_settings()
    if not json_data:
        return set()

    flat = _nested_to_flat(json_data)
    changed: set[str] = set()
    for key, value in flat.items():
        if key not in _OVERLAY_FIELDS:
            logger.debug("Ignoring unknown overlay field: %s", key)
            continue
        try:
            setattr(settings, key, value)
            changed.add(key)
        except Exception as e:
            logger.warning("Failed to apply overlay field %s: %s", key, e)

    return changed


def get_settings() -> Settings:
    """Return the global Settings instance, creating it on first call."""
    global _settings, _sources
    if _settings is None:
        _settings = Settings()
        changed = _apply_overlay(_settings)
        _sources = _compute_sources(_settings, changed)
    return _settings


def reload_settings() -> Settings:
    """Reload from env/dotenv, re-apply overlay, and mutate the existing instance in place.

    Mutates in place so module-level references captured at import time
    (e.g. ``settings = get_settings()`` in routers) see the updated values.
    """
    global _settings, _sources
    fresh = Settings()
    changed = _apply_overlay(fresh)
    _sources = _compute_sources(fresh, changed)

    if _settings is None:
        _settings = fresh
        return _settings

    for field_name in type(fresh).model_fields:
        setattr(_settings, field_name, getattr(fresh, field_name))
    return _settings


def get_settings_sources() -> dict[str, SettingsSource]:
    """Return the source map for the current settings instance."""
    if not _sources:
        get_settings()
    return dict(_sources)
