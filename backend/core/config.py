from loguru import logger
from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "research_assistant"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    JWT_SECRET_KEY: str = "change-me-jwt"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "research-assistant"

    NEXTAUTH_SECRET: str = ""

    model_config = {"env_file": ".env", "extra": "allow"}

    @field_validator("APP_ENV")
    @classmethod
    def valid_env(cls, v: str) -> str:
        if v not in ("development", "staging", "production"):
            raise ValueError(f"APP_ENV must be development|staging|production, got '{v}'")
        return v


def _audit_secrets(s: Settings) -> None:
    """
    Warns loudly at startup if placeholder secrets are still set.
    In production raises immediately — never run with default secrets.
    """
    PLACEHOLDERS = {"change-me", "change-me-jwt", "change-me-yet-another-random-64-char-string"}

    warnings: list[str] = []

    if s.SECRET_KEY in PLACEHOLDERS:
        warnings.append("SECRET_KEY is using a placeholder value")
    if s.JWT_SECRET_KEY in PLACEHOLDERS:
        warnings.append("JWT_SECRET_KEY is using a placeholder value")
    if not s.OPENAI_API_KEY or s.OPENAI_API_KEY.startswith("sk-..."):
        warnings.append("OPENAI_API_KEY is not set")
    if not s.TAVILY_API_KEY or s.TAVILY_API_KEY.startswith("tvly-..."):
        warnings.append("TAVILY_API_KEY is not set")
    if not s.PINECONE_API_KEY or s.PINECONE_API_KEY == "...":
        warnings.append("PINECONE_API_KEY is not set")

    for w in warnings:
        logger.warning("[secrets audit] ⚠  {}", w)

    if warnings and s.APP_ENV == "production":
        raise RuntimeError(
            "Production startup blocked — insecure secrets detected:\n"
            + "\n".join(f"  • {w}" for w in warnings)
        )


settings = Settings()
_audit_secrets(settings)