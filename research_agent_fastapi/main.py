# research_agent/main.py
from .state import ResearchState
from .graph import build_graph
from langsmith import traceable
from langchain_core.runnables import RunnableConfig


@traceable(name="research-pipeline", metadata={"version": "1.0"})
async def run_research(topic: str):
    graph = build_graph()

    initial_state: ResearchState = {
        "messages": [],
        "topic": topic,
        "findings": "",
        "draft": "",
        "feedback": "",
        "verdict": "",
        "revision_count": 0
    }

    config = RunnableConfig(
        tags=[f"topic: {topic[:30]}"],
        metadata={"revision_count": 0}
    )

    final_state = await graph.ainvoke(initial_state, config)
    from langsmith import Client
    client = Client()

    return final_state




if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_research("What are the main AI regulations introduced in 2026?"))
    print(f"\nFinal verdict: {result['verdict']}")
    print(f"Revision count: {result['revision_count']}")
    print(f"\nDraft preview: {result['draft'][:300]}...")