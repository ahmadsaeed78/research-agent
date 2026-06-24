# research_agent/graph.py
from langgraph.graph import StateGraph, START, END
from .config import MAX_REVISIONS
from .state import ResearchState
from .nodes import researcher_node, writer_node, critic_node


def route_after_critic(state: ResearchState):
    verdict = state["verdict"]
    revision_count = state["revision_count"]

    if verdict == "APPROVED" or revision_count >= MAX_REVISIONS:
        return "end"
    else:
        return "revise"


def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("researcher", researcher_node)
    builder.add_node("writer", writer_node)
    builder.add_node("critic", critic_node)

    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "critic")

    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "end": END,
            "revise": "writer"
        }
    )

    return builder.compile()