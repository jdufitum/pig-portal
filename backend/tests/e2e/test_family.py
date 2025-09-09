from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    return client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"}).json()


def test_family_endpoint(client: TestClient):
    owner = auth(client, "owner@farm.test")
    # Create parents
    sire = client.post("/api/v1/pigs/", json={"ear_tag": "SIRE-1", "sex": "M", "class": "boar"}, headers={"Authorization": f"Bearer {owner['access_token']}"}).json()
    dam = client.post("/api/v1/pigs/", json={"ear_tag": "DAM-1", "sex": "F", "class": "sow"}, headers={"Authorization": f"Bearer {owner['access_token']}"}).json()
    # Create piglet
    piglet = client.post("/api/v1/pigs/", json={"ear_tag": "PIGLET-1", "sex": "M", "sire_id": sire["id"], "dam_id": dam["id"]}, headers={"Authorization": f"Bearer {owner['access_token']}"}).json()

    fam = client.get(f"/api/v1/pigs/{piglet['id']}/family", headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert fam.status_code == 200
    body = fam.json()
    assert any(p["ear_tag"] == "SIRE-1" for p in body["parents"]) and any(c["ear_tag"] == "PIGLET-1" for c in body["offspring"]) == False

