from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pigs.db")
engine = create_engine(DATABASE_URL, echo=False)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
