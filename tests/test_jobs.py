"""Integration-like tests use fakeredis and never reach external services."""
import fakeredis
from app.features.feature_jobs.providers.redis_store import RedisStore
from app.features.feature_jobs.services.job_service import JobService
from app.features.feature_jobs.services.job_worker import JobWorker
from app.features.feature_jobs.providers.fake_ai import FakeAI

def test_success_and_idempotency():
    store = RedisStore(fakeredis.FakeRedis(decode_responses=True))
    service = JobService(store)
    first = service.submit("tenant-a", "hello", "key1")
    duplicate = service.submit("tenant-a", "hello", "key1")
    assert first["id"] == duplicate["id"]
    assert JobWorker(store, FakeAI()).run_once() == "completed"
    assert service.get(first["id"], "tenant-a")["result"] == "Processed: hello"
    assert service.get(first["id"], "tenant-b") is None

def test_retry_exhaustion():
    class AlwaysTimeout:
        def infer(self, prompt):
            raise TimeoutError("temporary")
    store = RedisStore(fakeredis.FakeRedis(decode_responses=True))
    service = JobService(store)
    job = service.submit("a", "x", "retry")
    worker = JobWorker(store, AlwaysTimeout(), max_attempts=3)
    assert [worker.run_once() for _ in range(3)] == ["retrying", "retrying", "dead_letter"]
    assert service.get(job["id"], "a")["attempts"] == 3
