"""Worker loop with finite retries and deterministic fake AI provider."""
import time
from datetime import datetime, timezone

class JobWorker:
    def __init__(self, store, provider, max_attempts=3):
        self.store = store
        self.provider = provider
        self.max_attempts = max_attempts

    def run_once(self):
        job_id = self.store.dequeue(timeout=1)
        if job_id is None:
            return None
        job = self.store.get(job_id)
        if job is None or job["status"] not in ("queued", "retrying"):
            return None
        job["status"] = "running"
        job["attempts"] += 1
        self.store.update(job)
        try:
            result = self.provider.infer(job["prompt"])
            if not isinstance(result, str) or not result.strip():
                raise ValueError("Model produced an invalid result")
            job["result"] = result
            job["status"] = "completed"
        except (ConnectionError, TimeoutError) as exc:
            job["status"] = "dead_letter" if job["attempts"] >= self.max_attempts else "retrying"
            job["error"] = type(exc).__name__
            if job["status"] == "retrying":
                self.store.client.lpush("jobs:waiting", job_id)
        except ValueError as exc:
            job["status"] = "failed"
            job["error"] = type(exc).__name__
        job["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.store.update(job)
        return job["status"]
