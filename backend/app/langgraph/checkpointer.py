"""
Checkpointer abstraction layer for GoalPilot LangGraph workflows.

Centralizes the checkpointer instance so graph.py is decoupled from the
specific saver implementation. To swap storage backends, only this file
needs to change — no workflow logic is affected.

Current backend: MemorySaver (in-process, non-persistent)

Future backends (drop-in replacements):
    from langgraph.checkpoint.postgres import PostgresSaver
    from langgraph.checkpoint.redis import RedisSaver
"""

from langgraph.checkpoint.memory import MemorySaver

# Single shared checkpointer instance used by the compiled workflow.
# Replace MemorySaver() with PostgresSaver(...) or RedisSaver(...)
# to enable persistent, cross-session workflow recovery.
checkpointer = MemorySaver()
