# research_agent/tools.py
from langchain_tavily import TavilySearch
from langchain.tools import tool

tavily_search = TavilySearch(max_results=3)

@tool
def web_search(query: str) -> str:
    """Search the web for current information on a topic."""
    results = tavily_search.invoke({"query": query})

    formatted = []
    for r in results["results"]:
        formatted.append(
            f"Source: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
        )

    return "\n\n".join(formatted)