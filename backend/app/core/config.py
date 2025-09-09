from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List

# Deprecated in favor of app.config.Settings. Keep a thin shim for backward compatibility
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='', extra='ignore')

    DATABASE_URL: str = ''
    JWT_SECRET: str = ''
    JWT_EXPIRE_MINUTES: int = 0
    S3_ENDPOINT: str | None = None
    S3_BUCKET: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    ALLOWED_ORIGINS: List[str] = ['*']

    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(',') if o.strip()]
        return v

# Expose values from the unified settings if available
try:
    from app.config import settings as unified
    settings = unified
except Exception:  # pragma: no cover
    settings = Settings()
