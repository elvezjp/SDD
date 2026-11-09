"""Registry of LLM provider and model-specific configurations.

Adding a new provider: add an entry to PROVIDERS.
Adding a new model family with non-standard params: add an entry to MODELS.
No other files need to change.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Optional


@dataclass
class ProviderConfig:
    client_type: str  # "openai_compatible" | "claude" | "bedrock"
    display_name: str = ""
    base_url: Optional[str] = None
    api_key_required: bool = True
    extra_body: dict = field(default_factory=dict)


@dataclass
class ModelConfig:
    max_tokens_param: str = "max_tokens"
    temperature_supported: bool = True
    fixed_temperature: Optional[float] = None  # overrides user setting when set
    effort_levels: tuple[str, ...] = ()  # empty when effort cannot be set


PROVIDERS: dict[str, ProviderConfig] = {
    "claude": ProviderConfig(
        client_type="claude",
        display_name="Claude (Anthropic API)",
    ),
    "openai": ProviderConfig(
        client_type="openai_compatible",
        display_name="OpenAI",
    ),
    "openrouter": ProviderConfig(
        client_type="openai_compatible",
        display_name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
    ),
    "ollama": ProviderConfig(
        client_type="openai_compatible",
        display_name="Ollama (ローカル)",
        base_url="http://localhost:11434/v1",
        api_key_required=False,
    ),
    "lmstudio": ProviderConfig(
        client_type="openai_compatible",
        display_name="LM Studio (ローカル)",
        base_url="http://localhost:1234/v1",
        api_key_required=False,
    ),
    "kimi": ProviderConfig(
        client_type="openai_compatible",
        display_name="Moonshot Kimi",
        base_url="https://api.moonshot.ai/v1",
        extra_body={"thinking": {"type": "disabled"}},
    ),
    "bedrock": ProviderConfig(
        client_type="bedrock",
        display_name="AWS Bedrock",
    ),
}

_CLAUDE_MODEL_RE = re.compile(r"claude-([a-z]+)-(\d+)(?:-(\d{1,2}))?(?=$|[-:@])")

_OPENAI_REASONING = ModelConfig(
    max_tokens_param="max_completion_tokens",
    temperature_supported=False,
    effort_levels=("low", "medium", "high"),
)
_OPENAI_REASONING_FIXED_EFFORT = ModelConfig(
    max_tokens_param="max_completion_tokens", temperature_supported=False
)

# Model-specific parameter overrides, matched by model family: a key matches the
# same ID or any ID that continues it after "-", "." or ":" (the longest key wins).
MODELS: dict[str, ModelConfig] = {
    "gpt-5": _OPENAI_REASONING,
    "gpt-5-pro": _OPENAI_REASONING_FIXED_EFFORT,
    "gpt-5.4-pro": _OPENAI_REASONING_FIXED_EFFORT,
    "gpt-5.5-pro": _OPENAI_REASONING_FIXED_EFFORT,
    "o1": _OPENAI_REASONING,
    "o1-mini": _OPENAI_REASONING_FIXED_EFFORT,
    "o3": _OPENAI_REASONING,
    "o4": _OPENAI_REASONING,
    "kimi-k2.6": ModelConfig(fixed_temperature=0.6),
}


def _claude_effort_levels(model: str) -> tuple[str, ...]:
    """Return the effort levels a Claude model accepts (empty when it has none)."""
    match = _CLAUDE_MODEL_RE.search(model)
    if not match:
        return ()
    family = match.group(1)
    version = (int(match.group(2)), int(match.group(3) or 0))
    if version >= (4, 7):
        return ("low", "medium", "high", "xhigh", "max")
    if version == (4, 6) and family in ("opus", "sonnet"):
        return ("low", "medium", "high", "max")
    if version == (4, 5) and family == "opus":
        return ("low", "medium", "high")
    return ()


def _find_model_family(model: str) -> Optional[ModelConfig]:
    # OpenRouter prefixes IDs with the vendor, e.g. "openai/gpt-5.5"
    name = model.rsplit("/", 1)[-1]
    for key in sorted(MODELS, key=len, reverse=True):
        if name == key or (name.startswith(key) and name[len(key)] in "-.:"):
            return MODELS[key]
    return None


def get_model_config(model: str, provider: Optional[str] = None) -> ModelConfig:
    """Return the parameters a model accepts on a provider, falling back to defaults."""
    client_type = PROVIDERS[provider].client_type if provider in PROVIDERS else None
    if client_type in ("claude", "bedrock"):
        # Sampling parameters are never sent to Claude (see ClaudeClient.chat)
        return ModelConfig(temperature_supported=False, effort_levels=_claude_effort_levels(model))

    config = _find_model_family(model) or ModelConfig()
    if provider != "openai":
        # reasoning_effort is only known to work on the OpenAI API itself
        config = replace(config, effort_levels=())
    return config
