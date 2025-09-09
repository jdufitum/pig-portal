import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from datetime import date as _date


class PigBase(BaseModel):
    ear_tag: str = Field(..., min_length=1)
    sex: Optional[str] = Field(None, pattern="^(M|F)$")
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    pig_class: Optional[str] = Field(None, alias="class", pattern="^(piglet|grower|finisher|sow|boar)$")
    source: Optional[str] = None
    status: Optional[str] = Field("active", pattern="^(active|sold|dead)$")
    current_pen: Optional[str] = Field(None, alias="pen")
    sire_id: Optional[uuid.UUID] = None
    dam_id: Optional[uuid.UUID] = None

    class Config:
        populate_by_name = True

    @field_validator("ear_tag")
    @classmethod
    def normalize_ear_tag(cls, v: str) -> str:
        vv = v.strip()
        if not vv:
            raise ValueError("ear_tag must not be empty")
        return vv

    @field_validator("birth_date")
    @classmethod
    def check_birth_not_future(cls, v: _date | None) -> _date | None:
        if v and v > _date.today():
            raise ValueError("birth_date cannot be in the future")
        return v


class PigCreate(PigBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ear_tag": "SOW-001",
                    "sex": "F",
                    "breed": "Large White",
                    "birth_date": "2025-01-10",
                    "class": "sow",
                    "source": "on-farm",
                    "status": "active",
                    "current_pen": "A1"
                }
            ]
        }
    }


class PigUpdate(BaseModel):
    sex: Optional[str] = Field(None, pattern="^(M|F)$")
    breed: Optional[str] = None
    birth_date: Optional[date] = None
    pig_class: Optional[str] = Field(None, alias="class", pattern="^(piglet|grower|finisher|sow|boar)$")
    source: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|sold|dead)$")
    current_pen: Optional[str] = Field(None, alias="pen")
    sire_id: Optional[uuid.UUID] = None
    dam_id: Optional[uuid.UUID] = None

    class Config:
        populate_by_name = True


class PigOut(PigBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

