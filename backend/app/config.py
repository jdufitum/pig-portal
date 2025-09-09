from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, AliasChoices


class Settings(BaseSettings):
    app_name: str = Field(default="Pig Farm Management Portal")
    debug: bool = Field(default=True)

    # Security
    secret_key: str = Field(default="change-me", validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"))
    access_token_expires_minutes: int = Field(default=30)
    refresh_token_expires_days: int = Field(default=7)
    jwt_algorithm: str = Field(default="HS256")

    # Database
    database_url: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/pigfarm", validation_alias=AliasChoices("DATABASE_URL", "DATABASE_URI"))

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"], validation_alias=AliasChoices("CORS_ORIGINS", "ALLOWED_ORIGINS"))

    # Object storage (S3-compatible)
    s3_endpoint: str | None = None
    s3_bucket: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value):
        # Accept comma-separated string or JSON array; default to ["*"] when empty
        if value is None or value == "":
            return ["*"]
        if isinstance(value, str):
            # If looks like JSON list, let pydantic handle later
            if value.strip().startswith("[") and value.strip().endswith("]"):
                return value
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()