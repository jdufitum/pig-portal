from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Sex(str, Enum):
    MALE = "male"
    FEMALE = "female"

class PigStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    DEAD = "dead"

class Pen(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    location: Optional[str] = None

    pigs: List["Pig"] = Relationship(back_populates="pen")

class Litter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    farrowing_date: Optional[date] = None
    wean_date: Optional[date] = None
    sow_id: Optional[int] = Field(default=None, foreign_key="pig.id")
    boar_id: Optional[int] = Field(default=None, foreign_key="pig.id")
    service_date: Optional[date] = None
    expected_farrow_date: Optional[date] = None

    piglets: List["Pig"] = Relationship(back_populates="litter")

class Pig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ear_tag: str = Field(index=True, unique=True, nullable=False)
    name: Optional[str] = Field(default=None, index=True)
    sex: Sex
    breed: Optional[str] = None
    birth_date: Optional[date] = None

    status: PigStatus = Field(default=PigStatus.ACTIVE, index=True)

    pen_id: Optional[int] = Field(default=None, foreign_key="pen.id")
    pen: Optional[Pen] = Relationship(back_populates="pigs")

    sire_id: Optional[int] = Field(default=None, foreign_key="pig.id")
    dam_id: Optional[int] = Field(default=None, foreign_key="pig.id")

    litter_id: Optional[int] = Field(default=None, foreign_key="litter.id")
    litter: Optional[Litter] = Relationship(back_populates="piglets")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Movement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pig_id: int = Field(foreign_key="pig.id", index=True)
    from_pen_id: Optional[int] = Field(default=None, foreign_key="pen.id")
    to_pen_id: Optional[int] = Field(default=None, foreign_key="pen.id")
    moved_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class WeightRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pig_id: int = Field(foreign_key="pig.id", index=True)
    recorded_on: date = Field(index=True)
    weight_kg: float

class SaleEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pig_id: int = Field(foreign_key="pig.id", index=True)
    buyer: Optional[str] = None
    sale_date: date
    price: float
    weight_kg: Optional[float] = None

class DeathEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pig_id: int = Field(foreign_key="pig.id", index=True)
    death_date: date
    cause: Optional[str] = None
    pen_id: Optional[int] = Field(default=None, foreign_key="pen.id")
