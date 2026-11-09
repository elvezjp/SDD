"""Unit tests for Bedrock client."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from spec_ai_writer.llm.bedrock_client import BedrockClient


def _mock_session(mock_get_session, content):
    """Make the aiobotocore session return a client responding with content blocks."""
    body = MagicMock()
    body.read = AsyncMock(return_value=json.dumps({"content": content}).encode())

    client = MagicMock()
    client.invoke_model = AsyncMock(return_value={"body": body})

    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=client)
    context.__aexit__ = AsyncMock(return_value=False)
    mock_get_session.return_value.create_client.return_value = context
    return client


def _request_body(client):
    return json.loads(client.invoke_model.call_args.kwargs["body"])


@pytest.mark.unit
class TestBedrockClient:
    @patch("spec_ai_writer.llm.bedrock_client.aiobotocore.session.get_session")
    async def test_chat_never_sends_temperature(self, mock_get_session):
        client = _mock_session(mock_get_session, [{"type": "text", "text": "ok"}])

        await BedrockClient(temperature=0.7).chat(
            [{"role": "user", "content": "hi"}], temperature=0.3
        )

        body = _request_body(client)
        assert "temperature" not in body
        assert body["anthropic_version"] == "bedrock-2023-05-31"
        assert body["max_tokens"] == 4096

    @patch("spec_ai_writer.llm.bedrock_client.aiobotocore.session.get_session")
    async def test_chat_skips_thinking_blocks(self, mock_get_session):
        _mock_session(
            mock_get_session,
            [
                {"type": "thinking", "thinking": "", "signature": "sig"},
                {"type": "text", "text": "プロジェクトの目的は何ですか？"},
            ],
        )

        response = await BedrockClient().chat([{"role": "user", "content": "hi"}])

        assert response == "プロジェクトの目的は何ですか？"

    @patch("spec_ai_writer.llm.bedrock_client.aiobotocore.session.get_session")
    async def test_chat_passes_system_message_separately(self, mock_get_session):
        client = _mock_session(mock_get_session, [{"type": "text", "text": "ok"}])

        await BedrockClient().chat(
            [
                {"role": "system", "content": "You are an interviewer"},
                {"role": "user", "content": "hi"},
            ]
        )

        body = _request_body(client)
        assert body["system"] == "You are an interviewer"
        assert body["messages"] == [
            {"role": "user", "content": [{"type": "text", "text": "hi"}]}
        ]
