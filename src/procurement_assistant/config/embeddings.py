from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic_settings import BaseSettings, SettingsConfigDict

from procurement_assistant.config.providers import get_openai_settings


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


def get_embedding_model() -> Embeddings:
    """Create an OpenAI embedding model using centralized settings."""

    embedding_settings = get_embedding_settings()
    openai_settings = get_openai_settings()

    return OpenAIEmbeddings(
        model=embedding_settings.model,
        api_key=openai_settings.api_key.get_secret_value(),
        base_url=openai_settings.base_url,
    )
