from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingSettings(BaseSettings):
    """Central configuration for the embedding model."""

    model_config = SettingsConfigDict(
        env_prefix="EMBEDDING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str = "text-embedding-3-small"


@lru_cache
def get_embedding_settings() -> EmbeddingSettings:
    """Load and cache embedding configuration."""
    return EmbeddingSettings()
