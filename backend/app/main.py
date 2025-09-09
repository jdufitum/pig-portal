from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging import configure_logging

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
