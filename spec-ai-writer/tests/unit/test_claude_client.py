"""Unit tests for Claude client."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from anthropic import APIConnectionError, APITimeoutError, AsyncAnthropic, AuthenticationError
from spec_ai_writer.llm.claude_client import ClaudeClient
from spec_ai_writer.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMResponseError,
)


def _response(*blocks, stop_reason="end_turn", stop_details=None):
    return SimpleNamespace(content=list(blocks), stop_reason=stop_reason, stop_details=stop_details)


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

    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_returns_text(self, mock_anthropic):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(
            return_value=_response(_text("前半"), _text("後半"))
        )
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="test-key")
        assert await client.chat([{"role": "user", "content": "hi"}]) == "前半後半"

    @pytest.mark.parametrize(
        "sdk_error, expected",
        [
            (
                AuthenticationError(
                    "invalid", response=Mock(status_code=401, headers={}), body=None
                ),
                LLMAuthenticationError,
            ),
            (APIConnectionError(message="down", request=Mock()), LLMConnectionError),
            (APITimeoutError(request=Mock()), LLMConnectionError),
            (RuntimeError("unexpected"), LLMResponseError),
        ],
    )
    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_converts_errors(self, mock_anthropic, sdk_error, expected):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(side_effect=sdk_error)
        mock_anthropic.return_value = mock_client

        with pytest.raises(expected):
            await ClaudeClient(api_key="test-key").chat([{"role": "user", "content": "hi"}])

    @pytest.mark.parametrize(
        "response, message",
        [
            (
                _response(
                    stop_reason="refusal",
                    stop_details=SimpleNamespace(category="cyber", explanation="declined"),
                ),
                "拒否しました（カテゴリ: cyber）",
            ),
            (_response(stop_reason="refusal"), "拒否しました"),
            (_response(_text("途中まで"), stop_reason="max_tokens"), "max_tokens"),
            (_response(_thinking(), stop_reason="max_tokens"), "max_tokens"),
            (_response(), "応答が空でした"),
            (_response(_thinking()), "応答が空でした"),
            (_response(_text("  ")), "応答が空でした"),
        ],
    )
    @patch("spec_ai_writer.llm.claude_client.AsyncAnthropic")
    async def test_chat_rejects_unusable_responses(self, mock_anthropic, response, message):
        mock_client = Mock()
        mock_client.messages.create = AsyncMock(return_value=response)
        mock_anthropic.return_value = mock_client

        with pytest.raises(LLMResponseError, match=message):
            await ClaudeClient(api_key="test-key").chat([{"role": "user", "content": "hi"}])


@pytest.mark.unit
class TestClaudeClientWithRealSdk:
    def test_client_can_be_created(self):
        """Not mocked on purpose: fails when an SDK update breaks client creation."""
        client = ClaudeClient(api_key="test-key")
        assert isinstance(client.client, AsyncAnthropic)

    def test_client_uses_current_api_version(self):
        client = ClaudeClient(api_key="test-key")
        assert client.client.default_headers["anthropic-version"] == "2026-10-21"
