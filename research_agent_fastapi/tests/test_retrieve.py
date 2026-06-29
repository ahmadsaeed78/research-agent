# test_retrieve.py — retrieve a completed job by its ID
import httpx
import asyncio

async def retrieve():
    job_id = "741768e2-51af-4ba4-bdf9-04943742dc56"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"http://127.0.0.1:8000/research/job_celery/{job_id}")
        result = response.json()
        print(f"Status: {result['status']}")
        if result.get('result'):
            print(f"Draft preview: {result['result']['draft'][:300]}")

asyncio.run(retrieve())