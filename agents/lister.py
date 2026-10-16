"""
agents/lister.py

the list agent.
input:  state["topic"]
output: state["subtopics"]
"""

from pydantic import BaseModel, Field

from llm import llm
from state import State


# the shape we want back from the llm.
# with_structured_output forces the llm to fill this exactly,
# so we get a real python list, not text we have to parse.
class SubtopicList(BaseModel):
    subtopics: list[str] = Field(description="4 to 6 short subtopic names")


PROMPT = """you are planning a study digest for students in an AI cohort.
break the topic below into 4 to 6 subtopics.

rules:
- each subtopic should be explainable in one short paragraph
- order them from basic to advanced
- no two subtopics should overlap

topic: {topic}"""

structured_llm = llm.with_structured_output(SubtopicList)


def list_agent(state: State) -> dict:
    result = structured_llm.invoke(PROMPT.format(topic=state["topic"]))

    print("\n[list agent] subtopics:")
    for i, sub in enumerate(result.subtopics, start=1):
        print(f"  {i}. {sub}")

    # an agent only returns the fields it changed.
    # langgraph merges this into the shared state for us.
    return {"subtopics": result.subtopics}