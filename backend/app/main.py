from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth
from . import __version__

app = FastAPI(title=settings.app_name, debug=settings.debug, version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/")
def root():
    return {"app": settings.app_name, "version": __version__}


@app.get("/health")
def health_check():
    return {"status": "ok"}