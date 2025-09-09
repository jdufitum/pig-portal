import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str
    due_date: date
    assigned_to: Optional[uuid.UUID] = None
    link_type: Optional[str] = Field(None, pattern="^(pig|litter)$")
    link_id: Optional[uuid.UUID] = None
    priority: str = Field("med", pattern="^(low|med|high)$")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Weigh pig SOW-001",
                    "due_date": "2025-03-05",
                    "link_type": "pig",
                    "priority": "high"
                }
            ]
        }
    }


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[uuid.UUID] = None
    link_type: Optional[str] = Field(None, pattern="^(pig|litter)$")
    link_id: Optional[uuid.UUID] = None
    status: Optional[str] = Field(None, pattern="^(open|done)$")
    priority: Optional[str] = Field(None, pattern="^(low|med|high)$")


class TaskOut(BaseModel):
    id: uuid.UUID
    title: str
    due_date: date
    assigned_to: Optional[uuid.UUID] = None
    link_type: Optional[str] = None
    link_id: Optional[uuid.UUID] = None
    status: str
    priority: str
    created_at: datetime

    class Config:
        from_attributes = True

