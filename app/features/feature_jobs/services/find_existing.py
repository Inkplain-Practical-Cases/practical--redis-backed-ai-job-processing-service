# Prevent duplicate keys within tenant scope.
def find_existing(queue, tenant_id, key):
    return next((job for job in queue.jobs.values() if job.get("tenant_id") == tenant_id and job.get("key") == key), None)
