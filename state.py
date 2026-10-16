"""
state.py

the shared memory of the system.
every agent reads from this and writes back to it.
we add more fields in later steps.
"""

from typing import Annotated, TypedDict


class Finding(TypedDict):
    summary: str        # written by the llm
    sources: list[str]  # urls, straight from the search tool


def merge_findings(old: dict, new: dict) -> dict:
    """
    a reducer: tells langgraph how to combine updates to the same field.

    5 research agents run at once, and each returns {"findings": {its_subtopic: ...}}.
    without this, langgraph doesn't know which one to keep and throws an error.
    with this, it merges them all into one dict.
    """
    return {**(old or {}), **(new or {})}


class State(TypedDict):
    topic: str                                            # what the user typed, e.g. "RAG"
    subtopics: list[str]                                  # filled by the list agent
    findings: Annotated[dict[str, Finding], merge_findings]  # filled by research agents, merged


class ResearchTask(TypedDict):
    """the small input each parallel research agent gets. not the whole state."""
    topic: str
    subtopic: str