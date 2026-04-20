from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import List

class Settings(BaseSettings):
    APP_ENV : str = "development"
    SECRET_KEY: str = "change-me"

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "research_assistant"
    POSTGRES_USER : str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER} : {self.POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST} : {self.POSTGRES_PORT} / {self.POSTGRES_DB}"
        )
    
    REDIS_HOST: str = "redis"
    REDIS_PORT:int = 6379

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST} : {self.REDIS_PORT}"

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES = 1440

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "research-assistant"

    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()


