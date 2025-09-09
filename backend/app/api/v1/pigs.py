from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, UploadFile, File as UploadFileDep
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...deps import get_db, get_current_user
from ...config import settings
from ...models import Pig, WeightRecord
from ...roles import require_role
from ...models.user import UserRole
from ...schemas.pig import PigCreate, PigUpdate, PigOut
from ...schemas.weight import WeightCreate, WeightOut


router = APIRouter(prefix="/pigs", tags=["pigs"], responses={404: {"description": "Not found"}})


@router.post("/", response_model=PigOut, status_code=status.HTTP_201_CREATED)
def create_pig(payload: PigCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.OWNER))):
    pig = Pig(
        ear_tag=payload.ear_tag.strip(),
        sex=payload.sex,
        breed=payload.breed,
        birth_date=payload.birth_date,
        pig_class=payload.pig_class,
        source=payload.source,
        status=payload.status or "active",
        current_pen=payload.current_pen,
        sire_id=payload.sire_id,
        dam_id=payload.dam_id,
    )
    db.add(pig)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate ear_tag")
    db.refresh(pig)
    return pig


@router.get("/", response_model=List[PigOut])
def list_pigs(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search by ear_tag"),
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(active|sold|dead)$"),
    sex: Optional[str] = Query(None, pattern="^(M|F)$"),
    pen: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    response: Response = None,
):
    base = db.query(Pig)
    conditions = []
    if search:
        conditions.append(Pig.ear_tag.ilike(f"%{search}%"))
    if status_filter:
        conditions.append(Pig.status == status_filter)
    if sex:
        conditions.append(Pig.sex == sex)
    if pen:
        conditions.append(Pig.current_pen == pen)
    if conditions:
        base = base.filter(and_(*conditions))
    total = base.count()
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    rows = base.order_by(Pig.created_at.desc()).limit(limit).offset(offset).all()
    return rows


@router.get("/export")
def export_pigs(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    sex: Optional[str] = None,
    pen: Optional[str] = None,
):
    query = db.query(Pig)
    if search:
        query = query.filter(Pig.ear_tag.ilike(f"%{search}%"))
    if status_filter:
        query = query.filter(Pig.status == status_filter)
    if sex:
        query = query.filter(Pig.sex == sex)
    if pen:
        query = query.filter(Pig.current_pen == pen)
    rows = query.order_by(Pig.ear_tag.asc()).all()
    headers = ["id","ear_tag","sex","breed","birth_date","class","source","status","current_pen","sire_id","dam_id"]
    def cell(v):
        if v is None:
            return ""
        return str(v)
    csv_lines = [",".join(headers)]
    for r in rows:
        rec = [
            str(r.id), r.ear_tag or "", r.sex or "", r.breed or "",
            r.birth_date.isoformat() if r.birth_date else "",
            r.pig_class or "",
            r.source or "",
            r.status or "",
            r.current_pen or "",
            str(r.sire_id) if r.sire_id else "",
            str(r.dam_id) if r.dam_id else "",
        ]
        csv_lines.append(",".join([cell(x) for x in rec]))
    content = "\n".join(csv_lines)
    return Response(content=content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=pigs.csv"})


@router.get("/{pig_id}", response_model=PigOut)
def get_pig(pig_id: uuid.UUID, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")
    return pig


@router.patch("/{pig_id}", response_model=PigOut)
def update_pig(
    pig_id: uuid.UUID,
    payload: PigUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.OWNER)),
):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    data = payload.model_dump(exclude_unset=True, by_alias=True)
    # Map alias 'class' to model attribute 'pig_class' already configured via column name
    if "class" in data:
        data["pig_class"] = data.pop("class")
    for key, value in data.items():
        if hasattr(pig, key):
            setattr(pig, key, value)
    db.add(pig)
    db.commit()
    db.refresh(pig)
    return pig


# Weights sub-routes
@router.post("/{pig_id}/weights", response_model=WeightOut, status_code=status.HTTP_201_CREATED)
def add_weight(pig_id: uuid.UUID, payload: WeightCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.WORKER, UserRole.OWNER))):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")
    # Prevent future-dated weights beyond a small grace
    today = date.today()
    grace_days = 2
    if payload.date > today + timedelta(days=grace_days):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="date cannot be in the future")
    record = WeightRecord(pig_id=pig_id, date=payload.date, weight_kg=payload.weight_kg, notes=payload.notes)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{pig_id}/weights", response_model=List[WeightOut])
def list_weights(
    pig_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    query = db.query(WeightRecord).filter(WeightRecord.pig_id == pig_id)
    if from_date:
        query = query.filter(WeightRecord.date >= from_date)
    if to_date:
        query = query.filter(WeightRecord.date <= to_date)
    return query.order_by(WeightRecord.date.asc()).all()


@router.get("/{pig_id}/growth-curve")
def growth_curve(
    pig_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    query = db.query(WeightRecord).filter(WeightRecord.pig_id == pig_id)
    if from_date:
        query = query.filter(WeightRecord.date >= from_date)
    if to_date:
        query = query.filter(WeightRecord.date <= to_date)
    records = query.order_by(WeightRecord.date.asc()).all()
    return [{"date": r.date.isoformat(), "kg": float(r.weight_kg)} for r in records]


@router.delete("/{pig_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pig(pig_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(require_role(UserRole.OWNER))):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")
    db.delete(pig)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{pig_id}/family")
def pig_family(pig_id: uuid.UUID, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")
    sire = db.get(Pig, pig.sire_id) if pig.sire_id else None
    dam = db.get(Pig, pig.dam_id) if pig.dam_id else None
    offspring = db.query(Pig).filter((Pig.sire_id == pig_id) | (Pig.dam_id == pig_id)).order_by(Pig.created_at.asc()).all()
    def serialize(p: Pig | None):
        if not p:
            return None
        return {"id": str(p.id), "ear_tag": p.ear_tag, "sex": p.sex, "class": p.pig_class}
    return {
        "parents": [x for x in [serialize(sire), serialize(dam)] if x],
        "offspring": [serialize(c) for c in offspring],
    }


@router.post("/import")
def import_pigs(file: UploadFile = UploadFileDep(...), db: Session = Depends(get_db), _=Depends(require_role(UserRole.OWNER))):
    """Import minimal CSV for pigs. Expected headers include at least ear_tag; optional: sex,class,birth_date,pen."""
    import csv, io
    content = file.file.read()
    try:
        text = content.decode("utf-8")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file encoding")
    reader = csv.DictReader(io.StringIO(text))
    results: list[dict] = []
    for idx, row in enumerate(reader, start=1):
        ear_tag = (row.get("ear_tag") or "").strip()
        if not ear_tag:
            results.append({"row": idx, "success": False, "message": "ear_tag required"})
            continue
        try:
            payload = PigCreate(
                ear_tag=ear_tag,
                sex=(row.get("sex") or None),
                pig_class=(row.get("class") or None),
                birth_date=(row.get("birth_date") or None),
                current_pen=(row.get("pen") or None),
            )
        except Exception as e:
            results.append({"row": idx, "success": False, "message": str(e)})
            continue
        pig = Pig(
            ear_tag=payload.ear_tag,
            sex=payload.sex,
            pig_class=payload.pig_class,
            birth_date=payload.birth_date,
            current_pen=payload.current_pen,
            status="active",
        )
        db.add(pig)
        try:
            db.commit()
            db.refresh(pig)
            results.append({"row": idx, "success": True, "id": str(pig.id)})
        except IntegrityError:
            db.rollback()
            results.append({"row": idx, "success": False, "message": "Duplicate ear_tag"})
    return {"results": results}

