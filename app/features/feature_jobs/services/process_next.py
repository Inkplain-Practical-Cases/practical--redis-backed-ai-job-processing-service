# Process one queued job with a deterministic local model replacement.
def process_next(queue):
    job_id = queue.pop()
    if job_id is None:
        return None
    job = queue.jobs[job_id]
    job["status"] = "running"
    job["result"] = job["prompt"].strip().upper()
    job["status"] = "completed"
    return job
