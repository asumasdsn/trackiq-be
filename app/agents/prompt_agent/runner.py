from app.agents.prompt_agent.graph import prompt_graph
from app.core.checkpointer import get_checkpointer


class PromptAgentRunner:
    """Handles the execution lifecycle of the Prompt Agent."""

    def __init__(self):
        self.checkpointer = get_checkpointer()
        self.app = prompt_graph.compile(checkpointer=self.checkpointer)

    async def run(self, input_data: dict, thread_id: str):
        """Invoke the agent with a specific thread context."""
        config = {"configurable": {"thread_id": thread_id}}
        return await self.app.ainvoke(input_data, config=config)

    async def stream(self, input_data: dict, thread_id: str):
        """Stream graph steps as they occur."""
        config = {"configurable": {"thread_id": thread_id}}
        async for event in self.app.astream(input_data, config=config):
            yield event
