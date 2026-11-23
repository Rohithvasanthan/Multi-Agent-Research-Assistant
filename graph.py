import os
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

load_dotenv()


class AgentState(TypedDict):
    query: str
    research_notes: List[str]
    draft_report: str
    critique: str
    revision_count: int
    is_approved: bool


def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Please set it in .env or the sidebar.")
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=api_key,
    )


search_tool = DuckDuckGoSearchRun()


def researcher_node(state: AgentState) -> dict:
    """Node 1: Gathers live web context based on user query and any reviewer critique."""
    query = state["query"]
    critique = state.get("critique", "")
    search_query = f"{query} {critique}".strip()[:250]

    try:
        search_result = search_tool.invoke(search_query)
        notes = [f"- {search_result}"]
    except Exception as e:
        notes = [f"- Web search fallback triggered ({str(e)}). Relying on model architectural knowledge."]

    existing_notes = state.get("research_notes", [])
    return {"research_notes": existing_notes + notes}


def synthesizer_node(state: AgentState) -> dict:
    """Node 2: Synthesizes research notes into a structured technical response with code."""
    llm = get_llm()
    notes_text = "\n".join(state.get("research_notes", []))
    critique = state.get("critique", "None")

    prompt = f"""You are a Senior AI & Software Architect.
User Query: {state['query']}

Web Research Context:
{notes_text}

Previous Reviewer Critique (address this if present): {critique}

Instructions:
1. Provide a clear, structured, engineering-grade answer.
2. Include clean, well-commented code examples if applicable.
3. Highlight architectural trade-offs and best practices.
4. Keep the explanation concise, accurate, and grounded in the research context."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        "draft_report": response.content,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def reviewer_node(state: AgentState) -> dict:
    """Node 3: Audits the generated draft for accuracy, completeness, and hallucinations."""
    llm = get_llm()
    prompt = f"""You are a Strict Technical Reviewer auditing an AI-generated engineering report.

Original User Query: {state['query']}

Generated Draft:
{state['draft_report']}

Evaluation Rules:
- Check if the draft directly answers all parts of the user query.
- Check for missing edge cases, vague explanations, or potential inaccuracies.
- If the draft is thorough, accurate, and ready for production, reply ONLY with: APPROVED
- Otherwise, provide 2-3 concise bullet points on what must be added or improved."""

    response = llm.invoke([HumanMessage(content=prompt)])
    decision = response.content.strip()

    if decision.upper().startswith("APPROVED") or state.get("revision_count", 0) >= 2:
        return {"is_approved": True, "critique": ""}
    return {"is_approved": False, "critique": decision}


def route_after_review(state: AgentState) -> str:
    """Conditional Edge: Terminates if approved or max revisions reached; otherwise loops back."""
    if state.get("is_approved", False):
        return END
    return "researcher"


def build_research_graph():
    """Builds and compiles the cyclic LangGraph workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", researcher_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("reviewer", reviewer_node)

    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "synthesizer")
    workflow.add_edge("synthesizer", "reviewer")
    workflow.add_conditional_edges("reviewer", route_after_review)

    return workflow.compile()


research_agent = build_research_graph()