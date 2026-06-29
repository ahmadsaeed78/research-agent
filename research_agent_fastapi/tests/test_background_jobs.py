# test_background_job.py
import httpx
import asyncio
import time

async def test_background_job():
    async with httpx.AsyncClient(timeout=10.0) as client:

        # Step 1: submit the job — should return immediately
        start = time.time()
        response = await client.post(
            "http://127.0.0.1:8000/research/job_celery",
            json={"topic": "What are the main AI regulations in 2026?"}
        )
        submit_time = time.time() - start

        job = response.json()
        job_id = job["job_id"]
        print(f"Job submitted in {submit_time:.2f}s")
        print(f"Job ID: {job_id}")
        print(f"Status: {job['status']}\n")

        # Step 2: poll until done
        async with httpx.AsyncClient(timeout=10.0) as poll_client:
            while True:
                await asyncio.sleep(5)  # check every 5 seconds

                status_response = await poll_client.get(
                    f"http://127.0.0.1:8000/research/job_celery/{job_id}"
                )
                status = status_response.json()
                print(f"Status: {status['status']}")

                if status["status"] == "COMPLETED":
                    print(f"\nCompleted!")
                    print(f"Verdict: {status['result']['verdict']}")
                    print(f"Revisions: {status['result']['revision_count']}")
                    print(f"\nDraft preview:\n{status['result']['draft'][:300]}...")
                    break

                elif status["status"] == "FAILED":
                    print(f"\nFailed: {status['error']}")
                    break

asyncio.run(test_background_job())