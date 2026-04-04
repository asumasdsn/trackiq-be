from langgraph.checkpoint.memory import MemorySaver
# Swap for RedisCheckpointer or SqliteSaver in production

# In-memory checkpointer (stateful multi-turn conversations)
memory_checkpointer = MemorySaver()


def get_checkpointer():
    """Return the configured LangGraph checkpointer."""
    return memory_checkpointer
