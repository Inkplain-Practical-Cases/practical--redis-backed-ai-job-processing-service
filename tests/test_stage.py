"""Verify STEP-2 intake and scoped lookups with no external Redis dependency."""
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


