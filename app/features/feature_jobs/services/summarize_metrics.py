# Count job states to demonstrate metrics without exporting PII.
def summarize_metrics(queue):
    counts = {}
    for job in queue.jobs.values():
        status = job["status"]
        counts[status] = counts.get(status, 0) + 1
    return counts
