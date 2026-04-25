"""
Configuration module — all settings sourced from environment variables.
No hardcoded secrets or hostnames.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str = "mongodb://mongodb:27017"
    MONGO_DB: str = "trading_crm"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
