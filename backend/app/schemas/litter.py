import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LitterCreate(BaseModel):
    sow_id: Optional[uuid.UUID] = None
    boar_id: Optional[uuid.UUID] = None
    farrow_date: Optional[date] = None
    liveborn: Optional[int] = Field(None, ge=0)
    stillborn: Optional[int] = Field(None, ge=0)
    neonatal_deaths: Optional[int] = Field(0, ge=0)
    wean_date: Optional[date] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sow_id": "00000000-0000-0000-0000-000000000001",
                    "boar_id": "00000000-0000-0000-0000-000000000002",
                    "farrow_date": "2025-05-20",
                    "liveborn": 12,
                    "stillborn": 1,
                    "neonatal_deaths": 0
                }
            ]
        }
    }

    @model_validator(mode="after")
    def validate_wean_after_farrow(self):
        if self.wean_date is not None and self.farrow_date is not None and self.wean_date < self.farrow_date:
            raise ValueError("wean_date must be on or after farrow_date")
        return self


class LitterUpdate(BaseModel):
    wean_date: Optional[date] = None


class LitterOut(BaseModel):
    id: uuid.UUID
    sow_id: Optional[uuid.UUID] = None
    boar_id: Optional[uuid.UUID] = None
    farrow_date: Optional[date] = None
    liveborn: Optional[int] = None
    stillborn: Optional[int] = None
    neonatal_deaths: int
    wean_date: Optional[date] = None

    class Config:
        from_attributes = True

