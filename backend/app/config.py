from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default="Pig Farm Management Portal")
    debug: bool = Field(default=True)

    # Security
    secret_key: str = Field(default="change-me")
    access_token_expires_minutes: int = Field(default=30)
    refresh_token_expires_days: int = Field(default=7)
    jwt_algorithm: str = Field(default="HS256")

    # Database
    database_url: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/pigfarm")

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()