from datetime import date, timedelta
from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    r = client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"})
    return r.json()


def create_pig(client: TestClient, token: str, ear: str, sex: str) -> str:
    resp = client.post("/api/v1/pigs/", json={"ear_tag": ear, "sex": sex, "class": "sow" if sex=='F' else "boar"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_breeding_and_litters_flow(client: TestClient):
    owner = auth(client, "owner@farm.test")
    sow_id = create_pig(client, owner["access_token"], "SOW-BR-1", "F")
    boar_id = create_pig(client, owner["access_token"], "BOAR-BR-1", "M")

    service_date = date.today()
    svc = client.post("/api/v1/breeding/", json={"sow_id": sow_id, "boar_id": boar_id, "service_date": service_date.isoformat(), "method": "ai", "parity": 1}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert svc.status_code == 201, svc.text
    event = svc.json()

    # Expected farrow auto = +114d
    assert event["expected_farrow"] is not None

    # Update pregnancy check
    upd = client.patch(f"/api/v1/breeding/{event['id']}", json={"preg_check_date": (service_date + timedelta(days=28)).isoformat(), "preg_status": "pos"}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert upd.status_code == 200

    # GET /breeding?preg_status=pos includes record
    li = client.get("/api/v1/breeding", params={"preg_status": "pos"}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert li.status_code == 200 and any(x["id"] == event["id"] for x in li.json())

    # Upcoming farrowings includes this record
    up = client.get("/api/v1/breeding/upcoming-farrowings", params={"from": service_date.isoformat(), "to": (service_date + timedelta(days=115)).isoformat()}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert up.status_code == 200 and any(x["sow"] is not None for x in up.json())

    # Litter record and weaning validation
    farrow_date = service_date + timedelta(days=115)
    lit = client.post("/api/v1/litters/", json={"sow_id": sow_id, "boar_id": boar_id, "farrow_date": farrow_date.isoformat(), "liveborn": 12, "stillborn": 1, "neonatal_deaths": 0}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert lit.status_code == 201, lit.text
    litter = lit.json()

    # Set wean date and weaned count
    w = client.patch(f"/api/v1/litters/{litter['id']}", json={"wean_date": (farrow_date + timedelta(days=21)).isoformat(), "weaned": 11}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert w.status_code == 200

    # Validation: weaned > liveborn -> 400
    bad = client.patch(f"/api/v1/litters/{litter['id']}", json={"weaned": 100}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert bad.status_code == 400

