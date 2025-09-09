from io import BytesIO
from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    return client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"}).json()


def test_import_export_csv(client: TestClient):
    owner = auth(client, "owner@farm.test")
    csv_content = b"ear_tag,sex,class,pen\nIMP-1,M,grower,A\nIMP-2,F,sow,B\n"
    files = {"file": ("pigs.csv", BytesIO(csv_content), "text/csv")}
    r = client.post("/api/v1/pigs/import", files=files, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert r.status_code == 200
    res = r.json()["results"]
    assert len(res) == 2 and all(isinstance(x.get("success"), bool) for x in res)

    # Export contains headers & rows
    e = client.get("/api/v1/pigs/export", headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert e.status_code == 200
    text = e.text
    assert "ear_tag" in text and ("IMP-1" in text or "IMP-2" in text)

