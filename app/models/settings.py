from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field

class OwnerSettings(SQLModel, table=True):
	id: Optional[int] = Field(default=1, primary_key=True)
	farm_name: Optional[str] = None
	timezone: Optional[str] = None
	default_weigh_interval_days: Optional[int] =  Field(default=30)
	default_vaccine_cadence_days: Optional[int] = Field(default=180)
	default_deworm_cadence_days: Optional[int] = Field(default=90)
	sms_gateway_key: Optional[str] = None
	whatsapp_gateway_key: Optional[str] = None