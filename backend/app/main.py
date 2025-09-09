from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .core.logging import configure_logging
from .api.errors import register_error_handlers
import os

from .deps import get_current_user
from .routers.auth import router as auth_router
from .db import SessionLocal
from .models.user import User, UserRole
from .security import hash_password

tags_metadata = [
    {"name": "auth", "description": "Authentication and token management"},
    {"name": "Health", "description": "API health checks"},
    {"name": "pigs", "description": "Pig records, weights, and growth curves"},
    {"name": "breeding", "description": "Services and upcoming farrowings"},
    {"name": "litters", "description": "Farrowing and weaning records"},
    {"name": "health", "description": "Treatments and illness records"},
    {"name": "files", "description": "File uploads and media"},
    {"name": "tasks", "description": "Tasks and dashboard summaries"},
    {"name": "reports", "description": "Production KPIs and reports"},
]

app = FastAPI(title="Pig Farm API", openapi_url="/api/openapi.json", docs_url="/api/docs", openapi_tags=tags_metadata)

# Configure logging
configure_logging()
register_error_handlers(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/healthz')
async def healthz():
    return {"status": "ok"}

# Mount API routers placeholder
from .api.v1.health import router as health_router
from .api.v1.pigs import router as pigs_router
from .api.v1.breeding import router as breeding_router, litters_router
from .api.v1.health_events import router as health_events_router
from .api.v1.files import router as files_router
from .api.v1.tasks import router as tasks_router
from .api.v1.reports import router as reports_router
from .api.v1.settings import router as settings_router
app.include_router(health_router, prefix="/api/v1")
app.include_router(pigs_router, prefix="/api/v1")
app.include_router(breeding_router, prefix="/api/v1")
app.include_router(litters_router, prefix="/api/v1")
app.include_router(health_events_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")

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
        user = User(email=owner_email.lower(), name="Owner", role=UserRole.OWNER, password_hash=hash_password(owner_password))
        db.add(user)
        db.commit()
    finally:
        db.close()
