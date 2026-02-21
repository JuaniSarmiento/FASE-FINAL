import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@127.0.0.1:5440/ai_native"
    DB_ECHO: bool = False
    
    # AI Services - Defaults for local development
    # Docker will override these via environment variables in docker-compose.yml
    OLLAMA_BASE_URL: str = "http://187.77.41.214:11434"
    CHROMA_DB_HOST: str = "localhost"
    CHROMA_DB_PORT: int = 8001
    
    # Security
    SECRET_KEY: str = "supersecretkey"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Environment variables take precedence over .env file
        case_sensitive=False
    )

settings = Settings()

# Log configuration on startup (useful for debugging)
print("="*60)
print("📋 CONFIGURATION LOADED")
print("="*60)
print(f"OLLAMA_BASE_URL: {settings.OLLAMA_BASE_URL}")
print(f"CHROMA_DB_HOST: {settings.CHROMA_DB_HOST}")
print(f"CHROMA_DB_PORT: {settings.CHROMA_DB_PORT}")
print(f"DATABASE_URL: {settings.DATABASE_URL[:40]}...")
print("="*60)
