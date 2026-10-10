"""Tenant isolation, duplicate submission, retry, recovery and invalid output tests."""
import fakeredis
import pytest
from app.features.feature_jobs.providers.redis_store import RedisStore
from app.features.feature_jobs.services.job_service import JobService
from app.features.feature_jobs.services.job_worker import JobWorker
from app.features.feature_jobs.providers.fake_ai import FakeAI

def make_store():
    return RedisStore(fakeredis.FakeRedis(decode_responses=True))

def test_idempotency_and_tenant_boundary():
    store=make_store()
    service=JobService(store)
    first=service.submit("alpha","hello","request-1")
    assert first["id"]==service.submit("alpha","hello","request-1")["id"]
    assert service.get(first["id"],"beta") is None
    assert JobWorker(store,FakeAI()).run_once()=="completed"
    assert service.get(first["id"],"alpha")["result"]=="Processed: hello"

def test_idempotency_payload_conflict():
    service=JobService(make_store())
    service.submit("alpha","hello","reused")
    with pytest.raises(ValueError):
        service.submit("alpha","different","reused")

def test_retry_exhaustion_and_ack():
    class Broken:
        def infer(self,prompt):
            raise TimeoutError("secret details must not be logged")
    store=make_store()
    service=JobService(store)
    job=service.submit("alpha","prompt","r")
    worker=JobWorker(store,Broken(),max_attempts=3)
    assert [worker.run_once() for _ in range(3)]==["retrying","retrying","dead_letter"]
    assert service.get(job["id"],"alpha")["error"]=="TimeoutError"
    assert store.client.llen("jobs:processing")==0

def test_processing_list_survives_worker_loss():
    store=make_store()
    service=JobService(store)
    job=service.submit("alpha","hello","r")
    assert store.dequeue()==job["id"]
    assert store.client.llen("jobs:processing")==1
    assert store.recover()==1
    assert JobWorker(store,FakeAI()).run_once()=="completed"

def test_malformed_provider_result():
    class Empty:
        def infer(self,prompt):
            return ""
    store=make_store()
    job=JobService(store).submit("alpha","hello","bad")
    assert JobWorker(store,Empty()).run_once()=="failed"
    assert JobService(store).get(job["id"],"alpha")["error"]=="ValueError"
