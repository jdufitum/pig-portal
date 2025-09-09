import os
import sys
import datetime
import json
import time

import requests


BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000/api/v1")
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "owner@example.com")
OWNER_PASSWORD = os.environ.get("OWNER_PASSWORD", "password123")


def fail(msg: str, resp: requests.Response | None = None) -> None:
    if resp is not None:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        print(f"ERROR: {msg} status={resp.status_code} body={body}")
    else:
        print(f"ERROR: {msg}")
    sys.exit(1)


def main() -> None:
    # Login
    r = requests.post(f"{BASE}/auth/login", data={"username": OWNER_EMAIL, "password": OWNER_PASSWORD})
    if r.status_code != 200:
        fail("login failed", r)
    tokens = r.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    print("auth ok")

    # 1) Add pig
    pig_payload = {
        "ear_tag": "E2E-SOW-001",
        "sex": "F",
        "breed": "Yorkshire",
        "birth_date": str(datetime.date.today() - datetime.timedelta(days=400)),
        "class": "sow",
        "source": "on-farm",
        "status": "active",
        "current_pen": "P-1",
    }
    r = requests.post(f"{BASE}/pigs/", json=pig_payload, headers=headers)
    if r.status_code == 201:
        pig_id = r.json()["id"]
    elif r.status_code == 409:
        pigs = requests.get(f"{BASE}/pigs", headers=headers, params={"search": pig_payload["ear_tag"]}).json()
        pig_id = pigs[0]["id"]
    else:
        fail("create pig failed", r)
    print("pig id", pig_id)

    # 2) Add weight (T-10d)
    w1 = {"date": str(datetime.date.today() - datetime.timedelta(days=10)), "weight_kg": 150.5, "notes": "pre-service"}
    r = requests.post(f"{BASE}/pigs/{pig_id}/weights", json=w1, headers=headers)
    if r.status_code not in (200, 201):
        fail("add weight failed", r)
    print("weight 1 added")

    # 3) Record service
    svc = {
        "sow_id": pig_id,
        "service_date": str(datetime.date.today() - datetime.timedelta(days=30)),
        "method": "ai",
        "parity": 1,
        "pen_at_service": "M1",
    }
    r = requests.post(f"{BASE}/breeding/", json=svc, headers=headers)
    if r.status_code not in (200, 201):
        fail("create service failed", r)
    svc_id = r.json()["id"]
    print("service id", svc_id)

    # 4) Record litter
    lit = {
        "sow_id": pig_id,
        "farrow_date": str(datetime.date.today() - datetime.timedelta(days=2)),
        "liveborn": 10,
        "stillborn": 1,
    }
    r = requests.post(f"{BASE}/litters/", json=lit, headers=headers)
    if r.status_code not in (200, 201):
        fail("create litter failed", r)
    litter_id = r.json()["id"]
    print("litter id", litter_id)

    # 5) Add health event
    he = {
        "pig_id": pig_id,
        "date": str(datetime.date.today()),
        "diagnosis": "mild cough",
        "product": "oxytet",
        "dose": "5 ml",
        "route": "IM",
        "vet_name": "Dr Vet",
        "notes": "monitor",
        "cost": 12.5,
    }
    r = requests.post(f"{BASE}/health/", json=he, headers=headers)
    if r.status_code not in (200, 201):
        fail("create health event failed", r)
    hid = r.json()["id"]
    print("health id", hid)

    # 6) Export CSV and ensure ear tag present
    r = requests.get(f"{BASE}/pigs/export", headers=headers)
    if r.status_code != 200:
        fail("export csv failed", r)
    if pig_payload["ear_tag"] not in r.text:
        fail("csv missing created pig")
    print("csv ok")

    # 7) Report ADG (add a second weight first)
    w2 = {"date": str(datetime.date.today()), "weight_kg": 160.0}
    requests.post(f"{BASE}/pigs/{pig_id}/weights", json=w2, headers=headers)
    r = requests.get(f"{BASE}/reports/adg", headers=headers, params={"pig_id": pig_id})
    if r.status_code != 200:
        fail("adg report failed", r)
    adg = r.json()
    print("adg", json.dumps(adg))

    print("E2E SUCCESS")


if __name__ == "__main__":
    main()

