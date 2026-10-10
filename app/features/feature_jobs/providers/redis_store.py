"""Redis atomic submit, list queue and tenant-isolated status storage."""
import json
import os
import redis

class RedisStore:
    def __init__(self, client=None):
        self.client = client or redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

    def submit(self, job):
        # WATCH protects first-write idempotency and avoids duplicate enqueue on racing submissions.
        key = f"idem:{job['tenant_id']}:{job['idempotency_key']}"
        with self.client.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    old = pipe.get(key)
                    if old:
                        pipe.unwatch()
                        return json.loads(self.client.get(f"job:{old}"))
                    pipe.multi()
                    pipe.set(key, job["id"])
                    pipe.set(f"job:{job['id']}", json.dumps(job))
                    pipe.lpush("jobs:waiting", job["id"])
                    pipe.execute()
                    return job
                except redis.WatchError:
                    continue

    def get(self, job_id):
        raw = self.client.get(f"job:{job_id}")
        return json.loads(raw) if raw else None

    def update(self, job):
        self.client.set(f"job:{job['id']}", json.dumps(job))

    def dequeue(self, timeout=1):
        item = self.client.brpop("jobs:waiting", timeout=timeout)
        return item[1] if item else None
