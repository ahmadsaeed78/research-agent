# test_simple_stream.py
import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("GET", "http://127.0.0.1:8000/test/stream") as response:
            print(f"Status: {response.status_code}")
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    print(f"Received: {data}")

asyncio.run(test())