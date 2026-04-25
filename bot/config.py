"""
Bot configuration sourced entirely from environment variables.
"""
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    BOT_TOKEN: str
    BACKEND_URL: str = "http://backend:8000"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = BotSettings()
