"""Unit tests for Claude client."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from spec_ai_writer.llm.claude_client import ClaudeClient


def _response(*blocks):
    return SimpleNamespace(content=list(blocks))


def _text(text):
    return SimpleNamespace(type="text", text=text)


def _thinking():
    return SimpleNamespace(type="thinking", thinking="", signature="sig")


@pytest.mark.unit
class TestClaudeClient:
    @pytest.mark.parametrize(
        "model",
        ["claude-haiku-4-5-20251001", "claude-sonnet-4-6", "claude-haiku-5-5", "claude-opus-5-5"],
    )
    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_never_sends_temperature(self, mock_anthropic, model):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(return_value=_response(_text("ok")))
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="test-key", model=model, temperature=0.7)
        await client.chat([{"role": "user", "content": "hi"}], temperature=0.3)

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert "temperature" not in call_kwargs
        assert call_kwargs["model"] == model
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
