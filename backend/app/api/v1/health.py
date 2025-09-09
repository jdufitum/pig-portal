from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get('/healthz')
async def healthz_v1():
    return {"status": "ok"}

@router.get('/ping')
async def ping_v1():
    return {"ping": "pong"}
