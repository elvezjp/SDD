"""Base abstract interface for LLM clients."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .exceptions import LLMResponseError

logger = logging.getLogger(__name__)

# 共通プロンプト定義（spec.md 3.7.4）
QUESTION_GENERATION_INSTRUCTION = "次の質問を1つだけ生成してください。質問のみを出力し、説明や前置きは不要です。"

EXTRACTION_SYSTEM_PROMPT = """あなたは会話から構造化データを抽出する専門家です。
与えられた会話から、指定されたスキーマに従ってデータを抽出し、JSON形式で返してください。

重要な指示:
1. 会話に明示的に含まれていない情報は推測しないでください
2. リストや配列が適切な場合は配列として返してください
3. 情報が欠けている場合は null を使用してください
4. JSON形式で返してください（マークダウンのコードブロックは不要）"""

EXTRACTION_USER_PROMPT_TEMPLATE = """以下の会話から、次のスキーマに従ってデータを抽出してください:

{schema_description}

会話:
{conversation}

JSON形式で抽出したデータを返してください:"""


class BaseLLMClient(ABC):
    """Abstract base class for LLM API clients."""

    def __init__(self, api_key: str = "", model: Optional[str] = None, temperature: float = 0.7, timeout: float = 30.0):
        """
        Initialize the LLM client.

        Args:
            api_key: API key for the LLM provider
            model: Model name to use (provider-specific)
            temperature: Temperature for generation (0.0-2.0)
            timeout: Timeout in seconds for API calls
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def _require_response_text(
        self,
        provider: str,
        text: str,
        stop_reason: Optional[str],
        refusal_category: Optional[str] = None,
    ) -> str:
        """
        Return the response text, or raise when the response is not usable.

        Args:
            provider: Provider name used in the error message
            text: Text extracted from the response
            stop_reason: Why the model stopped generating
            refusal_category: Refusal category, when the provider reports one

        Returns:
            The response text

        Raises:
            LLMResponseError: If the model refused, was cut off, or returned no text
        """
        if stop_reason == "refusal":
            category = f"（カテゴリ: {refusal_category}）" if refusal_category else ""
            logger.warning("%s refused the request: category=%s", provider, refusal_category)
            raise LLMResponseError(f"{provider} がリクエストへの応答を拒否しました{category}。")
        if stop_reason == "max_tokens":
            logger.warning("%s response reached max_tokens: %d characters", provider, len(text))
            raise LLMResponseError(
                f"{provider} の応答が出力の上限（max_tokens）に達し、途中で打ち切られました。"
            )
        if not text.strip():
            logger.warning("%s returned no text: stop_reason=%s", provider, stop_reason)
            raise LLMResponseError(f"{provider} の応答が空でした（stop_reason: {stop_reason}）。")
        return text

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send a chat request to the LLM and return the response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                      Example: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate

        Returns:
            The LLM's response text

        Raises:
            Exception: If the API call fails
        """
        pass

    async def generate_question(
        self,
        system_prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate the next interview question based on system prompt and context.

        Args:
            system_prompt: System prompt defining the LLM's role and task
            context: Dictionary containing conversation history and metadata
                     Keys: conversation_history, missing_fields, previous_phases

        Returns:
            The generated question text

        Raises:
            Exception: If question generation fails
        """
        # Build context prompt
        prompt = self._build_context_prompt(system_prompt, context)

        # Create messages with system prompt and user request
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt + "\n\n" + QUESTION_GENERATION_INSTRUCTION}
        ]

        return await self.chat(messages)

    async def extract_structured_data(
        self,
        conversation: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured data from a conversation according to a schema.

        Args:
            conversation: The full conversation text
            schema: JSON schema describing the expected structure

        Returns:
            Dictionary containing the extracted structured data

        Raises:
            Exception: If extraction fails
        """
        # Build schema description
        schema_description = "\n".join([
            f"- {field}: {desc}"
            for field, desc in schema.items()
        ])

        # Build user prompt from template
        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            schema_description=schema_description,
            conversation=conversation
        )

        # Create messages with system and user prompts
        messages = [
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # Use lower temperature for more consistent extraction
        response = await self.chat(messages, temperature=0.3)

        # Parse JSON response
        try:
            # Remove potential markdown code blocks
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                lines = cleaned_response.split("\n")
                if len(lines) > 2:
                    cleaned_response = "\n".join(lines[1:-1])

            # Try to extract JSON from response
            json_start = cleaned_response.find("{")
            json_end = cleaned_response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = cleaned_response[json_start:json_end]
                return json.loads(json_str)
            else:
                return json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            logger.warning(f"LLM応答のJSON解析に失敗しました: {e}")
            return {}

    def _build_context_prompt(
        self,
        system_prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build a prompt that includes system instructions and context.

        Args:
            system_prompt: The base system prompt
            context: Context dictionary with conversation history, etc.

        Returns:
            Complete prompt string
        """
        prompt_parts = [system_prompt]

        if "conversation_history" in context and context["conversation_history"]:
            prompt_parts.append("\n\n## 会話履歴:\n")
            prompt_parts.append(context["conversation_history"])

        if "missing_fields" in context and context["missing_fields"]:
            prompt_parts.append("\n\n## まだ収集が必要な情報:\n")
            for field in context["missing_fields"]:
                prompt_parts.append(f"- {field}\n")

        if "previous_phases" in context and context["previous_phases"]:
            prompt_parts.append("\n\n## 前フェーズの情報:\n")
            prompt_parts.append(str(context["previous_phases"]))

        return "".join(prompt_parts)
