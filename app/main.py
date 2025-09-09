from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.db.session import init_db
from app.api.pigs import router as pigs_router
from app.api.health import router as health_router
from app.api.settings import router as settings_router

app = FastAPI(title="Pig Farm API")
app.include_router(pigs_router)
app.include_router(health_router)
app.include_router(settings_router)

@app.on_event("startup")
def on_startup() -> None:
    init_db()

origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
