"""
state.py

the shared memory of the system.
every agent reads from this and writes back to it.
we add more fields in later steps.
"""

from typing import TypedDict


class Finding(TypedDict):
    summary: str        # written by the llm
    sources: list[str]  # urls, straight from the search tool


class State(TypedDict):
    topic: str                     # what the user typed, e.g. "RAG"
    subtopics: list[str]           # filled by the list agent
    findings: dict[str, Finding]   # filled by the research agent, keyed by subtopic