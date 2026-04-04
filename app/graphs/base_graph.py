from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "Addable"]
    next_step: str


def create_base_graph():
    """Template function to create a stateful LangGraph graph."""
    workflow = StateGraph(AgentState)
    
    # Define Nodes
    # workflow.add_node("agent", call_model)
    # workflow.add_node("action", call_tool)
    
    # Define Edges
    # workflow.set_entry_point("agent")
    # workflow.add_conditional_edges(...)
    
    return workflow
