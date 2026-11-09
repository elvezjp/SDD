"""API tests for GET/PUT /api/settings."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from spec_ai_writer.config.settings import reload_settings
from spec_ai_writer.config.settings_file import get_settings_path
from spec_ai_writer.web.app import app


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    """TestClient with isolated data directory and development mode."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    monkeypatch.setenv("KIMI_API_KEY", "")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "")
    monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "claude")
    reload_settings()
    yield TestClient(app)
    reload_settings()


@pytest.mark.api
class TestSettingsAPI:
    def test_get_returns_all_providers(self, client):
        resp = client.get("/api/settings/")
        assert resp.status_code == 200
        body = resp.json()
        assert "active_provider" in body
        assert "temperature" in body
        assert "providers" in body
        assert "sources" in body
        # All 7 providers should be present
        for p in ("claude", "openai", "openrouter", "ollama", "lmstudio", "kimi", "bedrock"):
            assert p in body["providers"]

    def test_get_returns_masked_keys(self, client, tmp_path, monkeypatch):
        from spec_ai_writer.config.settings_file import save_settings
        save_settings({
            "active_provider": "kimi",
            "providers": {
                "kimi": {
                    "model": "kimi-k2.6",
                    "api_key": "sk-kimi-supersecretvalue",
                },
            },
        })
        reload_settings()

        resp = client.get("/api/settings/")
        assert resp.status_code == 200
        body = resp.json()

        assert body["active_provider"] == "kimi"
        assert body["providers"]["kimi"]["model"] == "kimi-k2.6"

        masked = body["providers"]["kimi"]["api_key_masked"]
        assert masked != "sk-kimi-supersecretvalue"
        assert "****" in masked

    def test_get_source_tracking(self, client, tmp_path, monkeypatch):
        from spec_ai_writer.config.settings_file import save_settings
        save_settings({
            "active_provider": "kimi",
            "providers": {"kimi": {"model": "kimi-k2.6", "api_key": "sk-kimi"}},
        })
        reload_settings()

        resp = client.get("/api/settings/")
        body = resp.json()

        assert body["sources"]["active_provider"] == "json"
        assert body["sources"]["kimi.model"] == "json"
        assert body["sources"]["kimi.api_key"] == "json"

    def test_put_persists_provider_slot(self, client, tmp_path):
        resp = client.put("/api/settings/", json={
            "active_provider": "kimi",
            "providers": {
                "kimi": {
                    "model": "kimi-k2.6",
                    "api_key": "sk-kimi-newkey",
                },
            },
        })
        assert resp.status_code == 200, resp.text
        body = resp.json()

        assert body["active_provider"] == "kimi"
        assert body["providers"]["kimi"]["model"] == "kimi-k2.6"
        assert "****" in body["providers"]["kimi"]["api_key_masked"]

        stored = json.loads(get_settings_path().read_text())
        assert stored["active_provider"] == "kimi"
        assert stored["providers"]["kimi"]["api_key"] == "sk-kimi-newkey"

    def test_put_empty_api_key_preserves_existing(self, client):
        client.put("/api/settings/", json={
            "active_provider": "openai",
            "providers": {"openai": {"api_key": "sk-original-key-12345", "model": "gpt-4o"}},
        })

        resp = client.put("/api/settings/", json={
            "providers": {"openai": {"model": "gpt-4o-mini"}},
        })
        assert resp.status_code == 200

        stored = json.loads(get_settings_path().read_text())
        assert stored["providers"]["openai"]["api_key"] == "sk-original-key-12345"
        assert stored["providers"]["openai"]["model"] == "gpt-4o-mini"

    def test_put_explicit_empty_api_key_preserves(self, client):
        """Explicit empty string for api_key is treated as 'no change'."""
        client.put("/api/settings/", json={
            "active_provider": "openai",
            "providers": {"openai": {"api_key": "sk-original", "model": "gpt-4o"}},
        })

        resp = client.put("/api/settings/", json={
            "providers": {"openai": {"api_key": "", "model": "gpt-4"}},
        })
        assert resp.status_code == 200

        stored = json.loads(get_settings_path().read_text())
        assert stored["providers"]["openai"]["api_key"] == "sk-original"

    def test_put_independent_provider_slots(self, client):
        """Saving one provider must not overwrite another provider's settings."""
        client.put("/api/settings/", json={
            "providers": {"kimi": {"api_key": "sk-kimi-key", "model": "kimi-k2.6"}},
        })
        client.put("/api/settings/", json={
            "active_provider": "openai",
            "providers": {"openai": {"api_key": "sk-openai-key", "model": "gpt-4o"}},
        })

        stored = json.loads(get_settings_path().read_text())
        assert stored["providers"]["kimi"]["api_key"] == "sk-kimi-key"
        assert stored["providers"]["openai"]["api_key"] == "sk-openai-key"

    def test_put_rejects_invalid_temperature(self, client):
        resp = client.put("/api/settings/", json={"temperature": 5.0})
        assert resp.status_code == 422

    def test_put_rejects_invalid_provider(self, client):
        resp = client.put("/api/settings/", json={"active_provider": "gemini"})
        assert resp.status_code == 422

    def test_subsequent_get_reflects_put(self, client):
        client.put("/api/settings/", json={
            "active_provider": "kimi",
            "providers": {"kimi": {"model": "kimi-k2.6", "api_key": "sk-kimi"}},
        })
        get_resp = client.get("/api/settings/")
        assert get_resp.status_code == 200
        assert get_resp.json()["active_provider"] == "kimi"
        assert get_resp.json()["providers"]["kimi"]["model"] == "kimi-k2.6"


@pytest.mark.api
class TestGenerationParamsAPI:
    @pytest.mark.parametrize(
        "provider, model, temperature, effort",
        [
            ("claude", "claude-haiku-5-5", False, ["low", "medium", "high", "xhigh", "max"]),
            ("claude", "claude-haiku-4-5-20251001", False, []),
            ("ollama", "gemma3:4b", True, []),
            ("kimi", "kimi-k2.6", False, []),
        ],
    )
    def test_reports_params_for_model(self, client, provider, model, temperature, effort):
        resp = client.get(
            "/api/settings/generation-params", params={"provider": provider, "model": model}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["temperature_supported"] is temperature
        assert body["effort_levels"] == effort

    def test_empty_model_uses_configured_model(self, client):
        resp = client.get("/api/settings/generation-params", params={"provider": "ollama"})
        assert resp.status_code == 200
        assert resp.json()["model"]

    def test_rejects_unknown_provider(self, client):
        resp = client.get("/api/settings/generation-params", params={"provider": "nope"})
        assert resp.status_code == 422

    def test_put_saves_effort(self, client):
        resp = client.put("/api/settings/", json={"effort": "high"})
        assert resp.status_code == 200
        assert resp.json()["effort"] == "high"
        assert client.get("/api/settings/").json()["effort"] == "high"

    def test_put_rejects_invalid_effort(self, client):
        assert client.put("/api/settings/", json={"effort": "extreme"}).status_code == 422


@pytest.mark.api
class TestBedrockApiKeySetting:
    def _bedrock(self, client):
        return client.get("/api/settings/").json()["providers"]["bedrock"]

    def test_saved_key_is_masked(self, client):
        payload = {"providers": {"bedrock": {"api_key": "bedrock-secret-key-1234"}}}
        assert client.put("/api/settings/", json=payload).status_code == 200
        masked = self._bedrock(client)["api_key_masked"]
        assert masked == "bedr****1234"
        assert "secret" not in masked

    def test_empty_value_keeps_saved_key(self, client):
        client.put("/api/settings/", json={"providers": {"bedrock": {"api_key": "bedrock-secret-key-1234"}}})
        client.put("/api/settings/", json={"providers": {"bedrock": {"api_key": ""}}})
        assert self._bedrock(client)["api_key_masked"]

    def test_clear_removes_saved_key(self, client):
        client.put("/api/settings/", json={"providers": {"bedrock": {"api_key": "bedrock-secret-key-1234"}}})
        client.put("/api/settings/", json={"providers": {"bedrock": {"clear_api_key": True}}})
        assert self._bedrock(client)["api_key_masked"] == ""
