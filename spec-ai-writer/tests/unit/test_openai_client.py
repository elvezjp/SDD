"""Unit tests for OpenAI client."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from openai import AsyncOpenAI
from spec_ai_writer.llm.openai_client import GPT4_TURBO, GPT35_TURBO, OpenAIClient


@pytest.mark.unit
class TestOpenAIClient:
    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    def test_initialization(self, mock_openai):
        client = OpenAIClient(api_key="test-key", model=GPT4_TURBO, temperature=0.7)
        assert client.model == GPT4_TURBO
        assert client.temperature == 0.7
        assert client.max_tokens == 16000

    def test_initialization_without_api_key(self):
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIClient(api_key="")

    @patch("spec_ai_writer.llm.openai_client.OPENAI_AVAILABLE", False)
    def test_initialization_without_openai_package(self):
        with pytest.raises(ImportError, match="openai package is required"):
            OpenAIClient(api_key="test-key")

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_chat(self, mock_openai):
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "これはテスト応答です。"
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "こんにちは"},
        ]
        response = await client.chat(messages)

        assert response == "これはテスト応答です。"
        mock_client.chat.completions.create.assert_called_once()

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_chat_with_custom_temperature(self, mock_openai):
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Response"
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test-key", temperature_supported=True)
        await client.chat([{"role": "user", "content": "Test"}], temperature=0.5)

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_chat_empty_response(self, mock_openai):
        mock_response = Mock()
        mock_response.choices = []

        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        assert await client.chat([{"role": "user", "content": "Test"}]) == ""

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_chat_api_error(self, mock_openai):
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        mock_openai.return_value = mock_client

        from spec_ai_writer.llm.exceptions import LLMResponseError

        with pytest.raises(LLMResponseError, match="OpenAI API call failed"):
            await OpenAIClient(api_key="test-key").chat(
                [{"role": "user", "content": "Test"}]
            )

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    def test_base_url_passed_to_sdk(self, mock_openai):
        OpenAIClient(
            api_key="test-key", model="gemma3:4b", base_url="http://localhost:11434/v1"
        )
        call_kwargs = mock_openai.call_args.kwargs
        assert call_kwargs["base_url"] == "http://localhost:11434/v1"
        assert call_kwargs["api_key"] == "test-key"

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    def test_no_base_url_omits_kwarg(self, mock_openai):
        OpenAIClient(api_key="test-key")
        assert "base_url" not in mock_openai.call_args.kwargs

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_extra_body_passed_to_api(self, mock_openai):
        """extra_body should be forwarded to the completions.create call."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "ok"
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        extra = {"thinking": {"type": "disabled"}}
        client = OpenAIClient(api_key="test-key", extra_body=extra)
        await client.chat([{"role": "user", "content": "hi"}])

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["extra_body"] == extra

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_max_tokens_param_override(self, mock_openai):
        """max_tokens_param='max_completion_tokens' should be used for o-series models."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "ok"
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        client = OpenAIClient(
            api_key="test-key",
            model="o3",
            max_tokens_param="max_completion_tokens",
            temperature_supported=False,
        )
        await client.chat([{"role": "user", "content": "hi"}])

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert "max_completion_tokens" in call_kwargs
        assert "max_tokens" not in call_kwargs
        assert "temperature" not in call_kwargs

    @pytest.mark.parametrize("effort, expected", [("high", "high"), (None, None)])
    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_chat_sends_effort_only_when_set(self, mock_openai, effort, expected):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "ok"
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        await OpenAIClient(api_key="test-key", effort=effort).chat(
            [{"role": "user", "content": "hi"}]
        )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs.get("reasoning_effort") == expected

    def test_model_constants(self):
        assert GPT4_TURBO == "gpt-4-turbo-preview"
        assert GPT35_TURBO == "gpt-3.5-turbo"

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_generate_question(self, mock_openai):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "プロジェクトの目的は何ですか？"
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        question = await client.generate_question(
            system_prompt="You are an interviewer",
            context={"conversation_history": "", "missing_fields": [], "qa_count": 0},
        )
        assert "目的" in question

    @patch("spec_ai_writer.llm.openai_client.AsyncOpenAI")
    async def test_extract_structured_data(self, mock_openai):
        json_response = (
            '{"project_name": "test", "background": "背景", "purposes": ["目的1"]}'
        )
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json_response
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        data = await client.extract_structured_data(
            conversation="Q: 名前は? A: test",
            schema={
                "project_name": "プロジェクト名",
                "background": "背景",
                "purposes": "目的",
            },
        )
        assert data["project_name"] == "test"


@pytest.mark.unit
class TestOpenAIClientWithRealSdk:
    def test_client_can_be_created(self):
        """Not mocked on purpose: fails when an SDK update breaks client creation."""
        client = OpenAIClient(api_key="test-key", base_url="http://localhost:11434/v1")
        assert isinstance(client.client, AsyncOpenAI)
