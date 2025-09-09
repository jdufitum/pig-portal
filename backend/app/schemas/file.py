import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FileCreate(BaseModel):
    kind: str = Field(..., pattern="^(photo|doc)$")
    url: str


class FileOut(BaseModel):
    id: uuid.UUID
    pig_id: uuid.UUID | None
    kind: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True

