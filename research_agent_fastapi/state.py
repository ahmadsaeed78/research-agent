# research_agent/state.py
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    topic: str
    findings: str
    draft: str
    feedback: str
    verdict: str
    revision_count: int