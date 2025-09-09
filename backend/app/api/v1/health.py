from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get('/healthz')
async def healthz_v1():
    return {"status": "ok"}
