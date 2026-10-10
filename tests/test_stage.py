"""Verify STEP-5 intake and scoped lookups with no external Redis dependency."""
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_submit_and_scope():
    data=client.post("/jobs",json={"prompt":"hello","tenant_id":"alpha"})
    assert data.status_code==202
    job_id=data.json()["id"]
    assert client.get(f"/jobs/{job_id}",headers={"X-Tenant-Id":"beta"}).status_code==404
    result=client.get(f"/jobs/{job_id}",headers={"X-Tenant-Id":"alpha"})
    assert result.status_code==200

def test_worker():
    data=client.post("/jobs",json={"prompt":"work","tenant_id":"alpha"})
    assert client.post("/internal/run-once").status_code==200


def test_duplicate_request():
    payload={"prompt":"idem","tenant_id":"alpha"}
    h={"Idempotency-Key":"fixed"}
    first=client.post("/jobs",json=payload,headers=h)
    second=client.post("/jobs",json=payload,headers=h)
    assert first.json()["id"] == second.json()["id"]
    assert client.post("/jobs",json={"prompt":"other","tenant_id":"alpha"},headers=h).status_code==409

