from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENV: str = "dev"
    DATABASE_URL: str = "postgresql+asyncpg://labops:labops@localhost:5432/labops"
    JWT_SECRET: str = "change-me-access"
    JWT_REFRESH_SECRET: str = "change-me-refresh"
    JWT_ACCESS_MINUTES: int = 15
    JWT_REFRESH_DAYS: int = 7
    STORAGE_PATH: str = "./storage"
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    APP_BASE_URL: str = "http://localhost:5173"
    TIMEZONE: str = "Asia/Jakarta"
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    BACKUP_RETENTION_DAYS: int = 30

settings = Settings()