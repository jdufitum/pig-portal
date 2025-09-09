from io import BytesIO
from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    return client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"}).json()


def create_pig(client: TestClient, token: str) -> str:
    resp = client.post("/api/v1/pigs/", json={"ear_tag": "FILE-1", "sex": "F"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    return resp.json()["id"]


def test_upload_file_record(client: TestClient):
    owner = auth(client, "owner@farm.test")
    pig_id = create_pig(client, owner["access_token"])

    # Upload to pig photo endpoint (record + signed URL)
    files = {"image": ("test.jpg", BytesIO(b"fake-image"), "image/jpeg")}
    r = client.post(f"/api/v1/files/pigs/{pig_id}/photo", files=files, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["file"]["url"]

    # List files returns the record with URL
    li = client.get(f"/api/v1/files/pigs/{pig_id}", headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert li.status_code == 200 and any(f["url"] for f in li.json())

