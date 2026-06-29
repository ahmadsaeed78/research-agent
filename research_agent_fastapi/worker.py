# research_agent_fastapi/worker.py
import asyncio
from .celery_app import celery_app
from .main import run_research


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="research_agent_fastapi.worker.run_research_task"
)
def run_research_task(self, topic: str) -> dict:
    """
    Celery task that runs the research pipeline.
    bind=True gives access to self (the task instance) for retries.
    max_retries=3 means Celery will retry up to 3 times on failure.
    default_retry_delay=10 means wait 10 seconds between retries.
    """
    try:
        # Celery tasks are synchronous by default
        # run_research is async, so we need asyncio.run() to call it
        result = asyncio.run(run_research(topic))

        return {
            "topic": result["topic"],
            "draft": result["draft"],
            "verdict": result["verdict"],
            "revision_count": result["revision_count"]
        }

    except Exception as exc:
        # Retry the task on failure — Celery handles the backoff
        raise self.retry(exc=exc)