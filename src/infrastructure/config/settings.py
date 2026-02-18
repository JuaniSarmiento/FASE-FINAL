import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5440/ai_native")
    DB_ECHO: bool = False
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    CHROMA_DB_HOST: str = "chroma"
    CHROMA_DB_PORT: int = 8000
    SECRET_KEY: str = "supersecretkey" # TODO: Move to .env for production
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
