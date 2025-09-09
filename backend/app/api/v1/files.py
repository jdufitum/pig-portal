from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File as UploadFileDep, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from ...deps import get_db
from ...models import File, Pig
from ...roles import require_role
from ...models.user import UserRole
from ...services.files import get_s3_client, generate_object_key
from ...config import settings


router = APIRouter(prefix="/files", tags=["files"]) 


@router.post("/pigs/{pig_id}/photo")
def upload_pig_photo(pig_id: uuid.UUID, image: UploadFile = UploadFileDep(...), db: Session = Depends(get_db), _=Depends(require_role(UserRole.WORKER, UserRole.VET, UserRole.OWNER))) -> dict[str, Any]:
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    key = generate_object_key(pig_id, image.filename or "image.jpg")
    s3 = get_s3_client()
    try:
        signed_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": settings.s3_bucket, "Key": key, "ContentType": image.content_type or "application/octet-stream"},
            ExpiresIn=3600,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")

    object_url = f"{settings.s3_endpoint}/{settings.s3_bucket}/{key}" if settings.s3_endpoint else f"s3://{settings.s3_bucket}/{key}"

    record = File(pig_id=pig_id, kind="photo", url=object_url)
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"file": {"id": str(record.id), "url": record.url, "kind": record.kind}, "upload_url": signed_url}


@router.get("/pigs/{pig_id}")
def list_pig_files(pig_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(require_role(UserRole.WORKER, UserRole.VET, UserRole.OWNER))):
    files = db.query(File).filter(File.pig_id == pig_id).order_by(File.created_at.desc()).all()
    return [{"id": str(f.id), "url": f.url, "kind": f.kind, "created_at": f.created_at.isoformat()} for f in files]

