import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class WeightCreate(BaseModel):
    date: date
    weight_kg: Decimal = Field(..., gt=0)
    notes: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"date": "2025-03-01", "weight_kg": 25.5, "notes": "Post-weaning"}
            ]
        }
    }

    @field_validator("weight_kg")
    @classmethod
    def validate_positive_weight(cls, v: Decimal) -> Decimal:
        if v is None or v <= 0:
            raise ValueError("weight_kg must be > 0")
        return v


class WeightOut(BaseModel):
    id: uuid.UUID
    pig_id: uuid.UUID
    date: date
    weight_kg: Decimal
    notes: str | None = None

    class Config:
        from_attributes = True

