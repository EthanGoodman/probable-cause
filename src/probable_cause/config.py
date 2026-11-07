"""Application settings loaded from environment variables (and `.env` if present)."""

from functools import lru_cache
from typing import Literal
from urllib.parse import quote

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings. Each field maps to an upper-case env var (postgres_port -> POSTGRES_PORT)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    postgres_user: str = "probable_cause"
    postgres_password: SecretStr
    postgres_db: str = "probable_cause"
    # 127.0.0.1, not "localhost": on Windows, localhost tries IPv6 (::1) first, and the
    # container only listens on IPv4, so the connection hangs.
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432

    # Embeddings
    openai_api_key: SecretStr | None = None
    embedding_model: str = "text-embedding-3-small"

    # LLM
    llm_provider: Literal["openai", "anthropic"] = "openai"
    llm_model: str | None = None
    anthropic_api_key: SecretStr | None = None

    # Reranker
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    @property
    def database_url(self) -> str:
        """Postgres connection URL for psycopg, with user and password URL-encoded."""
        user = quote(self.postgres_user, safe="")
        password = quote(self.postgres_password.get_secret_value(), safe="")
        return (
            f"postgresql://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return the settings, read from the environment once and then cached."""
    return Settings()
