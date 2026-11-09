"""OpenAI-compatible LLM client."""

import logging
from typing import Dict, List, Optional

try:
    from openai import AsyncOpenAI, AuthenticationError, APIConnectionError, APITimeoutError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import BaseLLMClient
from .exceptions import LLMAuthenticationError, LLMConnectionError, LLMResponseError

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI and OpenAI-compatible endpoints.

    Supports OpenAI, OpenRouter, Ollama, LM Studio, Moonshot Kimi, and any
    other provider that implements the OpenAI chat completions API.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-6-luna",
        temperature: float = 0.7,
        max_tokens: int = 16000,
        timeout: float = 120.0,
        base_url: Optional[str] = None,
        extra_body: Optional[dict] = None,
        max_tokens_param: str = "max_tokens",
        temperature_supported: bool = False,
        fixed_temperature: Optional[float] = None,
        effort: Optional[str] = None,
    ):
        """
        Args:
            api_key: API key. For local servers that don't require auth, pass
                any non-empty string (e.g. "dummy").
            model: Model ID.
            temperature: Sampling temperature (0.0–2.0).
            max_tokens: Maximum tokens to generate.
            timeout: Request timeout in seconds.
            base_url: Override the default API endpoint. None = OpenAI official.
            extra_body: Provider-specific fields passed verbatim in the request
                body (e.g. {"thinking": {"type": "disabled"}} for Kimi).
            max_tokens_param: Parameter name for token limit. Use
                "max_completion_tokens" for o1/o3 series models.
            effort: reasoning_effort to send, or None to use the model's default.
            temperature_supported: Set False for models that reject the
                temperature parameter (o1/o3 series).
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        if not api_key:
            raise ValueError("OpenAI API key is required")

        super().__init__(api_key, model, temperature, timeout=timeout)
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.extra_body = extra_body or {}
        self.max_tokens_param = max_tokens_param
        self.temperature_supported = temperature_supported
        self.fixed_temperature = fixed_temperature
        self.effort = effort

        client_kwargs: dict = {"api_key": api_key, "timeout": self.timeout}
        if base_url:
            client_kwargs["base_url"] = base_url
        self.client = AsyncOpenAI(**client_kwargs)
        logger.info(
            "OpenAI client initialized: model=%s%s",
            model,
            f", base_url={base_url}" if base_url else "",
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        effective_max_tokens = max_tokens or self.max_tokens
        if self.fixed_temperature is not None:
            effective_temperature = self.fixed_temperature
        else:
            effective_temperature = temperature if temperature is not None else self.temperature

        api_kwargs: dict = {
            "model": self.model,
            "messages": messages,
            self.max_tokens_param: effective_max_tokens,
        }
        if self.temperature_supported:
            api_kwargs["temperature"] = effective_temperature
        if self.effort:
            api_kwargs["reasoning_effort"] = self.effort
        if self.extra_body:
            api_kwargs["extra_body"] = self.extra_body

        try:
            response = await self.client.chat.completions.create(**api_kwargs)
        except AuthenticationError as e:
            logger.error("OpenAI authentication failed: %s", e)
            raise LLMAuthenticationError(
                "OpenAI APIキーが無効です。設定画面の API キーを確認してください。"
            ) from e
        except (APIConnectionError, APITimeoutError) as e:
            logger.error("OpenAI connection error: %s", e)
            raise LLMConnectionError(
                f"OpenAI API に接続できません。ネットワーク接続を確認してください: {e}"
            ) from e
        except Exception as e:
            logger.error("OpenAI API call failed: %s", e)
            raise LLMResponseError(f"OpenAI API call failed: {e}") from e

        if not response.choices:
            logger.warning("Empty response from OpenAI API")
            return ""

        result = response.choices[0].message.content or ""
        logger.debug("OpenAI response: %d characters", len(result))
        return result


# Commonly used model IDs (kept for backwards compatibility with tests)
GPT4_TURBO = "gpt-4-turbo-preview"
GPT35_TURBO = "gpt-3.5-turbo"
