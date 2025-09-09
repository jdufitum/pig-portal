from datetime import date
from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    return client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"}).json()


def create_pig(client: TestClient, token: str) -> str:
    resp = client.post("/api/v1/pigs/", json={"ear_tag": "HEALTH-1", "sex": "F"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    return resp.json()["id"]


def test_health_permissions_and_listing(client: TestClient):
    owner = auth(client, "owner@farm.test")
    vet = auth(client, "vet@farm.test")
    worker = auth(client, "worker@farm.test")
    pig_id = create_pig(client, owner["access_token"])

    # Worker create
    r1 = client.post("/api/v1/health/", json={"pig_id": pig_id, "date": date.today().isoformat(), "diagnosis": "Cough", "product": "AB"}, headers={"Authorization": f"Bearer {worker['access_token']}"})
    assert r1.status_code == 201

    # Vet create
    r2 = client.post("/api/v1/health/", json={"pig_id": pig_id, "date": date.today().isoformat(), "diagnosis": "Fever"}, headers={"Authorization": f"Bearer {vet['access_token']}"})
    assert r2.status_code == 201

    # List by pig
    li = client.get("/api/v1/health/", params={"pig_id": pig_id}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert li.status_code == 200 and len(li.json()) >= 2

