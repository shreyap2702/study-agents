"""
agents/reviewer.py

the reviewer agent.
checks every research summary and sends weak ones back to the research agent.

input:  state["findings"]
output: state["rejected"], state["feedback"], state["attempts"]
"""

from pydantic import BaseModel, Field

from llm import llm
from state import State

MAX_REVIEWS = 2  # review once, allow one round of redos, then move on no matter what


class Verdict(BaseModel):
    subtopic: str = Field(description="the subtopic name, exactly as given")
    approved: bool
    reason: str = Field(description="if rejected, one specific thing to fix. empty if approved")


class Review(BaseModel):
    verdicts: list[Verdict]


PROMPT = """you are a strict reviewer for a study digest that goes to students.

main topic: {topic}

check each section below. reject a section if:
- it doesn't actually explain its subtopic
- it is vague or full of buzzwords
- it is longer than 150 words
otherwise approve it.

sections:
{sections}"""

structured_llm = llm.with_structured_output(Review)


def reviewer_agent(state: State) -> dict:
    findings = state["findings"]
    attempts = state.get("attempts", 0) + 1

    # first review: check everything. after that: only the ones that were redone.
    to_review = state.get("rejected") or list(findings)

    sections = "\n\n".join(f"### {sub}\n{findings[sub]['summary']}" for sub in to_review)
    review = structured_llm.invoke(PROMPT.format(topic=state["topic"], sections=sections))

    rejected, feedback = [], {}
    for verdict in review.verdicts:
        # ignore any subtopic name the llm got wrong
        if not verdict.approved and verdict.subtopic in findings:
            rejected.append(verdict.subtopic)
            feedback[verdict.subtopic] = verdict.reason

    print(f"\n[reviewer] review {attempts}: {len(to_review) - len(rejected)} approved, {len(rejected)} rejected")
    for sub in rejected:
        print(f"  - {sub}: {feedback[sub]}")

    return {"rejected": rejected, "feedback": feedback, "attempts": attempts}