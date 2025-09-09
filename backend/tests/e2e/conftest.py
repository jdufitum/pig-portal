import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db import SessionLocal
from app.models import User, UserRole
from app.security import hash_password


def seed_users(db: Session) -> None:
    for email, role in [
        ("owner@farm.test", UserRole.OWNER),
        ("vet@farm.test", UserRole.VET),
        ("worker@farm.test", UserRole.WORKER),
    ]:
        if not db.query(User).filter(User.email == email).first():
            db.add(User(email=email, name=email.split("@")[0].title(), role=role, password_hash=hash_password("Passw0rd!")))
    db.commit()


@pytest.fixture(scope="session", autouse=True)
def _ensure_seed():
    # Use the running database configured for the backend container.
    # Assumes docker compose has already applied migrations.
    try:
        with SessionLocal() as db:
            seed_users(db)
    except Exception as e:
        # If DB not ready, let tests fail with connection error for visibility
        raise
    yield


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def login(client: TestClient, email: str, password: str) -> dict:
    data = {"username": email, "password": password}
    resp = client.post("/api/v1/auth/login", data=data)
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    return {"access": payload["access_token"], "refresh": payload["refresh_token"]}

