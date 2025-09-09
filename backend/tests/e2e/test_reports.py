from datetime import date, timedelta
from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    return client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"}).json()


def create_pig(client: TestClient, token: str, ear: str) -> str:
    resp = client.post("/api/v1/pigs/", json={"ear_tag": ear, "sex": "M"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    return resp.json()["id"]


def test_reports_adg_and_farrowing_rate(client: TestClient):
    owner = auth(client, "owner@farm.test")
    pig_id = create_pig(client, owner["access_token"], "ADG-1")
    today = date.today()
    client.post(f"/api/v1/pigs/{pig_id}/weights", json={"date": today.isoformat(), "weight_kg": 10}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    client.post(f"/api/v1/pigs/{pig_id}/weights", json={"date": (today + timedelta(days=10)).isoformat(), "weight_kg": 20}, headers={"Authorization": f"Bearer {owner['access_token']}"})

    adg = client.get("/api/v1/reports/adg", params={"pig_id": pig_id, "from": today.isoformat(), "to": (today + timedelta(days=10)).isoformat()})
    assert adg.status_code == 200
    body = adg.json()
    assert body["days"] == 10 and body["start_kg"] == 10 and body["end_kg"] == 20 and body["adg_kg_per_day"] == 1

    # Farrowing rate: 2 services, 1 farrowing
    svc1 = client.post("/api/v1/breeding/", json={"service_date": today.isoformat()}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    svc2 = client.post("/api/v1/breeding/", json={"service_date": (today + timedelta(days=1)).isoformat()}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert svc1.status_code == 201 and svc2.status_code == 201
    lit = client.post("/api/v1/litters/", json={"farrow_date": (today + timedelta(days=114)).isoformat(), "liveborn": 10}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert lit.status_code == 201
    fr = client.get("/api/v1/reports/farrowing-rate", params={"from": today.isoformat(), "to": (today + timedelta(days=200)).isoformat()})
    assert fr.status_code == 200 and abs(fr.json()["rate"] - 0.5) < 1e-6

