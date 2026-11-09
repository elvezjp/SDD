"""
AWS Bedrock LLM Client Implementation

Provides integration with AWS Bedrock Runtime API to access Claude models.
Suitable for enterprise users already using AWS infrastructure.
"""

import json
import logging
from typing import List, Dict, Any, Optional

try:
    import aiobotocore.session
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import BotoCoreError, ClientError
    from botocore.tokens import ScopedEnvTokenProvider, TokenProviderChain
    AIOBOTOCORE_AVAILABLE = True
except ImportError:
    AIOBOTOCORE_AVAILABLE = False

from .base import BaseLLMClient
from .exceptions import LLMAuthenticationError, LLMConnectionError, LLMResponseError

logger = logging.getLogger(__name__)


class BedrockClient(BaseLLMClient):
    """
    AWS Bedrock client for Claude models.

    Supports Claude 3 models via AWS Bedrock Runtime API.
    Requires AWS credentials configured via environment variables or IAM role.
    """

    def __init__(
        self,
        model: str = "global.anthropic.claude-haiku-4-5-20251001-v1:0",
        region: str = "us-west-2",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 30.0,
        effort: Optional[str] = None
    ):
        """
        Initialize Bedrock client.

        Args:
            model: Bedrock model ID (e.g., "global.anthropic.claude-haiku-4-5-20251001-v1:0")
            region: AWS region (e.g., "us-west-2", "us-east-1")
            aws_access_key_id: AWS access key (optional, can use IAM role)
            aws_secret_access_key: AWS secret key (optional, can use IAM role)
            api_key: Bedrock API key. Takes precedence over the AWS credentials
            temperature: Accepted for interface compatibility; not sent to the API
            max_tokens: Maximum tokens to generate
            timeout: Timeout in seconds for API calls
            effort: Effort level, or None to use the model's default

        Raises:
            ImportError: If aiobotocore is not installed
        """
        if not AIOBOTOCORE_AVAILABLE:
            raise ImportError(
                "aiobotocore is required for Bedrock integration. "
                "Install it with: pip install aiobotocore"
            )

        # Note: Bedrock doesn't use api_key, so we pass empty string
        super().__init__("", model, temperature, timeout=timeout)
        self.max_tokens = max_tokens
        self.effort = effort

        # Store client kwargs; the actual HTTP client is created per chat() call
        self._session = aiobotocore.session.get_session()
        config_kwargs: Dict[str, Any] = {
            "read_timeout": int(self.timeout),
            "connect_timeout": int(self.timeout),
        }
        if api_key:
            # Scoped to this client so that AWS_BEARER_TOKEN_BEDROCK in the process
            # environment is neither required nor modified.
            self._session.register_component(
                "token_provider",
                TokenProviderChain(
                    providers=[
                        ScopedEnvTokenProvider(
                            self._session, environ={"AWS_BEARER_TOKEN_BEDROCK": api_key}
                        )
                    ]
                ),
            )
            config_kwargs["auth_scheme_preference"] = "httpBearerAuth"

        self._client_kwargs: Dict[str, Any] = {
            "region_name": region,
            "config": BotoConfig(**config_kwargs),
        }
        if not api_key and aws_access_key_id and aws_secret_access_key:
            self._client_kwargs["aws_access_key_id"] = aws_access_key_id
            self._client_kwargs["aws_secret_access_key"] = aws_secret_access_key

        logger.info(f"Bedrock client initialized with model: {model}, region: {region}")

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Convert standard message format to Bedrock API format.

        Bedrock API requires content to be a list of content blocks.

        Args:
            messages: List of message dicts with 'role' and 'content' keys

        Returns:
            List of message dicts for Bedrock API
        """
        return [
            {
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}]
            }
            for msg in messages
        ]

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send chat messages to Claude via Bedrock and get response.

        Bedrock API requires system message to be passed in a separate field,
        and content must be a list of content blocks. Sampling parameters are
        never sent, because Claude 4.7 and later reject them with a 400 error.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Accepted for interface compatibility; not sent to the API
            max_tokens: Override default max_tokens

        Returns:
            Assistant's response text

        Raises:
            RuntimeError: If API call fails
        """
        # Separate system message from conversation messages
        system_message = ""
        conversation_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append(msg)

        # Build request body for Bedrock Claude API
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens or self.max_tokens,
            "messages": self._convert_messages(conversation_messages)
        }

        # Add system message if present
        if system_message:
            request_body["system"] = system_message

        if self.effort:
            request_body["output_config"] = {"effort": self.effort}

        try:
            async with self._session.create_client(
                "bedrock-runtime", **self._client_kwargs
            ) as client:
                # Invoke model via Bedrock Runtime API
                response = await client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json"
                )

                # Parse response (body is an async stream in aiobotocore)
                response_body = json.loads(await response["body"].read())

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"Bedrock ClientError [{error_code}]: {error_message}")
            if error_code in ("UnrecognizedClientException", "AccessDeniedException", "InvalidSignatureException"):
                raise LLMAuthenticationError(
                    "AWS認証情報が無効です。.env ファイルの AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY を確認してください。"
                ) from e
            raise LLMResponseError(f"Bedrock API error [{error_code}]: {error_message}") from e

        except BotoCoreError as e:
            logger.error(f"Bedrock BotoCoreError: {e}")
            raise LLMConnectionError(
                f"Bedrock APIに接続できません。ネットワーク接続とAWSリージョン設定を確認してください: {e}"
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error during Bedrock API call: {e}")
            raise LLMResponseError(f"Bedrock API call failed: {e}") from e

        # Bedrock Claude API returns content as a list of content blocks
        text = "".join(
            block.get("text", "")
            for block in response_body.get("content", [])
            if block.get("type") == "text"
        )
        logger.debug(f"Bedrock response received: {len(text)} characters")
        stop_details = response_body.get("stop_details") or {}
        return self._require_response_text(
            "Bedrock", text, response_body.get("stop_reason"), stop_details.get("category")
        )
