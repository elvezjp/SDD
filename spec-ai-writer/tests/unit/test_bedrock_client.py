"""Unit tests for Bedrock client."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from spec_ai_writer.llm.bedrock_client import BedrockClient
from spec_ai_writer.llm.exceptions import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMResponseError,
)


def _mock_session(mock_get_session, content, **fields):
    """Make the aiobotocore session return a client responding with content blocks."""
    body = MagicMock()
    body.read = AsyncMock(return_value=json.dumps({"content": content, **fields}).encode())

    client = MagicMock()
    client.invoke_model = AsyncMock(return_value={"body": body})

    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=client)
    context.__aexit__ = AsyncMock(return_value=False)
    mock_get_session.return_value.create_client.return_value = context
    return client


def _client_error(code):
    return ClientError({"Error": {"Code": code, "Message": "failed"}}, "InvokeModel")


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

    @pytest.mark.parametrize(
        "effort, expected", [("high", {"effort": "high"}), (None, None)]
    )
    @patch("spec_ai_writer.llm.bedrock_client.aiobotocore.session.get_session")
    async def test_chat_sends_effort_only_when_set(self, mock_get_session, effort, expected):
        client = _mock_session(mock_get_session, [{"type": "text", "text": "ok"}])

        await BedrockClient(effort=effort).chat([{"role": "user", "content": "hi"}])

        assert _request_body(client).get("output_config") == expected

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

    @patch("spec_ai_writer.llm.bedrock_client.aiobotocore.session.get_session")
    async def test_chat_returns_text_and_uses_model_id(self, mock_get_session):
        client = _mock_session(
            mock_get_session,
            [{"type": "text", "text": "前半"}, {"type": "text", "text": "後半"}],
        )

        bedrock = BedrockClient(model="anthropic.test-model-v1:0")
        response = await bedrock.chat([{"role": "user", "content": "hi"}])

        assert response == "前半後半"
        assert client.invoke_model.call_args.kwargs["modelId"] == "anthropic.test-model-v1:0"

    @pytest.mark.parametrize(
        "error, expected",
        [
            (_client_error("AccessDeniedException"), LLMAuthenticationError),
            (_client_error("UnrecognizedClientException"), LLMAuthenticationError),
            (_client_error("ThrottlingException"), LLMResponseError),
            (EndpointConnectionError(endpoint_url="https://example.com"), LLMConnectionError),
            (RuntimeError("unexpected"), LLMResponseError),
        ],
    )
    @patch("spec_ai_writer.llm.bedrock_client.aiobotocore.session.get_session")
    async def test_chat_converts_errors(self, mock_get_session, error, expected):
        client = _mock_session(mock_get_session, [])
        client.invoke_model.side_effect = error

        with pytest.raises(expected):
            await BedrockClient().chat([{"role": "user", "content": "hi"}])

    @pytest.mark.parametrize(
        "content, fields, message",
        [
            ([], {"stop_reason": "refusal", "stop_details": {"category": "cyber"}}, "拒否しました（カテゴリ: cyber）"),
            ([], {"stop_reason": "refusal"}, "拒否しました"),
            ([{"type": "text", "text": "途中まで"}], {"stop_reason": "max_tokens"}, "max_tokens"),
            ([{"type": "thinking", "thinking": ""}], {"stop_reason": "max_tokens"}, "max_tokens"),
            ([], {"stop_reason": "end_turn"}, "応答が空でした"),
            ([{"type": "thinking", "thinking": ""}], {"stop_reason": "end_turn"}, "応答が空でした"),
        ],
    )
    @patch("spec_ai_writer.llm.bedrock_client.aiobotocore.session.get_session")
    async def test_chat_rejects_unusable_responses(self, mock_get_session, content, fields, message):
        _mock_session(mock_get_session, content, **fields)

        with pytest.raises(LLMResponseError, match=message):
            await BedrockClient().chat([{"role": "user", "content": "hi"}])


@pytest.mark.unit
class TestBedrockClientWithRealSdk:
    def test_client_can_be_created(self):
        """Not mocked on purpose: fails when an SDK update breaks client creation."""
        assert BedrockClient(region="us-west-2").model
