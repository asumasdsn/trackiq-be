from langgraph.graph import StateGraph, END
from app.agents.research_agent.state import ResearchAgentState
from app.agents.research_agent.nodes import search_node, synthesize_node


def create_research_graph():
    """Assembles the multi-step StateGraph for Research Agent."""
    workflow = StateGraph(ResearchAgentState)

    # Nodes
    workflow.add_node("research", search_node)
    workflow.add_node("synthesize", synthesize_node)

    # Edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow


research_graph = create_research_graph()
