from langchain_core.messages import AIMessage
from app.agents.prompt_agent.state import PromptAgentState


async def call_model_node(state: PromptAgentState):
    """Node that invokes the LLM to generate a response."""
    # Logic to call LLM would go here
    return {
        "messages": [AIMessage(content="Hello! I am your modular prompt agent.")],
        "iteration_count": state.get("iteration_count", 0) + 1
    }


async def finalize_node(state: PromptAgentState):
    """Node to perform final cleanup or formatting before finishing."""
    return {"is_complete": True}
