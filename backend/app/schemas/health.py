import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class HealthEventCreate(BaseModel):
    pig_id: Optional[uuid.UUID] = None
    pen: Optional[str] = None
    date: date
    diagnosis: Optional[str] = None
    product: Optional[str] = None
    dose: Optional[str] = None
    route: Optional[str] = None
    vet_name: Optional[str] = None
    notes: Optional[str] = None
    cost: Optional[Decimal] = Field(None, ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "pig_id": "00000000-0000-0000-0000-000000000010",
                    "date": "2025-03-15",
                    "diagnosis": "Coughing",
                    "product": "Oxytet",
                    "dose": "5 ml",
                    "route": "IM",
                    "vet_name": "Dr. Vet",
                    "notes": "Follow-up in 3 days",
                    "cost": 12.5
                }
            ]
        }
    }


class HealthEventOut(BaseModel):
    id: uuid.UUID
    pig_id: Optional[uuid.UUID] = None
    pen: Optional[str] = None
    date: date
    diagnosis: Optional[str] = None
    product: Optional[str] = None
    dose: Optional[str] = None
    route: Optional[str] = None
    vet_name: Optional[str] = None
    notes: Optional[str] = None
    cost: Optional[Decimal] = None

    class Config:
        from_attributes = True

