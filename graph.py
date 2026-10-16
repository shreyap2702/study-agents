from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from agents.lister import list_agent
from state import State


def build_graph():
    graph = StateGraph(State)

    # if the whole agent fails, langgraph runs it again (up to 3 times)
    retry = RetryPolicy(max_attempts=3)

    graph.add_node("list", list_agent, retry_policy=retry)

    graph.add_edge(START, "list")
    graph.add_edge("list", END)

    return graph.compile()