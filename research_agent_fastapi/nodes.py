# research_agent/nodes.py
from langchain_core.messages import HumanMessage
from .config import llm
from .state import ResearchState
from .tools import web_search


async def researcher_node(state: ResearchState):
    topic = state["topic"]
    raw_results = web_search.invoke({"query": topic})

    summarize_prompt = f"""You are a research assistant. Below are raw web search 
results on the topic: "{topic}"

Extract and organize the key facts as a clean bulleted list. 
Do not add opinions or analysis — just organize what was found.

Raw search results:
{raw_results}
"""
    response = await llm.ainvoke([HumanMessage(content=summarize_prompt)])
    return {
        "findings": response.content,
        "messages": [HumanMessage(content=f"Research completed on: {topic}")]
    }


async def writer_node(state: ResearchState):
    topic = state["topic"]
    findings = state["findings"]
    feedback = state.get("feedback", "")
    revision_count = state.get("revision_count", 0)

    if revision_count == 0:
        prompt = f"""You are a research writer. Using only the findings below,
write a clear well-structured answer to this topic: "{topic}"

Do not add facts that aren't in the findings.

Findings:
{findings}
"""
    else:
        prompt = f"""You are a research writer revising a draft based on feedback.

Topic: "{topic}"

Original findings:
{findings}

Previous draft:
{state['draft']}

Critic's feedback:
{feedback}

Write a revised draft that addresses the feedback. Use ONLY the findings above 
— do not introduce new facts not present in the findings.
"""
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return {
        "draft": response.content,
        "messages": [HumanMessage(content="Draft written.")]
    }


def parse_verdict(text: str) -> str:
    """
    Robustly extract APPROVED or NEEDS_REVISION from free-text critic output.
    Handles markdown bold, varying punctuation, and case differences.
    """
    normalized = text.upper()

    if "NEEDS_REVISION" in normalized or "NEEDS REVISION" in normalized:
        return "NEEDS_REVISION"
    elif "APPROVED" in normalized:
        return "APPROVED"
    else:
        return "NEEDS_REVISION"


async def critic_node(state: ResearchState):
    topic = state["topic"]
    findings = state["findings"]
    draft = state["draft"]
    revision_count = state.get("revision_count", 0)

    review_prompt = f"""You are a strict fact-checking critic. Compare the draft 
below against the findings it should be based on.

Topic: "{topic}"

Findings (the ONLY allowed source of facts):
{findings}

Draft to review:
{draft}

Check specifically for:
1. Any claim, name, number, or example in the draft that does NOT appear in the findings
2. Any important point from the findings that the draft left out

Respond in this exact format, with no other text:
VERDICT: APPROVED
or
VERDICT: NEEDS_REVISION
ISSUES: <specific problems, or None>
"""
    response = await llm.ainvoke([HumanMessage(content=review_prompt)])
    content = response.content
    verdict = parse_verdict(str(content))

    return {
        "feedback": content,
        "verdict": verdict,
        "revision_count": revision_count + 1,
        "messages": [HumanMessage(content="Critic completed.")]
    }