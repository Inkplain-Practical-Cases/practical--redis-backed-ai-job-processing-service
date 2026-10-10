# Retry transient failures up to a fixed limit.
def process_with_retries(job, executor, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        job["attempts"] = attempt
        try:
            job["result"] = executor(job["prompt"])
            job["status"] = "completed"
            return job
        except (TimeoutError, ConnectionError) as exc:
            job["status"] = "dead_letter" if attempt == max_attempts else "retrying"
            job["error"] = type(exc).__name__
    return job
