from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class PromptAgentState(TypedDict):
    """
    Schema for the Prompt Agent's internal state.
    'messages' uses 'add_messages' to append new messages instead of overwriting.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    context: dict
    iteration_count: int
    is_complete: bool
