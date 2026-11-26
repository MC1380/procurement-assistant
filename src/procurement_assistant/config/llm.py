from functools import lru_cache

from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict

from procurement_assistant.config.providers import get_openai_settings


class LLMSettings(BaseSettings):
    """Configuration specific to the language model."""

    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model: str


@lru_cache
def get_llm_settings() -> LLMSettings:
    """Load and cache language model configuration."""
    return LLMSettings()


def get_chat_model() -> ChatOpenAI:
    """Create a ChatOpenAI instance using centralized settings."""

    llm_settings = get_llm_settings()
    openai_settings = get_openai_settings()

    return ChatOpenAI(
        model=llm_settings.model,
        api_key=openai_settings.api_key.get_secret_value(),
        base_url=openai_settings.base_url,
    )
