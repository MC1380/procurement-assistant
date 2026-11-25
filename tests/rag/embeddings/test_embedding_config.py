from procurement_assistant.config.embeddings import (
    EmbeddingSettings,
    get_embedding_settings,
)


def test_embedding_settings_uses_default_model():
    settings = EmbeddingSettings(_env_file=None)

    assert settings.model == "text-embedding-3-small"


def test_embedding_settings_reads_environment_variable(monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL", "custom-embedding-model")

    settings = EmbeddingSettings(_env_file=None)

    assert settings.model == "custom-embedding-model"


def test_get_embedding_settings_returns_cached_instance():
    get_embedding_settings.cache_clear()

    first = get_embedding_settings()
    second = get_embedding_settings()

    assert first is second

    get_embedding_settings.cache_clear()
