from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    APP_ENV: str = "development"
    MAX_UPLOAD_SIZE_MB: int = 5
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    SKILLS_DB_PATH: str = "app/data/skills_db.json"
    UPLOADS_DIR: str = "uploads"
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
