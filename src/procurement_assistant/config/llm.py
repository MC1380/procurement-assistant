from functools import lru_cache

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Central configuration for the language model."""

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str
    api_key: SecretStr
    base_url: str | None = None


@lru_cache
def get_llm_settings() -> LLMSettings:
    """Load and cache LLM configuration."""
    return LLMSettings()


def get_chat_model() -> ChatOpenAI:
    """Create a ChatOpenAI instance using centralized settings."""

    settings = get_llm_settings()

    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url,
    )
