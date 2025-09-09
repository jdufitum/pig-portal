from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.models.health import HealthEvent
from app.models.pig import Pig, PigStatus

router = APIRouter(prefix="/health", tags=["health"])

@router.post("/", response_model=HealthEvent)
def create_health_event(event: HealthEvent, session: Session = Depends(get_session)) -> HealthEvent:
	pig = session.get(Pig, event.pig_id)
	if pig is None:
		raise HTTPException(status_code=404, detail="Pig not found for health event")
	if pig.status != PigStatus.ACTIVE:
		raise HTTPException(status_code=400, detail="Health events can only be recorded for active pigs")
	session.add(event)
	session.commit()
	session.refresh(event)
	return event