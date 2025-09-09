from fastapi import FastAPI
from app.db.session import init_db
from app.api.pigs import router as pigs_router

app = FastAPI(title="Pig Farm API")
app.include_router(pigs_router)

@app.on_event("startup")
def on_startup() -> None:
    init_db()
