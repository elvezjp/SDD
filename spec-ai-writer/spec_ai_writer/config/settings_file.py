"""Persistent JSON store for application settings editable from the Web UI.

Schema (data/settings.json):

    {
      "active_provider": "kimi",
      "temperature": 0.7,
      "effort": "auto",
      "providers": {
        "claude":     { "model": "...", "api_key": "..." },
        "openai":     { "model": "...", "api_key": "..." },
        "openrouter": { "model": "...", "api_key": "..." },
        "ollama":     { "model": "...", "base_url": "..." },
        "lmstudio":   { "model": "...", "base_url": "..." },
        "kimi":       { "model": "...", "api_key": "..." },
        "bedrock":    {
            "model": "...",
            "api_key": "...",
            "aws_access_key_id": "...",
            "aws_secret_access_key": "...",
            "aws_region": "..."
        }
      }
    }

Top-level and per-provider fields are all optional; missing fields fall back
to environment variables / pydantic defaults (see config/settings.py).

Security: API keys are stored in plaintext (same threat model as .env).
The file is written with 0o600 permissions. data/ is in .gitignore.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_SETTINGS_FILENAME = "settings.json"


def _resolve_data_dir() -> Path:
    data_dir = os.environ.get("DATA_DIR", "./data")
    return Path(data_dir).expanduser().resolve()


def get_settings_path() -> Path:
    return _resolve_data_dir() / _SETTINGS_FILENAME


# ---------------------------------------------------------------------------
# Load / Save
# ---------------------------------------------------------------------------


def load_settings() -> dict[str, Any]:
    """Load settings from disk. Returns {} if file missing or unreadable."""
    path = get_settings_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Failed to read settings at %s: %s", path, e)
        return {}
    if not isinstance(data, dict):
        logger.warning("settings.json is not a JSON object; ignoring.")
        return {}
    return data


def save_settings(data: dict[str, Any]) -> Path:
    """Atomically write settings to disk with 0o600 permissions."""
    if not isinstance(data, dict):
        raise TypeError(f"Settings must be a dict, got {type(data).__name__}")

    path = get_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.flush()
        try:
            os.fsync(f.fileno())
        except (AttributeError, OSError):
            pass

    os.replace(tmp, path)

    if sys.platform != "win32":
        try:
            os.chmod(path, 0o600)
        except OSError as e:
            logger.warning("Failed to chmod %s: %s", path, e)

    logger.info("Wrote settings to %s", path)
    return path


# ---------------------------------------------------------------------------
# Migration from legacy flat schema
# ---------------------------------------------------------------------------


_LEGACY_FILENAME = "llm_settings.json"


def _get_legacy_path() -> Path:
    return _resolve_data_dir() / _LEGACY_FILENAME


def migrate_legacy_settings() -> None:
    """Convert data/llm_settings.json (flat) to data/settings.json (nested).

    Called once at startup if the old file exists and the new one does not.
    The legacy file is renamed to llm_settings.json.migrated after conversion.
    """
    legacy = _get_legacy_path()
    new = get_settings_path()

    if not legacy.exists() or new.exists():
        return

    try:
        with legacy.open("r", encoding="utf-8") as f:
            flat = json.load(f)
        if not isinstance(flat, dict):
            return
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("Migration skipped – cannot read legacy file: %s", e)
        return

    nested = _flat_to_nested(flat)
    save_settings(nested)

    try:
        legacy.rename(legacy.with_suffix(".json.migrated"))
    except OSError:
        pass

    logger.info("Migrated %s → %s", legacy.name, _SETTINGS_FILENAME)


def _flat_to_nested(flat: dict[str, Any]) -> dict[str, Any]:
    """Convert old flat overlay format to new nested settings format."""
    nested: dict[str, Any] = {}

    if "default_llm_provider" in flat:
        nested["active_provider"] = flat["default_llm_provider"]
    if "temperature" in flat:
        nested["temperature"] = flat["temperature"]

    providers: dict[str, Any] = {}

    # Claude
    claude: dict[str, Any] = {}
    if flat.get("anthropic_api_key"):
        claude["api_key"] = flat["anthropic_api_key"]
    if claude:
        providers["claude"] = claude

    # Detect which openai-compatible provider the old base_url belonged to
    base_url: str = flat.get("openai_base_url", "") or ""
    api_key: str = flat.get("openai_api_key", "") or ""
    model: str = flat.get("openai_model", "") or ""

    if "openrouter.ai" in base_url:
        p: dict[str, Any] = {}
        if model:
            p["model"] = model
        if api_key:
            p["api_key"] = api_key
        if p:
            providers["openrouter"] = p
    elif "11434" in base_url:
        p = {}
        if model:
            p["model"] = model
        if base_url:
            p["base_url"] = base_url
        if p:
            providers["ollama"] = p
    elif "1234" in base_url:
        p = {}
        if model:
            p["model"] = model
        if base_url:
            p["base_url"] = base_url
        if p:
            providers["lmstudio"] = p
    else:
        # Default: plain OpenAI
        p = {}
        if model:
            p["model"] = model
        if api_key:
            p["api_key"] = api_key
        if p:
            providers["openai"] = p

    # Bedrock
    bedrock: dict[str, Any] = {}
    if flat.get("bedrock_model_id"):
        bedrock["model"] = flat["bedrock_model_id"]
    if flat.get("aws_access_key_id"):
        bedrock["aws_access_key_id"] = flat["aws_access_key_id"]
    if flat.get("aws_secret_access_key"):
        bedrock["aws_secret_access_key"] = flat["aws_secret_access_key"]
    if flat.get("aws_region"):
        bedrock["aws_region"] = flat["aws_region"]
    if bedrock:
        providers["bedrock"] = bedrock

    if providers:
        nested["providers"] = providers

    return nested
