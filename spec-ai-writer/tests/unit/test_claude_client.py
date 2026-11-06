"""Unit tests for Claude client."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from spec_ai_writer.llm.claude_client import ClaudeClient, temperature_supported


def _response(*blocks):
    return SimpleNamespace(content=list(blocks))


def _text(text):
    return SimpleNamespace(type="text", text=text)


def _thinking():
    return SimpleNamespace(type="thinking", thinking="", signature="sig")


@pytest.mark.unit
class TestTemperatureSupported:
    @pytest.mark.parametrize(
        "model",
        [
            "claude-haiku-4-5-20251001",
            "claude-haiku-4-5",
            "claude-sonnet-4-6",
            "claude-opus-4-6",
            "claude-sonnet-4-20250514",
            "claude-3-5-haiku-20241022",
        ],
    )
    def test_supported(self, model):
        assert temperature_supported(model) is True

    @pytest.mark.parametrize(
        "model",
        [
            "claude-opus-4-7",
            "claude-opus-4-8",
            "claude-haiku-5-5",
            "claude-sonnet-5-5",
            "claude-opus-5-5",
            "claude-fable-5-1",
            "unknown-model",
        ],
    )
    def test_unsupported(self, model):
        assert temperature_supported(model) is False


@pytest.mark.unit
class TestClaudeClient:
    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_sends_temperature_to_supported_model(self, mock_anthropic):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(return_value=_response(_text("ok")))
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="test-key", model="claude-haiku-4-5-20251001")
        await client.chat([{"role": "user", "content": "hi"}], temperature=0.3)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.3

    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_omits_temperature_for_unsupported_model(self, mock_anthropic):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(return_value=_response(_text("ok")))
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="test-key", model="claude-haiku-5-5")
        await client.chat([{"role": "user", "content": "hi"}], temperature=0.3)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert "temperature" not in call_kwargs
        assert call_kwargs["model"] == "claude-haiku-5-5"
        assert call_kwargs["max_tokens"] == 4096

    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_skips_thinking_blocks(self, mock_anthropic):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(
            return_value=_response(_thinking(), _text("プロジェクトの目的は何ですか？"))
        )
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="test-key", model="claude-haiku-5-5")
        response = await client.chat([{"role": "user", "content": "hi"}])

        assert response == "プロジェクトの目的は何ですか？"

    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_passes_system_message_separately(self, mock_anthropic):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(return_value=_response(_text("ok")))
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="test-key")
        await client.chat(
            [
                {"role": "system", "content": "You are an interviewer"},
                {"role": "user", "content": "hi"},
            ]
        )

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs["system"] == "You are an interviewer"
        assert call_kwargs["messages"] == [{"role": "user", "content": "hi"}]
