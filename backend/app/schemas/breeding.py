import uuid
from datetime import date, timedelta
from typing import Optional

from pydantic import BaseModel, Field


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


class BreedingUpdate(BaseModel):
    expected_farrow: Optional[date] = None
    preg_check_date: Optional[date] = None
    preg_status: Optional[str] = Field(None, pattern="^(pos|neg|unknown)$")
    parity: Optional[int] = None
    pen_at_service: Optional[str] = None
    notes: Optional[str] = None


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

