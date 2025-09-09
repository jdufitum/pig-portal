from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.db.session import get_session
from app.models.settings import OwnerSettings

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/", response_model=OwnerSettings)
def get_settings(session: Session = Depends(get_session)) -> OwnerSettings:
	settings = session.get(OwnerSettings, 1)
	if settings is None:
		settings = OwnerSettings()
		session.add(settings)
		session.commit()
		session.refresh(settings)
	return settings

@router.post("/", response_model=OwnerSettings)
@router.put("/", response_model=OwnerSettings)
def upsert_settings(payload: OwnerSettings, session: Session = Depends(get_session)) -> OwnerSettings:
	settings = session.get(OwnerSettings, 1)
	if settings is None:
		settings = OwnerSettings()
	for field, value in payload.model_dump(exclude_unset=True).items():
		setattr(settings, field, value)
	session.add(settings)
	session.commit()
	session.refresh(settings)
	return settings