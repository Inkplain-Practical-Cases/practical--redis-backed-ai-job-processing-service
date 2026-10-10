"""Educational HTTP application for STEP-3. Not the hardened final service."""
from uuid import uuid4
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from app.features.feature_jobs.providers.memory_queue import MemoryQueue
from app.features.feature_jobs.services.process_next import process_next


app = FastAPI(title="Redis AI jobs STEP-3")
queue = MemoryQueue()
class JobInput(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    tenant_id: str = Field(min_length=1, max_length=64)

@app.post("/jobs", status_code=202)
def submit_job(body: JobInput, idempotency_key: str = Header(default="demo")):
    job = {"id": str(uuid4()), "prompt": body.prompt, "tenant_id": body.tenant_id,
           "key": idempotency_key, "status": "queued", "result": None}
    queue.submit(job)
    return {"id": job["id"], "status": job["status"]}

@app.get("/jobs/{job_id}")
def get_job(job_id: str, x_tenant_id: str = Header(alias="X-Tenant-Id")):
    job = queue.jobs.get(job_id)
    if job is None or job["tenant_id"] != x_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"id": job["id"], "status": job["status"], "result": job["result"]}

@app.post("/internal/run-once")
def run_once():
    job = process_next(queue)
    return {"status": job["status"] if job else "idle"}

