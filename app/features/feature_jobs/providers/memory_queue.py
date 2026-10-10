# Offline queue double supporting deterministic tests; not Redis persistence.
from collections import deque
class MemoryQueue:
    def __init__(self):
        self.items = deque()
        self.jobs = {}
    def submit(self, job):
        self.jobs[job["id"]] = job
        self.items.append(job["id"])
    def pop(self):
        return self.items.popleft() if self.items else None
