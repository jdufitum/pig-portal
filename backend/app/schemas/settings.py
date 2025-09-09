from pydantic import BaseModel


class OwnerSettingsOut(BaseModel):
    app_name: str
    cors_origins: list[str]

    class Config:
        from_attributes = True

