from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='', extra='ignore')

    DATABASE_URL: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres'
    JWT_SECRET: str = 'change-me'
    JWT_EXPIRE_MINUTES: int = 60 * 24
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

settings = Settings()
