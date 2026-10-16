"""
agents/approval.py

human in the loop.
interrupt() pauses the whole graph and hands the draft to main.py.
the graph only continues when you answer.
"""

from langgraph.types import interrupt

from state import State


def approval(state: State) -> dict:
    answer = interrupt({"subject": state["subject"], "body": state["body"]})
    return {"approved": answer.strip().lower() in ("y", "yes")}