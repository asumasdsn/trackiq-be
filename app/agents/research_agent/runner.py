from app.agents.research_agent.graph import research_graph
from app.core.checkpointer import get_checkpointer


class ResearchAgentRunner:
    """Handles execution for the modular Research Agent."""

    def __init__(self):
        self.checkpointer = get_checkpointer()
        self.app = research_graph.compile(checkpointer=self.checkpointer)

    async def run(self, input_data: dict, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        return await self.app.ainvoke(input_data, config=config)
