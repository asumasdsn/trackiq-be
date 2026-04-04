from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ResearchAgentState(TypedDict):
    """
    Schema for the Research Agent's state.
    'research_notes' stores accumulated data from external searches.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    research_notes: List[str]
    current_topic: str
    is_complete: bool
