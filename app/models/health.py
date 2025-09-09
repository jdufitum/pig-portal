from __future__ import annotations
from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

class HealthEvent(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	pig_id: int = Field(foreign_key="pig.id", index=True)
	date: date
	type: str
	description: Optional[str] = None
	cost: Optional[float] = None