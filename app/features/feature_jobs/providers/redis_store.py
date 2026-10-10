"""Redis provider for atomic job enqueue and leased worker delivery."""
import json
import os
import redis

class RedisStore:
    def __init__(self, client=None):
        self.client = client if client is not None else redis.Redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"),decode_responses=True)

    def submit(self, job):
        key = f"idem:{job['tenant_id']}:{job['idempotency_key']}"
        with self.client.pipeline() as p:
            while True:
                try:
                    p.watch(key)
                    prior = p.get(key)
                    if prior:
                        existing = p.get(f"job:{prior}")
                        p.unwatch()
                        if existing is not None:
                            return json.loads(existing)
                        raise RuntimeError("Idempotency index points to missing job")
                    p.multi()
                    p.set(key,job["id"])
                    p.set(f"job:{job['id']}",json.dumps(job))
                    p.lpush("jobs:waiting",job["id"])
                    p.execute()
                    return job
                except redis.WatchError:
                    continue

    def get(self,job_id):
        raw=self.client.get(f"job:{job_id}")
        return json.loads(raw) if raw else None

    def update(self,job):
        self.client.set(f"job:{job['id']}",json.dumps(job))

    def dequeue(self,timeout=1):
        # Moves to a processing list atomically; a crash does not erase its reference.
        return self.client.brpoplpush("jobs:waiting","jobs:processing",timeout=timeout)

    def acknowledge(self,job_id):
        self.client.lrem("jobs:processing",1,job_id)

    def requeue(self,job_id):
        with self.client.pipeline(transaction=True) as p:
            p.lrem("jobs:processing",1,job_id)
            p.lpush("jobs:waiting",job_id)
            p.execute()

    def recover(self):
        # Administrative recovery: only run after all workers have stopped.
        recovered=0
        while self.client.rpoplpush("jobs:processing","jobs:waiting") is not None:
            recovered+=1
        return recovered
