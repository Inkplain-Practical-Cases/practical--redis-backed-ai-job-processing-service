"""HTTP entrypoint: FastAPI doors only, with services injected by dependency."""
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from app.features.feature_jobs.services.job_service import JobService
from app.features.feature_jobs.providers.redis_store import RedisStore

app = FastAPI(title="Redis AI Job Processing")
store = RedisStore()
service = JobService(store)
class SubmitJob(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    tenant_id: str = Field(min_length=1, max_length=64)

@app.post("/jobs", status_code=202)
def submit_job(body: SubmitJob, idempotency_key: str = Header(min_length=1, max_length=128)):
    return service.submit(body.tenant_id, body.prompt, idempotency_key)

@app.get("/jobs/{job_id}")
def get_job(job_id: str, tenant_id: str = Header(alias="X-Tenant-Id")):
    job = service.get(job_id, tenant_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
