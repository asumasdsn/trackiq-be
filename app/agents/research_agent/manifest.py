from typing import Dict, Any

AGENT_MANIFEST: Dict[str, Any] = {
    "id": "research-agent-v1",
    "name": "Research Analyst",
    "description": "Agent specialized in gathering data and synthesizing complex summaries.",
    "version": "1.0.0",
    "required_tools": ["search_knowledge_base"],
    "system_prompt": "You are a world-class research analyst."
}
