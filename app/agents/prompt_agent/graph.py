from langgraph.graph import StateGraph, END
from app.agents.prompt_agent.state import PromptAgentState
from app.agents.prompt_agent.nodes import call_model_node, finalize_node


def create_prompt_graph():
    """Assembles the StateGraph for the Prompt Agent."""
    workflow = StateGraph(PromptAgentState)

    # Add Nodes
    workflow.add_node("agent", call_model_node)
    workflow.add_node("finalize", finalize_node)

    # Define Edges
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", "finalize")
    workflow.add_edge("finalize", END)

    return workflow


# Export the uncompiled graph
prompt_graph = create_prompt_graph()
