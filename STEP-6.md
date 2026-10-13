# STEP-6: Failure tests observability and CI

This branch adds the component summarize_metrics. Read app/features/feature_jobs/services/summarize_metrics.py for the implementation.

The end-to-end Redis integration and runtime tests are not yet completed.

## Database (Entity) Relations
STEP-6 uses Redis keys `job:{id}`, `idem:{tenant_id}:{idempotency_key}` and lists `jobs:waiting`, `jobs:processing`. All are derived from `RedisStore`. The ERD's edges are logical references to job IDs, not database-enforced foreign keys. Earlier steps have no Redis-backed persistence. See `STEP-6.erd` and `STEP-6-ERD` in main `.inkp`.
