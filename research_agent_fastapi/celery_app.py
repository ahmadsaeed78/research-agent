# research_agent_fastapi/celery_app.py
import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
broker_url = os.getenv("CELERY_BROKER_URL", redis_url)
backend_url = os.getenv("CELERY_RESULT_BACKEND", redis_url)

celery_app = Celery(
    "research_agent",
    broker=broker_url,
    backend=backend_url,
    include=["research_agent_fastapi.worker"]
)

# Task configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # worker_pool="solo",   # default for Windows compatibility
    task_track_started=True,        # enables STARTED state
    task_acks_late=True,            # only acknowledge after completion
    worker_prefetch_multiplier=1,   # one task per worker at a time
    result_expires=3600,            # results expire after 1 hour
)