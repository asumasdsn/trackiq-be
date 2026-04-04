from typing import Dict, Any

AGENT_MANIFEST: Dict[str, Any] = {
    "id": "prompt-agent-v1",
    "name": "Prompt Engineering Assistant",
    "description": "Specialized agent for refining and optimizing user prompts.",
    "version": "1.0.0",
    "default_params": {
        "temperature": 0.7,
        "max_tokens": 2048,
        "model": "gpt-4o"
    },
    "system_prompt": "You are an expert prompt engineer. Your goal is to improve usability and clarity."
}
