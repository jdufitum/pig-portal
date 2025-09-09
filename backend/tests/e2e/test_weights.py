from datetime import date, timedelta
from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    r = client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"})
    return r.json()


def create_pig(client: TestClient, token: str) -> str:
    resp = client.post("/api/v1/pigs/", json={"ear_tag": f"TEST-{date.today().isoformat()}", "sex": "M"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_weights_crud_and_growth(client: TestClient):
    owner = auth(client, "owner@farm.test")
    worker = auth(client, "worker@farm.test")
    pig_id = create_pig(client, owner["access_token"])

    today = date.today()
    w1 = client.post(f"/api/v1/pigs/{pig_id}/weights", json={"date": today.isoformat(), "weight_kg": 10.0}, headers={"Authorization": f"Bearer {worker['access_token']}"})
    assert w1.status_code == 201, w1.text
    w2 = client.post(f"/api/v1/pigs/{pig_id}/weights", json={"date": (today + timedelta(days=10)).isoformat(), "weight_kg": 20.0}, headers={"Authorization": f"Bearer {worker['access_token']}"})
    assert w2.status_code == 201

    # List weights with range
    li = client.get(f"/api/v1/pigs/{pig_id}/weights", params={"from": today.isoformat()}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert li.status_code == 200 and len(li.json()) >= 2

    # Growth curve returns series
    gc = client.get(f"/api/v1/pigs/{pig_id}/growth-curve", headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert gc.status_code == 200 and len(gc.json()) >= 2

    # Validation: zero weight -> 422
    bad = client.post(f"/api/v1/pigs/{pig_id}/weights", json={"date": today.isoformat(), "weight_kg": 0}, headers={"Authorization": f"Bearer {worker['access_token']}"})
    assert bad.status_code in (400, 422)

