"""
graph.py

wires the agents together.

START -> list -> research (x N, in parallel) -> END
"""

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy, Send

from agents.lister import list_agent
from agents.researcher import research_agent
from state import State


def send_to_research(state: State) -> list[Send]:
    """
    fan out: one Send per subtopic.
    each Send starts a separate copy of the research agent with its own small input.
    """
    return [
        Send("research", {"topic": state["topic"], "subtopic": subtopic})
        for subtopic in state["subtopics"]
    ]


def build_graph():
    graph = StateGraph(State)

    # if the whole agent fails, langgraph runs it again (up to 3 times)
    retry = RetryPolicy(max_attempts=3)

    graph.add_node("list", list_agent, retry_policy=retry)
    graph.add_node("research", research_agent, retry_policy=retry)

    graph.add_edge(START, "list")

    # instead of a normal edge, list -> research is decided at runtime:
    # however many subtopics there are, that many research agents start.
    graph.add_conditional_edges("list", send_to_research, ["research"])

    # langgraph waits for ALL research agents to finish before moving on
    graph.add_edge("research", END)

    return graph.compile()