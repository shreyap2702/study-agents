"""
state.py

the shared memory of the system.
every agent reads from this and writes back to it.
"""

from typing import Annotated, TypedDict


class Finding(TypedDict):
    summary: str        # written by the llm
    sources: list[str]  # urls, straight from the search tool


def merge_findings(old: dict, new: dict) -> dict:
    """
    a reducer: tells langgraph how to combine updates to the same field.
    many research agents return findings at once, this merges them into one dict.
    a redo of a subtopic overwrites its old finding.
    """
    return {**(old or {}), **(new or {})}


class State(TypedDict):
    topic: str                                               # what the user typed
    subtopics: list[str]                                     # list agent
    findings: Annotated[dict[str, Finding], merge_findings]  # research agents
    rejected: list[str]                                      # reviewer: subtopics to redo
    feedback: dict[str, str]                                 # reviewer: what to fix, per subtopic
    attempts: int                                            # reviewer: how many reviews so far
    subject: str                                             # mail agent
    body: str                                                # mail agent
    approved: bool                                           # you, at the approval step
    sent: int                                                # send step


class ResearchTask(TypedDict):
    """the small input each parallel research agent gets. not the whole state."""
    topic: str
    subtopic: str
    feedback: str  # empty on the first try, the reviewer's note on a redo