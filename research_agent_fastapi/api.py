from fastapi import FastAPI
from pydantic import BaseModel
from .main import run_research

import json
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig
from .graph import build_graph
from .state import ResearchState

from fastapi import HTTPException


import uuid
from fastapi import BackgroundTasks
from datetime import datetime, timezone


from contextlib import asynccontextmanager
import asyncio
from datetime import datetime, timedelta, timezone



#redis + celery 
from .worker import run_research_task
from .celery_app import celery_app
from celery.result import AsyncResult


# POST /research          → blocking JSON    — wait for full result, one response
# POST /research/stream   → SSE streaming   — live tokens, connection stays open
# POST /research/job      → background job  — instant job_id, poll for result
# GET  /research/job/{id} → job status      — check progress, get result when ready




# In-memory job store — simple dict for Phase 1
# Key: job_id, Value: job status dict
jobs: dict = {}


class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    completed_at: str | None = None
    result: dict | None = None
    error: str | None = None







async def process_research_job(job_id: str, topic: str):
    """
    Background worker function.
    Runs independently after the HTTP response is already sent.
    """
    try:
        # Update status to RUNNING
        jobs[job_id]["status"] = "RUNNING"

        # Run the actual research pipeline
        result = await run_research(topic)

        # Store the completed result
        jobs[job_id]["status"] = "COMPLETED"
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        jobs[job_id]["result"] = {
            "topic": result["topic"],
            "draft": result["draft"],
            "verdict": result["verdict"],
            "revision_count": result["revision_count"]
        }

    except Exception as e:
        # Store the failure so the client can see what went wrong
        jobs[job_id]["status"] = "FAILED"
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        jobs[job_id]["error"] = str(e)
#Above is all background related logic

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    # --- STARTUP LOGIC ---
    async def cleanup():
        while True:
            await asyncio.sleep(3600)  # run every hour
            # Note: Changed to timezone-aware UTC to match your background_tasks logic
            cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            
            to_delete = [
                job_id for job_id, job in jobs.items()
                if job["status"] in ("COMPLETED", "FAILED")
                and job["completed_at"]
                and datetime.fromisoformat(job["completed_at"]) < cutoff
            ]
            for job_id in to_delete:
                del jobs[job_id]

    # Create the background cleanup task on startup
    cleanup_task = asyncio.create_task(cleanup())
    
    yield  # The application runs while paused here
    
    # --- SHUTDOWN LOGIC ---
    # Cancel the background task cleanly when the app stops
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

# Pass the lifespan context manager into the FastAPI initialization
app = FastAPI(title="Research Agent API", lifespan=lifespan)

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    topic: str
    draft: str
    verdict: str
    revision_count: int






@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    result = await run_research(request.topic)
    return ResearchResponse(
        topic=result['topic'],
        draft=result['draft'],
        verdict=result['verdict'],
        revision_count=result['revision_count']
    )



@app.post("/research/stream")
async def research_stream(request: ResearchRequest):
    """
    Streams the research pipeline output as Server-Sent Events.
    Client receives node status updates and final draft tokens as they generate.
    """
    async def event_generator():
        graph = build_graph()
        initial_state: ResearchState = {
            "messages": [],
            "topic": request.topic,
            "findings": "",
            "draft": "",
            "feedback": "",
            "verdict": "",
            "revision_count": 0
        }
        config = RunnableConfig(tags=[f"topic:{request.topic[:30]}"])
        current_node = None  # track which node is running right now
        # astream_events yields fine-grained events as the graph runs
        async for event in graph.astream_events(initial_state, config=config, version="v2"):
            event_type = event["event"]
            event_name = event.get("name", "")
            if event_type=="on_chain_start" and event_name in ["researcher", "writer", "critic"]:
                current_node = event_name
                data = json.dumps({
                    "type": "node_start",
                    "node": event_name
                })
                yield f"data: {data}\n\n"
            # LLM token — stream writer tokens to client in real time
            elif event_type == "on_chat_model_stream" and current_node == "writer":
                chunk = event["data"].get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    data = json.dumps({
                        "type": "token",
                        "content": chunk.content
                    })
                    yield f"data: {data}\n\n"
            elif event_type == "on_chain_end" and event_name in ["researcher", "writer", "critic"]:
                output = event.get("data", {}).get("output", {})
                extra = {}

                if event_name == "critic" and "verdict" in output:
                    extra["verdict"] = output["verdict"]
                    extra["revision_count"] = output.get("revision_count", 0)

                data = json.dumps({
                    "type": "node_end",
                    "node": event_name,
                    **extra
                })
                yield f"data: {data}\n\n"
                
                if event_name == current_node:
                    current_node = None
            
        yield f"data: {json.dumps({"type": "done"})}\n\n"
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # prevents nginx from buffering the stream
        }
    )




#below is all endpoints supporting background worker
@app.post("/research/job", response_model=JobResponse)
async def create_research_job(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Immediately returns a job_id.
    Research runs in the background independently.
    """
    job_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()


    # Register the job as PENDING before scheduling work
    jobs[job_id] = {
        "job_id": job_id,
        "status": "PENDING",
        "created_at": created_at,
        "completed_at": None,
        "result": None,
        "error": None
    }
    # Schedule the background work — this returns immediately
    background_tasks.add_task(process_research_job, job_id, request.topic)

    return JobResponse(job_id=job_id, status="PENDING", created_at=created_at)



@app.get("/research/job/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Returns current status and result (if completed) for a given job.
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail=f"job {job_id} not found"
        )
    return JobStatusResponse(**jobs[job_id])







#below redis research job

@app.post("/research/job_celery")
async def create_research_job_celery(request: ResearchRequest):
    """Submit a research job to Celery. Returns immediately with task ID."""
    task = run_research_task.delay(request.topic)
    return {
        "job_id": task.id,
        "status": "PENDING"
    }


@app.get("/research/job_celery/{job_id}")
async def get_job_status_celery(job_id: str):
    """Check job status and retrieve result when complete."""
    task_result = AsyncResult(job_id, app=celery_app)
    if task_result.state == "PENDING":
        return {"job_id": job_id, "status": "PENDING"}

    elif task_result.state == "STARTED":
        return {"job_id": job_id, "status": "RUNNING"}

    elif task_result.state == "SUCCESS":
        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "result": task_result.result
        }

    elif task_result.state == "FAILURE":
        return {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(task_result.result)
        }

    else:
        return {"job_id": job_id, "status": task_result.state}






# # Add this temporarily to your api.py
# @app.get("/test/stream")
# async def test_stream_simple():
#     async def simple_generator():
#         for i in range(5):
#             import asyncio
#             await asyncio.sleep(0.5)
#             yield f"data: {json.dumps({'count': i})}\n\n"
#         yield f"data: {json.dumps({'type': 'done'})}\n\n"
    
#     return StreamingResponse(
#         simple_generator(),
#         media_type="text/event-stream",
#         headers={"Cache-Control": "no-cache"}
#     )