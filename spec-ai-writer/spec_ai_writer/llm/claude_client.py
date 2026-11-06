"""Claude API client implementation."""

import logging
import re
from typing import Dict, List, Optional

import httpx
from anthropic import AsyncAnthropic, AuthenticationError, APIConnectionError, APITimeoutError

from .base import BaseLLMClient
from .exceptions import LLMAuthenticationError, LLMConnectionError, LLMResponseError

logger = logging.getLogger(__name__)

# e.g. "claude-haiku-4-5-20251001", "claude-sonnet-4-20250514", "claude-haiku-5-5"
_MODEL_VERSION_RE = re.compile(r"^claude-[a-z]+-(\d+)(?:-(\d{1,2}))?(?:-\d{8})?$")


def temperature_supported(model: str) -> bool:
    """
    Return whether the Claude model accepts the temperature parameter.

    Claude 4.7 and later (including the 5 family) reject sampling parameters
    with a 400 error, so temperature is only sent to Claude 4.6 and earlier.
    Unknown model names are treated as unsupported, since omitting
    temperature never causes a request error.
    """
    if model.startswith("claude-3"):
        return True
    match = _MODEL_VERSION_RE.match(model)
    if not match:
        return False
    major, minor = int(match.group(1)), int(match.group(2) or 0)
    return (major, minor) <= (4, 6)


class ClaudeClient(BaseLLMClient):
    """Client for Anthropic's Claude API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-haiku-4-5-20251001",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 30.0
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key
            model: Claude model name
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Timeout in seconds for API calls
        """
        super().__init__(api_key, model, temperature, timeout=timeout)
        self.max_tokens = max_tokens
        self.client = AsyncAnthropic(api_key=api_key, timeout=httpx.Timeout(self.timeout))

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send a chat request to Claude.

        Anthropic API requires system message to be passed separately.
        This method extracts the system message and passes it as a parameter.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Claude's response text

        Raises:
            Exception: If API call fails
        """
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Separate system message from conversation messages
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append(msg)

        try:
            # Build API call kwargs
            api_kwargs = {
                "model": self.model,
                "max_tokens": tokens,
                "messages": conversation_messages
            }

            if temperature_supported(self.model):
                api_kwargs["temperature"] = temp

            # Add system message if present
            if system_message:
                api_kwargs["system"] = system_message

            response = await self.client.messages.create(**api_kwargs)
            # Models with thinking enabled return thinking blocks before the text
            return "".join(block.text for block in response.content if block.type == "text")
        except AuthenticationError as e:
            logger.error(f"Claude authentication failed: {e}")
            raise LLMAuthenticationError(
                "Anthropic APIキーが無効です。.env ファイルの ANTHROPIC_API_KEY を確認してください。"
            ) from e
        except (APIConnectionError, APITimeoutError) as e:
            logger.error(f"Claude connection error: {e}")
            raise LLMConnectionError(
                f"Claude APIに接続できません。ネットワーク接続を確認してください: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise LLMResponseError(f"Claude API error: {str(e)}") from e
