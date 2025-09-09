from datetime import date
from fastapi.testclient import TestClient


def auth(client: TestClient, email: str) -> dict:
    return client.post("/api/v1/auth/login", data={"username": email, "password": "Passw0rd!"}).json()


def test_tasks_flow(client: TestClient):
    owner = auth(client, "owner@farm.test")

    # Create a task linked to pig-less context
    t = client.post("/api/v1/tasks/", json={"title": "Weigh TEST-100", "due_date": date.today().isoformat()}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert t.status_code == 201, t.text
    task = t.json()

    # Summary endpoint
    s = client.get("/api/v1/tasks/summary")
    assert s.status_code == 200 and s.json().get("open") >= 1

    # Mark done
    d = client.patch(f"/api/v1/tasks/{task['id']}", json={"status": "done"}, headers={"Authorization": f"Bearer {owner['access_token']}"})
    assert d.status_code == 200 and d.json()["status"] == "done"

