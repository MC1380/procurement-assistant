from pydantic import SecretStr

from procurement_assistant.config.providers import (
    OpenAISettings,
    get_openai_settings,
)


def test_openai_settings_reads_environment_variables(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")

    settings = OpenAISettings(_env_file=None)

    assert settings.api_key == SecretStr("test-api-key")
    assert settings.base_url == "https://example.com/v1"


def test_openai_settings_base_url_is_optional(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)

    settings = OpenAISettings(_env_file=None)

    assert settings.base_url is None


def test_get_openai_settings_returns_cached_instance(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

    get_openai_settings.cache_clear()

    first = get_openai_settings()
    second = get_openai_settings()

    assert first is second

    get_openai_settings.cache_clear()
