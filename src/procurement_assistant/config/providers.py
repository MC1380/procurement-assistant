from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISettings(BaseSettings):
    """Configuration for connecting to OpenAI services."""

    model_config = SettingsConfigDict(
        env_prefix="OPENAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: SecretStr
    base_url: str | None = None


@lru_cache
def get_openai_settings() -> OpenAISettings:
    """Load and cache OpenAI configuration."""
    return OpenAISettings()
