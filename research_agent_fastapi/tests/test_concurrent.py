# test_concurrent.py
import asyncio
import httpx
import time

async def make_request(client, topic):
    start = time.time()
    response = await client.post(
        "http://127.0.0.1:8000/research",
        json={"topic": topic},
        timeout=120.0
    )
    elapsed = time.time() - start
    print(f"'{topic[:40]}...' finished in {elapsed:.1f}s")
    return response.json()

async def main():
    async with httpx.AsyncClient() as client:
        start = time.time()
        
        results = await asyncio.gather(
            make_request(client, "What are the main AI regulations introduced in 2026?"),
            make_request(client, "What are the latest developments in quantum computing?")
        )
        
        total = time.time() - start
        print(f"\nTotal time for both requests: {total:.1f}s")
        
        # Add this — check revision counts to confirm the theory
        for r in results:
            print(f"Topic: {r['topic'][:40]}... | Revisions: {r['revision_count']}")

asyncio.run(main())