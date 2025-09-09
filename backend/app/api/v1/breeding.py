from __future__ import annotations

from datetime import date
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...deps import get_db
from ...models import BreedingEvent, Litter, Pig
from ...roles import require_role
from ...models.user import UserRole
from ...schemas.breeding import BreedingCreate, BreedingUpdate, BreedingOut
from ...schemas.litter import LitterCreate, LitterUpdate, LitterOut
from ...services.breeding import compute_expected_farrow


router = APIRouter(prefix="/breeding", tags=["breeding"])


@router.post("/", response_model=BreedingOut, status_code=status.HTTP_201_CREATED)
def create_service(payload: BreedingCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.OWNER, UserRole.WORKER))):
    expected = compute_expected_farrow(payload.service_date, payload.expected_farrow)
    event = BreedingEvent(
        sow_id=payload.sow_id,
        boar_id=payload.boar_id,
        service_date=payload.service_date,
        method=payload.method,
        expected_farrow=expected,
        preg_check_date=payload.preg_check_date,
        preg_status=payload.preg_status,
        parity=payload.parity,
        pen_at_service=payload.pen_at_service,
        notes=payload.notes,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=List[BreedingOut])
def list_services(
    db: Session = Depends(get_db),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    preg_status: Optional[str] = Query(None, pattern="^(pos|neg|unknown)$"),
):
    q = db.query(BreedingEvent)
    if from_date:
        q = q.filter(BreedingEvent.service_date >= from_date)
    if to_date:
        q = q.filter(BreedingEvent.service_date <= to_date)
    if preg_status:
        q = q.filter(BreedingEvent.preg_status == preg_status)
    return q.order_by(BreedingEvent.service_date.desc()).all()


@router.get("/upcoming-farrowings")
def upcoming_farrowings(
    db: Session = Depends(get_db),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    q = db.query(BreedingEvent)
    if from_date:
        q = q.filter(BreedingEvent.expected_farrow >= from_date)
    if to_date:
        q = q.filter(BreedingEvent.expected_farrow <= to_date)
    events = q.order_by(BreedingEvent.expected_farrow.asc()).all()

    arr = []
    for e in events:
        sow = db.get(Pig, e.sow_id) if e.sow_id else None
        arr.append({
            "sow": (sow.ear_tag if sow else None),
            "expected_farrow": (e.expected_farrow.isoformat() if e.expected_farrow else None),
            "parity": e.parity,
            "pen": e.pen_at_service,
        })
    return arr


litters_router = APIRouter(prefix="/litters", tags=["litters"])


@litters_router.post("/", response_model=LitterOut, status_code=status.HTTP_201_CREATED)
def create_litter(payload: LitterCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.OWNER, UserRole.WORKER))):
    # Pydantic validator ensures wean_date >= farrow_date when both provided
    litter = Litter(
        sow_id=payload.sow_id,
        boar_id=payload.boar_id,
        farrow_date=payload.farrow_date,
        liveborn=payload.liveborn,
        stillborn=payload.stillborn,
        neonatal_deaths=payload.neonatal_deaths or 0,
        wean_date=payload.wean_date,
    )
    db.add(litter)
    db.commit()
    db.refresh(litter)
    return litter


@litters_router.patch("/{litter_id}", response_model=LitterOut)
def update_litter(litter_id: uuid.UUID, payload: LitterUpdate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.OWNER, UserRole.WORKER))):
    litter = db.get(Litter, litter_id)
    if not litter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Litter not found")

    data = payload.model_dump(exclude_unset=True)
    if "wean_date" in data and litter.farrow_date and data["wean_date"] and data["wean_date"] < litter.farrow_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="wean_date must be on or after farrow_date")
    for k, v in data.items():
        setattr(litter, k, v)
    db.add(litter)
    db.commit()
    db.refresh(litter)
    return litter


@litters_router.get("/", response_model=List[LitterOut])
def list_litters(db: Session = Depends(get_db), from_date: Optional[date] = Query(None, alias="from"), to_date: Optional[date] = Query(None, alias="to")):
    q = db.query(Litter)
    if from_date:
        q = q.filter(Litter.farrow_date >= from_date)
    if to_date:
        q = q.filter(Litter.farrow_date <= to_date)
    return q.order_by(Litter.farrow_date.desc().nullslast()).all()

