"""Factory for creating LLM clients from settings."""

from __future__ import annotations

from typing import Optional

from spec_ai_writer.config.settings import Settings

from .base import BaseLLMClient
from .provider_registry import PROVIDERS, get_model_config


def configured_model(settings: Settings, provider: str) -> str:
    """Return the model ID configured for a provider."""
    return {
        "claude":     settings.claude_model,
        "openai":     settings.openai_model,
        "openrouter": settings.openrouter_model,
        "ollama":     settings.ollama_model,
        "lmstudio":   settings.lmstudio_model,
        "kimi":       settings.kimi_model,
        "bedrock":    settings.bedrock_model_id,
    }[provider]


def _requested_effort(settings: Settings, provider: str, model: str) -> Optional[str]:
    """Return the effort to send, or None for "auto" and levels the model lacks."""
    levels = get_model_config(model, provider).effort_levels
    return settings.effort if settings.effort in levels else None


class LLMFactory:
    """Creates LLM client instances from settings + provider registry."""

    @staticmethod
    def create_client(
        provider: Optional[str] = None,
        settings: Optional[Settings] = None,
    ) -> BaseLLMClient:
        if settings is None:
            from spec_ai_writer.config.settings import get_settings
            settings = get_settings()

        if provider is None:
            provider = settings.default_llm_provider

        provider = provider.lower()

        prov_cfg = PROVIDERS.get(provider)
        if prov_cfg is None:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                f"Supported: {', '.join(PROVIDERS)}"
            )

        if prov_cfg.client_type == "claude":
            return LLMFactory._create_claude_client(settings)
        elif prov_cfg.client_type == "openai_compatible":
            return LLMFactory._create_openai_compatible_client(settings, provider)
        elif prov_cfg.client_type == "bedrock":
            return LLMFactory._create_bedrock_client(settings)

        raise ValueError(f"Unhandled client_type: {prov_cfg.client_type}")  # pragma: no cover

    # ------------------------------------------------------------------
    # Provider-specific builders
    # ------------------------------------------------------------------

    @staticmethod
    def _create_claude_client(settings: Settings) -> BaseLLMClient:
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required for Claude provider. "
                "Set it in .env or via the Settings screen."
            )
        from .claude_client import ClaudeClient
        return ClaudeClient(
            api_key=settings.anthropic_api_key,
            model=settings.claude_model,
            temperature=settings.temperature,
            effort=_requested_effort(settings, "claude", settings.claude_model),
        )

    @staticmethod
    def _create_openai_compatible_client(
        settings: Settings,
        provider: str,
    ) -> BaseLLMClient:
        prov_cfg = PROVIDERS[provider]

        # Resolve api_key from per-provider settings fields.
        key_map: dict[str, str] = {
            "openai":     settings.openai_api_key,
            "openrouter": settings.openrouter_api_key or settings.openai_api_key,
            "ollama":     "",
            "lmstudio":   "",
            "kimi":       settings.kimi_api_key,
        }
        base_url_override_map: dict[str, str] = {
            "ollama":   settings.ollama_base_url,
            "lmstudio": settings.lmstudio_base_url,
        }

        model = configured_model(settings, provider)
        api_key = key_map.get(provider, "")
        base_url_override = base_url_override_map.get(provider, "")

        if not api_key and prov_cfg.api_key_required:
            env_hint = {
                "openai":     "OPENAI_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
                "kimi":       "KIMI_API_KEY",
            }.get(provider, f"{provider.upper()}_API_KEY")
            raise ValueError(
                f"API key is required for {prov_cfg.display_name}. "
                f"Set {env_hint} in .env or via the Settings screen."
            )
        if not api_key:
            api_key = "dummy"  # local servers ignore the key

        effective_base_url = base_url_override or prov_cfg.base_url

        try:
            from .openai_client import OpenAIClient
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

        model_cfg = get_model_config(model, provider)
        return OpenAIClient(
            api_key=api_key,
            model=model,
            temperature=settings.temperature,
            base_url=effective_base_url,
            extra_body=prov_cfg.extra_body,
            max_tokens_param=model_cfg.max_tokens_param,
            temperature_supported=model_cfg.temperature_supported,
            fixed_temperature=model_cfg.fixed_temperature,
            effort=_requested_effort(settings, provider, model),
        )

    @staticmethod
    def _create_bedrock_client(settings: Settings) -> BaseLLMClient:
        has_access_keys = settings.aws_access_key_id and settings.aws_secret_access_key
        if not settings.aws_bearer_token_bedrock and not has_access_keys:
            raise ValueError(
                "A Bedrock API key (AWS_BEARER_TOKEN_BEDROCK) or AWS credentials "
                "(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY) are required for Bedrock. "
                "Set them in .env or via the Settings screen."
            )
        try:
            from .bedrock_client import BedrockClient
        except ImportError:
            raise ImportError(
                "boto3 is required for Bedrock. Install with: pip install boto3"
            )
        return BedrockClient(
            model=settings.bedrock_model_id,
            api_key=settings.aws_bearer_token_bedrock or None,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region=settings.aws_region,
            temperature=settings.temperature,
            effort=_requested_effort(settings, "bedrock", settings.bedrock_model_id),
        )


def create_default_client() -> BaseLLMClient:
    from spec_ai_writer.config.settings import get_settings
    settings = get_settings()
    is_valid, errors = settings.validate_llm_config()
    if not is_valid:
        raise ValueError("Invalid LLM configuration:\n" + "\n".join(f"  - {e}" for e in errors))
    return LLMFactory.create_client(settings=settings)
