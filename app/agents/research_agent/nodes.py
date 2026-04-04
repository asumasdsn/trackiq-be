from langchain_core.messages import AIMessage
from app.agents.research_agent.state import ResearchAgentState
from app.tools.base_tools import search_knowledge_base


async def search_node(state: ResearchAgentState):
    """
    Simulated node that uses tools to fetch external research.
    """
    topic = state.get("current_topic", "General AI")
    # Using the search tool we created earlier
    raw_data = search_knowledge_base.invoke({"query": topic})
    
    return {
        "research_notes": [raw_data],
        "messages": [AIMessage(content=f"I have conducted research on: {topic}")]
    }


async def synthesize_node(state: ResearchAgentState):
    """
    Node that synthesizes research notes into a final summary.
    """
    notes = state.get("research_notes", [])
    summary = f"Summary of findings: {' | '.join(notes)}"
    
    return {
        "messages": [AIMessage(content=f"Research complete. {summary}")],
        "is_complete": True
    }
