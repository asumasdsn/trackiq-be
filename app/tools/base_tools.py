from langchain_core.tools import tool


@tool
def search_knowledge_base(query: str) -> str:
    """Useful for searching internal documentation and knowledge bases."""
    return f"Search results for: {query}"


@tool
def consult_expert(topic: str) -> str:
    """Useful when you need advice from a subject matter expert on a specific topic."""
    return f"Expert advice on {topic}"
