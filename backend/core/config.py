from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_ENV : str = "development"
    SECRET_KEY: str = "change-me"
    
    # Neon PostgreSQL Database URL
    DATABASE_URL: str = "postgresql://neondb_owner:npg_NfA2YQCna5WJ@ep-rough-rice-an00b1uo-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    
    REDIS_HOST: str = "redis"
    REDIS_PORT:int = 6379
    REDIS_URL: str = "redis://redis:6379"

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    OPENAI_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "research-assistant"

    model_config = {"env_file": ".env", "extra": "allow"}

settings = Settings()


