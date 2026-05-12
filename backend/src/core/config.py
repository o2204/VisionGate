from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


_base_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore"
)

class Settings(BaseSettings):
    DATABASE_URL: str

    SUPABASE_URL: str
    SUPABASE_KEY: str 

    JWT_SECRET: str 
    JWT_ALGORITHM: str 

    REDIS_HOST: str
    REDIS_PORT: int

    APP_NAME: str = "VisionGate"
    APP_DOMAIN: str = "localhost:8000"
    
    model_config = _base_config

class NotificationSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    TWILIO_SID: str 
    TWILIO_AUTH_TOKEN: str
    TWILIO_NUMBER: str
    
    model_config = _base_config


@lru_cache
def get_settings():
    return Settings()

@lru_cache
def get_notification_settings():
    return NotificationSettings()

settings = get_settings()
notification_settings = get_notification_settings()
