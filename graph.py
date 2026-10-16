"""
graph.py

wires the agents together.

START -> list -> research (x N, parallel) -> reviewer
reviewer -> research (only the rejected ones)   if something was rejected
reviewer -> mail                                if all good, or out of tries
mail -> approval (pauses for you) -> send or END
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy, Send

from agents.approval import approval
from agents.lister import list_agent
from agents.mailer import mail_agent
from agents.researcher import research_agent
from agents.reviewer import MAX_REVIEWS, reviewer_agent
from agents.sender import send_mail
from state import State


def send_to_research(state: State) -> list[Send]:
    """fan out: one research agent per subtopic."""
    return [
        Send("research", {"topic": state["topic"], "subtopic": sub, "feedback": ""})
        for sub in state["subtopics"]
    ]


def after_review(state: State):
    """redo the rejected subtopics, or move on to the mail agent."""
    if state["rejected"] and state["attempts"] < MAX_REVIEWS:
        return [
            Send("research", {"topic": state["topic"], "subtopic": sub, "feedback": state["feedback"][sub]})
            for sub in state["rejected"]
        ]
    return "mail"


def after_approval(state: State):
    return "send" if state["approved"] else END


def build_graph():
    graph = StateGraph(State)

    # if an agent fails, langgraph runs it again (up to 3 times)
    retry = RetryPolicy(max_attempts=3)

    graph.add_node("list", list_agent, retry_policy=retry)
    graph.add_node("research", research_agent, retry_policy=retry)
    graph.add_node("reviewer", reviewer_agent, retry_policy=retry)
    graph.add_node("mail", mail_agent, retry_policy=retry)
    graph.add_node("approval", approval)
    graph.add_node("send", send_mail)  # no retry here: a retry could email everyone twice

    graph.add_edge(START, "list")
    graph.add_conditional_edges("list", send_to_research, ["research"])
    graph.add_edge("research", "reviewer")
    graph.add_conditional_edges("reviewer", after_review, ["research", "mail"])
    graph.add_edge("mail", "approval")
    graph.add_conditional_edges("approval", after_approval, ["send", END])
    graph.add_edge("send", END)

    # the checkpointer saves state, so the graph can pause at approval and resume later
    return graph.compile(checkpointer=InMemorySaver())