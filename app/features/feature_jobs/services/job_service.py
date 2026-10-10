"""Job orchestration: tenant ownership and typed state transitions."""
from uuid import uuid4
from datetime import datetime, timezone

class JobService:
    def __init__(self, store):
        self.store = store

    def submit(self, tenant_id, prompt, idempotency_key):
        if not tenant_id.strip() or not prompt.strip():
            raise ValueError("tenant and prompt must not be blank")
        now = datetime.now(timezone.utc).isoformat()
        job = {"id": str(uuid4()), "tenant_id": tenant_id, "idempotency_key": idempotency_key, "prompt": prompt,
               "status": "queued", "attempts": 0, "result": None, "error": None, "created_at": now, "updated_at": now}
        saved = self.store.submit(job)
        if saved["prompt"] != prompt or saved["tenant_id"] != tenant_id:
            raise ValueError("idempotency key reused with different payload")
        return {"id": saved["id"], "status": saved["status"]}

    def get(self, job_id, tenant_id):
        job = self.store.get(job_id)
        if not job or job["tenant_id"] != tenant_id:
            return None
        return {k: v for k, v in job.items() if k not in ("prompt", "idempotency_key")}
