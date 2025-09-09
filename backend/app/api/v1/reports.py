from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...deps import get_db
from ...models import WeightRecord, BreedingEvent, Litter


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/adg")
def adg(pig_id: uuid.UUID, db: Session = Depends(get_db), from_date: Optional[date] = Query(None, alias="from"), to_date: Optional[date] = Query(None, alias="to")):
    q = db.query(WeightRecord).filter(WeightRecord.pig_id == pig_id)
    if from_date:
        q = q.filter(WeightRecord.date >= from_date)
    if to_date:
        q = q.filter(WeightRecord.date <= to_date)
    records = q.order_by(WeightRecord.date.asc()).all()
    if len(records) < 2:
        return {"days": 0, "start_kg": None, "end_kg": None, "adg_kg_per_day": None}
    start = records[0]
    end = records[-1]
    days = (end.date - start.date).days or 1
    start_kg = Decimal(str(start.weight_kg))
    end_kg = Decimal(str(end.weight_kg))
    adg = (end_kg - start_kg) / Decimal(days)
    return {"days": days, "start_kg": float(start_kg), "end_kg": float(end_kg), "adg_kg_per_day": float(adg)}


@router.get("/farrowing-rate")
def farrowing_rate(db: Session = Depends(get_db), from_date: Optional[date] = Query(None, alias="from"), to_date: Optional[date] = Query(None, alias="to")):
    sq = db.query(BreedingEvent)
    if from_date:
        sq = sq.filter(BreedingEvent.service_date >= from_date)
    if to_date:
        sq = sq.filter(BreedingEvent.service_date <= to_date)
    services = sq.count()

    lq = db.query(Litter)
    if from_date:
        lq = lq.filter(Litter.farrow_date >= from_date)
    if to_date:
        lq = lq.filter(Litter.farrow_date <= to_date)
    farrowings = lq.count()
    rate = (farrowings / services) if services else 0.0
    return {"services": services, "farrowings": farrowings, "rate": rate}


@router.get("/fcr")
def fcr(pig_id: Optional[uuid.UUID] = None, pen_id: Optional[str] = Query(None, alias="pen_id"), from_date: Optional[date] = Query(None, alias="from"), to_date: Optional[date] = Query(None, alias="to")):
    return {"feed_kg": 0.0, "gain_kg": 0.0, "fcr": None}

