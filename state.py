"""
state.py

the shared memory of the system.
every agent reads from this and writes back to it.
we add more fields in later steps.
"""

from typing import TypedDict


class State(TypedDict):
    topic: str             # what the user typed, e.g. "RAG"
    subtopics: list[str]   # filled by the list agent