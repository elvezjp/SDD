"""Settings API router.

GET /api/settings   – Return current settings with per-field source info.
GET /api/settings/generation-params – Return the parameters a model accepts.
PUT /api/settings   – Partial update; persists to data/settings.json and hot-reloads.

Per-provider slots are stored independently in the JSON file, so switching
between providers never overwrites another provider's configuration.

Secret fields (api_key, aws_*) are returned masked and are ignored on PUT
when the value is empty, so re-submitting the masked placeholder cannot
accidentally erase the stored key.
"""

from __future__ import annotations

import logging
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from spec_ai_writer.config.settings import (
    SettingsSource,
    get_settings,
    get_settings_sources,
    reload_settings,
)
from spec_ai_writer.config.settings_file import load_settings, save_settings
from spec_ai_writer.llm.factory import configured_model
from spec_ai_writer.llm.provider_registry import PROVIDERS, get_model_config

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

_PROVIDER_NAMES = Literal[
    "claude", "openai", "openrouter", "ollama", "lmstudio", "kimi", "bedrock"
]


class ProviderSettingsResponse(BaseModel):
    model: str = ""
    api_key_masked: str = ""
    base_url: str = ""
    # Bedrock-only
    aws_access_key_id_masked: str = ""
    aws_secret_access_key_masked: str = ""
    aws_region: str = ""


class SettingsResponse(BaseModel):
    active_provider: str
    temperature: float
    effort: str
    providers: dict[str, ProviderSettingsResponse]
    # Flat source map: "temperature" / "kimi.model" / "claude.api_key" → source
    sources: dict[str, SettingsSource]


class GenerationParamsResponse(BaseModel):
    model: str
    temperature_supported: bool
    effort_levels: list[str]


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ProviderUpdate(BaseModel):
    model: Optional[str] = None
    api_key: Optional[str] = Field(default=None, repr=False)
    clear_api_key: Optional[bool] = None
    base_url: Optional[str] = None
    aws_access_key_id: Optional[str] = Field(default=None, repr=False)
    aws_secret_access_key: Optional[str] = Field(default=None, repr=False)
    aws_region: Optional[str] = None


class SettingsUpdateRequest(BaseModel):
    active_provider: Optional[_PROVIDER_NAMES] = None  # type: ignore[valid-type]
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    effort: Optional[Literal["auto", "low", "medium", "high", "xhigh", "max"]] = None
    providers: Optional[dict[str, ProviderUpdate]] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}****{value[-4:]}"


def _build_response() -> SettingsResponse:
    s = get_settings()
    srcs = get_settings_sources()

    def _src(flat_key: str, dot_key: str) -> SettingsSource:
        return srcs.get(flat_key, "default")

    providers: dict[str, ProviderSettingsResponse] = {}
    source_map: dict[str, SettingsSource] = {
        "active_provider": srcs.get("default_llm_provider", "default"),
        "temperature":     srcs.get("temperature", "default"),
        "effort":          srcs.get("effort", "default"),
    }

    for name in PROVIDERS:
        if name == "claude":
            providers[name] = ProviderSettingsResponse(
                model=s.claude_model,
                api_key_masked=_mask(s.anthropic_api_key),
            )
            source_map["claude.model"]   = srcs.get("claude_model", "default")
            source_map["claude.api_key"] = srcs.get("anthropic_api_key", "default")

        elif name == "openai":
            providers[name] = ProviderSettingsResponse(
                model=s.openai_model,
                api_key_masked=_mask(s.openai_api_key),
            )
            source_map["openai.model"]   = srcs.get("openai_model", "default")
            source_map["openai.api_key"] = srcs.get("openai_api_key", "default")

        elif name == "openrouter":
            providers[name] = ProviderSettingsResponse(
                model=s.openrouter_model,
                api_key_masked=_mask(s.openrouter_api_key),
            )
            source_map["openrouter.model"]   = srcs.get("openrouter_model", "default")
            source_map["openrouter.api_key"] = srcs.get("openrouter_api_key", "default")

        elif name == "ollama":
            providers[name] = ProviderSettingsResponse(
                model=s.ollama_model,
                base_url=s.ollama_base_url,
            )
            source_map["ollama.model"]    = srcs.get("ollama_model", "default")
            source_map["ollama.base_url"] = srcs.get("ollama_base_url", "default")

        elif name == "lmstudio":
            providers[name] = ProviderSettingsResponse(
                model=s.lmstudio_model,
                base_url=s.lmstudio_base_url,
            )
            source_map["lmstudio.model"]    = srcs.get("lmstudio_model", "default")
            source_map["lmstudio.base_url"] = srcs.get("lmstudio_base_url", "default")

        elif name == "kimi":
            providers[name] = ProviderSettingsResponse(
                model=s.kimi_model,
                api_key_masked=_mask(s.kimi_api_key),
            )
            source_map["kimi.model"]   = srcs.get("kimi_model", "default")
            source_map["kimi.api_key"] = srcs.get("kimi_api_key", "default")

        elif name == "bedrock":
            providers[name] = ProviderSettingsResponse(
                model=s.bedrock_model_id,
                api_key_masked=_mask(s.aws_bearer_token_bedrock),
                aws_access_key_id_masked=_mask(s.aws_access_key_id),
                aws_secret_access_key_masked=_mask(s.aws_secret_access_key),
                aws_region=s.aws_region,
            )
            source_map["bedrock.model"]                  = srcs.get("bedrock_model_id", "default")
            source_map["bedrock.api_key"]                = srcs.get("aws_bearer_token_bedrock", "default")
            source_map["bedrock.aws_access_key_id"]      = srcs.get("aws_access_key_id", "default")
            source_map["bedrock.aws_secret_access_key"]  = srcs.get("aws_secret_access_key", "default")
            source_map["bedrock.aws_region"]             = srcs.get("aws_region", "default")

    return SettingsResponse(
        active_provider=s.default_llm_provider,
        temperature=s.temperature,
        effort=s.effort,
        providers=providers,
        sources=source_map,
    )


def _merge_settings(existing: dict[str, Any], req: SettingsUpdateRequest) -> dict[str, Any]:
    """Deep-merge a partial update request into the existing JSON settings dict."""
    merged: dict[str, Any] = dict(existing)

    if req.active_provider is not None:
        merged["active_provider"] = req.active_provider
    if req.temperature is not None:
        merged["temperature"] = req.temperature
    if req.effort is not None:
        merged["effort"] = req.effort

    if req.providers:
        merged_providers: dict[str, Any] = dict(merged.get("providers", {}))

        for provider_name, pu in req.providers.items():
            existing_slot: dict[str, Any] = dict(merged_providers.get(provider_name, {}))

            # Non-secret fields: empty string removes the key so Settings default takes over.
            if pu.model is not None:
                if pu.model:
                    existing_slot["model"] = pu.model
                else:
                    existing_slot.pop("model", None)

            if pu.base_url is not None:
                if pu.base_url:
                    existing_slot["base_url"] = pu.base_url
                else:
                    existing_slot.pop("base_url", None)

            if pu.aws_region is not None:
                if pu.aws_region:
                    existing_slot["aws_region"] = pu.aws_region
                else:
                    existing_slot.pop("aws_region", None)

            if pu.clear_api_key:
                existing_slot.pop("api_key", None)

            # Secret fields: empty string = "no change" (avoid accidental erasure).
            if pu.api_key:
                existing_slot["api_key"] = pu.api_key
            if pu.aws_access_key_id:
                existing_slot["aws_access_key_id"] = pu.aws_access_key_id
            if pu.aws_secret_access_key:
                existing_slot["aws_secret_access_key"] = pu.aws_secret_access_key

            merged_providers[provider_name] = existing_slot

        merged["providers"] = merged_providers

    return merged


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=SettingsResponse)
async def get_llm_settings() -> SettingsResponse:
    """Return current settings with secrets masked and source info per field."""
    return _build_response()


@router.get("/generation-params", response_model=GenerationParamsResponse)
async def get_generation_params(
    provider: _PROVIDER_NAMES,  # type: ignore[valid-type]
    model: str = "",
) -> GenerationParamsResponse:
    """Return the generation parameters applied to a provider and model."""
    resolved = model or configured_model(get_settings(), provider)
    config = get_model_config(resolved, provider)
    return GenerationParamsResponse(
        model=resolved,
        temperature_supported=config.temperature_supported and config.fixed_temperature is None,
        effort_levels=list(config.effort_levels),
    )


@router.put("/", response_model=SettingsResponse)
async def update_llm_settings(payload: SettingsUpdateRequest) -> SettingsResponse:
    """Partially update settings, persist to settings.json, and hot-reload."""
    try:
        existing = load_settings()
        merged = _merge_settings(existing, payload)
        save_settings(merged)
    except Exception as e:
        logger.exception("Failed to save settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save settings: {e}",
        ) from e

    reload_settings()

    s = get_settings()
    is_valid, errors = s.validate_llm_config()
    if not is_valid:
        logger.warning("Settings saved but failed validation: %s", errors)

    return _build_response()
