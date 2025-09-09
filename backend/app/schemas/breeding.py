import uuid
from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class BreedingCreate(BaseModel):
    sow_id: Optional[uuid.UUID] = None
    boar_id: Optional[uuid.UUID] = None
    service_date: Optional[date] = None
    method: str = Field("natural", pattern="^(natural|ai)$")
    expected_farrow: Optional[date] = None
    preg_check_date: Optional[date] = None
    preg_status: str = Field("unknown", pattern="^(pos|neg|unknown)$")
    parity: Optional[int] = None
    pen_at_service: Optional[str] = None
    notes: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sow_id": "00000000-0000-0000-0000-000000000001",
                    "boar_id": "00000000-0000-0000-0000-000000000002",
                    "service_date": "2025-02-01",
                    "method": "ai",
                    "parity": 2,
                    "pen_at_service": "M1"
                }
            ]
        }
    }

    @model_validator(mode="after")
    def validate_dates(self):
        if self.preg_check_date and self.service_date and self.preg_check_date < self.service_date:
            raise ValueError("preg_check_date must be on or after service_date")
        if self.expected_farrow and self.service_date and self.expected_farrow < self.service_date:
            raise ValueError("expected_farrow must be on or after service_date")
        return self


class BreedingUpdate(BaseModel):
    expected_farrow: Optional[date] = None
    preg_check_date: Optional[date] = None
    preg_status: Optional[str] = Field(None, pattern="^(pos|neg|unknown)$")
    parity: Optional[int] = None
    pen_at_service: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_update_dates(self):
        # Cannot fully validate relative to service_date without fetching; keep simple: ensure not impossible combinations
        return self


class BreedingOut(BaseModel):
    id: uuid.UUID
    sow_id: Optional[uuid.UUID] = None
    boar_id: Optional[uuid.UUID] = None
    service_date: Optional[date] = None
    method: str
    expected_farrow: Optional[date] = None
    preg_check_date: Optional[date] = None
    preg_status: str
    parity: Optional[int] = None
    pen_at_service: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

