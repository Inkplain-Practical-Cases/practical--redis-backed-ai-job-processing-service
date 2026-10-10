# Redis-Backed AI Job Processing Service

## Build
FastAPI API with Redis job state and queue, a separate worker process, tenant-scoped status lookups, idempotency keys, a deterministic offline AI adapter, bounded transient retries, Docker Compose and pytest fixtures.

## Run
```bash
docker compose up --build
```
Submit with `POST /jobs` JSON `{ "tenant_id": "demo", "prompt": "hello" }` and header `Idempotency-Key: demo-1`. Poll `GET /jobs/{job_id}` with header `X-Tenant-Id: demo`.

## Tests
```bash
pip install -r requirements.txt
pytest -q
```

## Learning stages
- STEP-1: Async API intake
- STEP-2: Queue provider
- STEP-3: Worker lifecycle
- STEP-4: Ownership and deduplication
- STEP-5: Retry exhaustion
- STEP-6: Failure coverage, logs and CI

Each `step-0N-*` branch has its corresponding `STEP-N.md` and `.crd`. This is an educational reference, **not a production-hardened queue**; worker leases, requeue after crash, nonblocking retry scheduling, authorization and production monitoring need hardening.
