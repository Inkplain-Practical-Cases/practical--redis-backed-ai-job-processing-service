"""Run a dedicated worker independently of the web application process."""
from app.features.feature_jobs.providers.redis_store import RedisStore
from app.features.feature_jobs.providers.fake_ai import FakeAI
from app.features.feature_jobs.services.job_worker import JobWorker

def main():
    worker = JobWorker(RedisStore(), FakeAI())
    while True:
        worker.run_once()

if __name__ == "__main__":
    main()
