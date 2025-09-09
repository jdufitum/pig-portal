from __future__ import annotations
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import select
from sqlmodel import Session, SQLModel
import io
import csv

from app.db.session import get_session
from app.models.pig import Pig, Pen, WeightRecord, Movement, Litter, Sex, PigStatus

router = APIRouter(prefix="/pigs", tags=["pigs"])

@router.post("/", response_model=Pig)
def register_pig(pig: Pig, session: Session = Depends(get_session)) -> Pig:
    existing = session.exec(select(Pig).where(Pig.ear_tag == pig.ear_tag)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ear tag already exists")
    session.add(pig)
    session.commit()
    session.refresh(pig)
    return pig

class BulkPigletRequest(Litter, table=False):  # pydantic model for request
    piglet_count: int
    sex: Sex
    breed: Optional[str] = None

@router.post("/bulk_piglets", response_model=List[Pig])
def bulk_register_piglets(req: BulkPigletRequest, session: Session = Depends(get_session)) -> List[Pig]:
    # ensure litter exists or create
    litter = session.exec(select(Litter).where(Litter.code == req.code)).first()
    if litter is None:
        litter = Litter(code=req.code, farrowing_date=req.farrowing_date, sow_id=req.sow_id, boar_id=req.boar_id)
        session.add(litter)
        session.flush()
    created: List[Pig] = []
    for i in range(req.piglet_count):
        ear_tag = f"{req.code}-{i+1}"
        if session.exec(select(Pig).where(Pig.ear_tag == ear_tag)).first():
            raise HTTPException(status_code=400, detail=f"Ear tag already exists: {ear_tag}")
        pig = Pig(
            ear_tag=ear_tag,
            sex=req.sex,
            breed=req.breed,
            birth_date=req.farrowing_date,
            litter_id=litter.id,
            sire_id=req.boar_id,
            dam_id=req.sow_id,
        )
        session.add(pig)
        created.append(pig)
    session.commit()
    for p in created:
        session.refresh(p)
    return created

class AssignPenRequest(SQLModel, table=False):
    pig_id: int
    to_pen_name: str

@router.post("/assign_pen", response_model=Pig)
def assign_pen(req: AssignPenRequest, session: Session = Depends(get_session)) -> Pig:
    pig = session.get(Pig, req.pig_id)
    if pig is None:
        raise HTTPException(status_code=404, detail="Pig not found")
    to_pen = session.exec(select(Pen).where(Pen.name == req.to_pen_name)).first()
    if to_pen is None:
        to_pen = Pen(name=req.to_pen_name)
        session.add(to_pen)
        session.flush()
    movement = Movement(pig_id=pig.id, from_pen_id=pig.pen_id, to_pen_id=to_pen.id)
    pig.pen_id = to_pen.id
    session.add(movement)
    session.add(pig)
    session.commit()
    session.refresh(pig)
    return pig

class WeightIn(SQLModel, table=False):
    pig_id: int
    recorded_on: date
    weight_kg: float

@router.post("/weights", response_model=WeightRecord)
def add_weight(record: WeightIn, session: Session = Depends(get_session)) -> WeightRecord:
    pig = session.get(Pig, record.pig_id)
    if pig is None:
        raise HTTPException(status_code=404, detail="Pig not found")
    wr = WeightRecord(pig_id=record.pig_id, recorded_on=record.recorded_on, weight_kg=record.weight_kg)
    session.add(wr)
    session.commit()
    session.refresh(wr)
    return wr

class StatusUpdateIn(SQLModel, table=False):
    pig_id: int
    status: PigStatus

@router.post("/status", response_model=Pig)
def update_status(req: StatusUpdateIn, session: Session = Depends(get_session)) -> Pig:
    pig = session.get(Pig, req.pig_id)
    if pig is None:
        raise HTTPException(status_code=404, detail="Pig not found")
    pig.status = req.status
    session.add(pig)
    session.commit()
    session.refresh(pig)
    return pig

class SaleIn(SQLModel, table=False):
    pig_id: int
    buyer: Optional[str] = None
    sale_date: date
    price: float
    weight_kg: Optional[float] = None

@router.post("/sale", response_model=Pig)
def record_sale(req: SaleIn, session: Session = Depends(get_session)) -> Pig:
    from app.models.pig import SaleEvent
    pig = session.get(Pig, req.pig_id)
    if pig is None:
        raise HTTPException(status_code=404, detail="Pig not found")
    sale = SaleEvent(
        pig_id=pig.id,
        buyer=req.buyer,
        sale_date=req.sale_date,
        price=req.price,
        weight_kg=req.weight_kg,
    )
    pig.status = PigStatus.SOLD
    session.add_all([sale, pig])
    session.commit()
    session.refresh(pig)
    return pig

class DeathIn(SQLModel, table=False):
    pig_id: int
    death_date: date
    cause: Optional[str] = None

@router.post("/death", response_model=Pig)
def record_death(req: DeathIn, session: Session = Depends(get_session)) -> Pig:
    from app.models.pig import DeathEvent
    pig = session.get(Pig, req.pig_id)
    if pig is None:
        raise HTTPException(status_code=404, detail="Pig not found")
    death = DeathEvent(
        pig_id=pig.id,
        death_date=req.death_date,
        cause=req.cause,
        pen_id=pig.pen_id,
    )
    pig.status = PigStatus.DEAD
    session.add_all([death, pig])
    session.commit()
    session.refresh(pig)
    return pig

@router.get("/", response_model=List[Pig])
def list_pigs(
    session: Session = Depends(get_session),
    q: Optional[str] = Query(default=None, description="Search in ear_tag or name"),
    status: Optional[PigStatus] = None,
    sex: Optional[Sex] = None,
    breed: Optional[str] = None,
    pen_name: Optional[str] = None,
) -> List[Pig]:
    stmt = select(Pig)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Pig.ear_tag.ilike(like)) | (Pig.name.ilike(like)))
    if status:
        stmt = stmt.where(Pig.status == status)
    if sex:
        stmt = stmt.where(Pig.sex == sex)
    if breed:
        stmt = stmt.where(Pig.breed == breed)
    if pen_name:
        sub = select(Pen.id).where(Pen.name == pen_name)
        stmt = stmt.where(Pig.pen_id.in_(sub))
    pigs = session.exec(stmt).all()
    return pigs

@router.get("/pen/{pen}", response_model=List[Pig])
def pigs_in_pen(pen: str, session: Session = Depends(get_session)) -> List[Pig]:
    pen_obj = session.exec(select(Pen).where(Pen.name == pen)).first()
    if pen_obj is None:
        return []
    pigs = session.exec(select(Pig).where(Pig.pen_id == pen_obj.id)).all()
    return pigs

@router.get("/export", response_class=StreamingResponse)
def export_pigs_csv(session: Session = Depends(get_session)):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "id",
        "ear_tag",
        "name",
        "sex",
        "breed",
        "birth_date",
        "status",
        "pen",
        "sire_id",
        "dam_id",
        "litter_id",
        "created_at",
        "updated_at",
    ])
    for pig in session.exec(select(Pig)).all():
        pen_name = None
        if pig.pen_id:
            pen_obj = session.get(Pen, pig.pen_id)
            pen_name = pen_obj.name if pen_obj else None
        writer.writerow([
            pig.id,
            pig.ear_tag,
            pig.name,
            pig.sex,
            pig.breed,
            pig.birth_date,
            pig.status,
            pen_name,
            pig.sire_id,
            pig.dam_id,
            pig.litter_id,
            pig.created_at,
            pig.updated_at,
        ])
    out.seek(0)
    return StreamingResponse(iter([out.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=pigs.csv"})

# -------- Batch Operations --------
class BulkAssignPenIn(SQLModel, table=False):
    pig_ids: List[int]
    to_pen_name: str

@router.post("/bulk_assign_pen", response_model=List[Pig])
def bulk_assign_pen(req: BulkAssignPenIn, session: Session = Depends(get_session)) -> List[Pig]:
    to_pen = session.exec(select(Pen).where(Pen.name == req.to_pen_name)).first()
    if to_pen is None:
        to_pen = Pen(name=req.to_pen_name)
        session.add(to_pen)
        session.flush()
    updated: List[Pig] = []
    for pid in req.pig_ids:
        pig = session.get(Pig, pid)
        if pig is None:
            continue
        movement = Movement(pig_id=pig.id, from_pen_id=pig.pen_id, to_pen_id=to_pen.id)
        pig.pen_id = to_pen.id
        session.add_all([movement, pig])
        updated.append(pig)
    session.commit()
    for p in updated:
        session.refresh(p)
    return updated

class BulkWeightIn(SQLModel, table=False):
    records: List[WeightIn]

@router.post("/bulk_weights", response_model=List[WeightRecord])
def bulk_weights(req: BulkWeightIn, session: Session = Depends(get_session)) -> List[WeightRecord]:
    inserted: List[WeightRecord] = []
    for r in req.records:
        pig = session.get(Pig, r.pig_id)
        if pig is None:
            continue
        wr = WeightRecord(pig_id=r.pig_id, recorded_on=r.recorded_on, weight_kg=r.weight_kg)
        session.add(wr)
        inserted.append(wr)
    session.commit()
    for w in inserted:
        session.refresh(w)
    return inserted

# -------- Family Tree --------
@router.get("/{pig_id}/family")
def family_tree(pig_id: int, session: Session = Depends(get_session)):
    pig = session.get(Pig, pig_id)
    if pig is None:
        raise HTTPException(status_code=404, detail="Pig not found")
    parents: List[Pig] = []
    if pig.sire_id:
        sire = session.get(Pig, pig.sire_id)
        if sire:
            parents.append(sire)
    if pig.dam_id:
        dam = session.get(Pig, pig.dam_id)
        if dam:
            parents.append(dam)
    siblings = []
    if pig.litter_id:
        siblings = session.exec(select(Pig).where((Pig.litter_id == pig.litter_id) & (Pig.id != pig.id))).all()
    offspring = session.exec(select(Pig).where((Pig.sire_id == pig.id) | (Pig.dam_id == pig.id))).all()
    return {
        "pig": pig,
        "parents": parents,
        "siblings": siblings,
        "offspring": offspring,
    }
