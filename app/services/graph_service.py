from typing import Any, Dict, Optional
from langgraph.graph import StateGraph
from app.core.checkpointer import get_checkpointer


class GraphService:
    def __init__(self):
        self.graphs: Dict[str, StateGraph] = {}
        self.checkpointer = get_checkpointer()

    def register_graph(self, name: str, graph: StateGraph):
        self.graphs[name] = graph

    async def run_graph(self, graph_name: str, input_data: Dict[str, Any], thread_id: str):
        if graph_name not in self.graphs:
            raise ValueError(f"Graph {graph_name} not found")
        
        compiled_graph = self.graphs[graph_name].compile(checkpointer=self.checkpointer)
        config = {"configurable": {"thread_id": thread_id}}
        
        result = await compiled_graph.ainvoke(input_data, config=config)
        return result

    def get_state(self, graph_name: str, thread_id: str):
        if graph_name not in self.graphs:
            return None
        compiled_graph = self.graphs[graph_name].compile(checkpointer=self.checkpointer)
        config = {"configurable": {"thread_id": thread_id}}
        return compiled_graph.get_state(config)
