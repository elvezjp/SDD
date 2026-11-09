"""Unit tests for per-model generation parameters."""

import pytest
from spec_ai_writer.config.settings import Settings
from spec_ai_writer.llm.bedrock_client import BedrockClient
from spec_ai_writer.llm.factory import LLMFactory, _requested_effort
from spec_ai_writer.llm.provider_registry import get_model_config

CLAUDE_ALL = ("low", "medium", "high", "xhigh", "max")
BASIC = ("low", "medium", "high")


@pytest.mark.unit
class TestClaudeParams:
    @pytest.mark.parametrize(
        "provider, model, levels",
        [
            ("claude", "claude-haiku-5-5", CLAUDE_ALL),
            ("claude", "claude-opus-4-8", CLAUDE_ALL),
            ("claude", "claude-sonnet-5", CLAUDE_ALL),
            ("claude", "claude-sonnet-4-6", ("low", "medium", "high", "max")),
            ("claude", "claude-opus-4-5-20251101", BASIC),
            ("claude", "claude-haiku-4-5-20251001", ()),
            ("claude", "claude-sonnet-4-20250514", ()),
            ("claude", "unknown-model", ()),
            ("bedrock", "global.anthropic.claude-haiku-4-5-20251001-v1:0", ()),
            ("bedrock", "anthropic.claude-opus-5-5", CLAUDE_ALL),
        ],
    )
    def test_effort_levels(self, provider, model, levels):
        config = get_model_config(model, provider)
        assert config.effort_levels == levels
        assert config.temperature_supported is False


@pytest.mark.unit
class TestOpenAICompatibleParams:
    @pytest.mark.parametrize(
        "model",
        ["gpt-5.5", "gpt-5.4-2026-03-01", "gpt-5-mini", "o1", "o3-mini", "o4-mini-2025-04-16"],
    )
    def test_reasoning_models_follow_their_family(self, model):
        config = get_model_config(model, "openai")
        assert config.temperature_supported is False
        assert config.max_tokens_param == "max_completion_tokens"
        assert config.effort_levels == BASIC

    @pytest.mark.parametrize("model", ["gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra"])
    def test_gpt6_family(self, model):
        config = get_model_config(model, "openai")
        assert config.temperature_supported is False
        assert config.max_tokens_param == "max_completion_tokens"
        assert config.effort_levels == CLAUDE_ALL

    @pytest.mark.parametrize("model", ["gpt-5.5-pro", "o1-mini"])
    def test_models_without_selectable_effort(self, model):
        config = get_model_config(model, "openai")
        assert config.temperature_supported is False
        assert config.effort_levels == ()

    def test_vendor_prefix_is_ignored_for_family(self):
        config = get_model_config("openai/gpt-5.5", "openrouter")
        assert config.temperature_supported is False
        assert config.effort_levels == ()

    @pytest.mark.parametrize("model", ["gpt-3.5-turbo", "gpt-4.1", "gpt-4o", "gpt-4o-mini"])
    def test_models_listed_as_accepting_temperature(self, model):
        config = get_model_config(model, "openai")
        assert config.temperature_supported is True
        assert config.effort_levels == ()

    @pytest.mark.parametrize(
        "provider, model",
        [
            ("openai", "o1x-experimental"),
            ("openai", "future-model"),
            ("openrouter", "vendor/unknown-model"),
            ("kimi", "kimi-k3"),
        ],
    )
    def test_unknown_models_receive_no_temperature(self, provider, model):
        assert get_model_config(model, provider).temperature_supported is False

    @pytest.mark.parametrize("provider", ["ollama", "lmstudio"])
    def test_local_servers_accept_temperature(self, provider):
        assert get_model_config("gemma4", provider).temperature_supported is True

    def test_fixed_temperature_model(self):
        config = get_model_config("kimi-k2.6", "kimi")
        assert config.temperature_supported is True
        assert config.fixed_temperature == 0.6


@pytest.mark.unit
class TestRequestedEffort:
    @pytest.mark.parametrize(
        "effort, provider, model, expected",
        [
            ("high", "claude", "claude-haiku-5-5", "high"),
            ("auto", "claude", "claude-haiku-5-5", None),
            ("high", "claude", "claude-haiku-4-5-20251001", None),
            ("xhigh", "claude", "claude-sonnet-4-6", None),
            ("max", "openai", "gpt-5.5", None),
            ("low", "openai", "gpt-5.5", "low"),
            ("high", "ollama", "gemma3:4b", None),
        ],
    )
    def test_only_supported_levels_are_sent(self, effort, provider, model, expected):
        settings = Settings(effort=effort)
        assert _requested_effort(settings, provider, model) == expected


@pytest.mark.unit
class TestBedrockCredentials:
    @staticmethod
    def _settings(token="", key="", secret=""):
        return Settings(
            default_llm_provider="bedrock",
            aws_bearer_token_bedrock=token,
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )

    @pytest.mark.parametrize(
        "credentials", [{"token": "test-api-key"}, {"key": "AKIATEST", "secret": "test-secret"}]
    )
    def test_either_credential_is_enough(self, credentials):
        settings = self._settings(**credentials)
        assert isinstance(LLMFactory.create_client(settings=settings), BedrockClient)
        assert settings.validate_llm_config()[0] is True

    @pytest.mark.parametrize("credentials", [{}, {"key": "AKIATEST"}])
    def test_missing_credentials_are_rejected(self, credentials):
        settings = self._settings(**credentials)
        with pytest.raises(ValueError, match="Bedrock API key"):
            LLMFactory.create_client(settings=settings)
        assert settings.validate_llm_config()[0] is False
