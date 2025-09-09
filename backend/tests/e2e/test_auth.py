from fastapi.testclient import TestClient


def test_login_and_refresh(client: TestClient):
    # Login
    resp = client.post("/api/v1/auth/login", data={"username": "owner@farm.test", "password": "Passw0rd!"})
    assert resp.status_code == 200, resp.text
    tokens = resp.json()
    assert tokens["access_token"] and tokens["refresh_token"]

    # Access protected route
    r2 = client.get("/api/v1/ping-protected", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r2.status_code == 200

    # Without token -> 401
    r3 = client.get("/api/v1/ping-protected")
    assert r3.status_code == 401

    # Refresh
    r4 = client.post("/api/v1/auth/refresh", json={"token": tokens["refresh_token"]})
    assert r4.status_code == 200
    assert r4.json()["access_token"]

