from datetime import date
from fastapi.testclient import TestClient


SAMPLE = {"ear_tag": "SOW-001", "sex": "F", "class":"sow", "birth_date": "2025-01-01", "pen":"Gestation A"}


def auth(client: TestClient, email: str) -> dict:
    r = client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"})
    return r.json()


def test_pig_crud_and_roles(client: TestClient):
    owner = auth(client, "owner@farm.test")
    worker = auth(client, "worker@farm.test")
    vet = auth(client, "vet@farm.test")

    # Worker cannot create pigs
    rw = client.post("/api/v1/pigs/", json=SAMPLE, headers={"Authorization": f"Bearer {worker['access_token']}"})
    assert rw.status_code == 403

    # Owner creates
    ro = client.post("/api/v1/pigs/", json=SAMPLE, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert ro.status_code == 201, ro.text
    pig = ro.json()

    # Get by id
    g = client.get(f"/api/v1/pigs/{pig['id']}", headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert g.status_code == 200

    # Duplicate ear tag -> 409
    dup = client.post("/api/v1/pigs/", json=SAMPLE, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert dup.status_code == 409

    # List with filters
    li = client.get("/api/v1/pigs", params={"sex":"F","pen":"Gestation A"}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert li.status_code == 200 and any(row["id"] == pig["id"] for row in li.json())

    # Update pen and class
    up = client.patch(f"/api/v1/pigs/{pig['id']}", json={"pen": "Gestation B", "class": "sow"}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert up.status_code == 200 and up.json()["current_pen"] == "Gestation B"

    # Vet cannot delete pig -> 403
    vd = client.delete(f"/api/v1/pigs/{pig['id']}", headers={"Authorization": f"Bearer {vet['access_token']}"})
    assert vd.status_code == 403

    # Owner delete
    od = client.delete(f"/api/v1/pigs/{pig['id']}", headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert od.status_code == 204

