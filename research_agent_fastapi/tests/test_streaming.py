import httpx
import asyncio
import json

async def test_stream():
    print("Connecting to stream...\n")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            "http://127.0.0.1:8000/research/stream",
            json={"topic": "What are the main AI regulations in 2026?"}
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    
                    if data["type"] == "node_start":
                        print(f"\n[{data['node'].upper()} STARTED]")
                    
                    elif data["type"] == "token":
                        print(data["content"], end="", flush=True)
                    
                    elif data["type"] == "node_end":
                        node = data["node"]
                        if node == "critic":
                            print(f"\n[CRITIC DONE — verdict: {data.get('verdict')}, revisions: {data.get('revision_count')}]")
                        else:
                            print(f"\n[{node.upper()} DONE]")
                    
                    elif data["type"] == "done":
                        print("\n\n[STREAM COMPLETE]")

asyncio.run(test_stream())