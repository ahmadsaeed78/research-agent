# Research Agent Deploy

A research-focused FastAPI project that uses Celery and Redis to run asynchronous research tasks and stream results.

## What this project does

- Provides a FastAPI REST API for research requests
- Uses LangChain and LangGraph to build and run research pipelines
- Supports synchronous research, streaming responses, and background Celery jobs
- Uses Redis as Celery broker and result backend
- Includes Docker Compose for local development and production-like deployment

## Technologies used

- Python 3.12
- FastAPI
- Uvicorn
- Celery
- Redis
- langchain, langchain-core, langchain-openai, langgraph, langgraph-checkpoint, langgraph-prebuilt, langsmith
- Docker / Docker Compose
- pytest / pytest-asyncio

## Repository structure

- `Dockerfile` - build image for the FastAPI app
- `docker-compose.yml` - local stack: `web`, `worker`, `redis`
- `research_agent_fastapi/` - application code
- `research_agent_fastapi/tests/` - test suite
- `.env.example` - environment variable template

## Setup

1. Clone repository

```bash
git clone https://github.com/ahmadsaeed78/research-agent.git
cd research-agent-deploy
```

2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Copy environment variables

```bash
copy .env.example .env
```

5. Update `.env` with your API keys and project settings

## Run locally

### With Docker Compose

```bash
docker compose up --build
```

The API will be available at `http://127.0.0.1:8000`.

### Without Docker

```bash
uvicorn research_agent_fastapi.api:app --host 0.0.0.0 --port 8000 --workers 1
```

Start the Celery worker in a separate terminal:

```bash
celery -A research_agent_fastapi.celery_app worker --loglevel=info --concurrency=1
```

## Deployment notes

- This project can deploy to platforms like Railway using the Dockerfile and `docker-compose.yml`.
- Railway should use `docker-compose.yml` or a Dockerfile build with a separate Redis add-on.
- Ensure environment variables are configured in the production service.

## Testing

```bash
pytest research_agent_fastapi/tests -q
```

If you see async test errors, install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

## Notes for recruiters

This repository demonstrates a cloud-ready ML/AI research service with:

- asynchronous task orchestration using Celery and Redis
- containerized deployment using Docker Compose
- API-first design with FastAPI
- pipeline orchestration with LangChain and LangGraph
- professional project documentation and environment management

## Important URLs

- `http://127.0.0.1:8000/docs` - OpenAPI Swagger UI
- `http://127.0.0.1:8000/redoc` - ReDoc UI
