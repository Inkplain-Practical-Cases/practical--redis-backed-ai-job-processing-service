# Request contracts prevent invalid, unbounded AI jobs from entering the queue.
# ICS layer: schema; Step: 1.
from pydantic import BaseModel, Field
class JobRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
