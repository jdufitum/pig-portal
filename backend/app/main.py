from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import configure_logging
import os

from .deps import get_current_user
from .routers.auth import router as auth_router
from .db import SessionLocal
from .models.user import User, UserRole
from .security import hash_password

app = FastAPI(title="Pig Farm API", openapi_url="/api/openapi.json", docs_url="/api/docs")

# Configure logging
configure_logging()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/healthz')
async def healthz():
    return {"status": "ok"}

# Mount API routers placeholder
from .api.v1.health import router as health_router
app.include_router(health_router, prefix="/api/v1")

# Auth routes
app.include_router(auth_router, prefix="/api/v1")


@app.get('/api/v1/ping-protected')
def ping_protected(current_user: User = Depends(get_current_user)):
    return {"status": "ok"}


@app.on_event("startup")
def bootstrap_owner() -> None:
    owner_email = os.getenv("OWNER_EMAIL")
    owner_password = os.getenv("OWNER_PASSWORD")
    if not owner_email or not owner_password:
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == owner_email.lower()).first()
        if existing:
            return
        user = User(
            email=owner_email.lower(),
            full_name="Owner",
            role=UserRole.OWNER,
            password_hash=hash_password(owner_password),
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
