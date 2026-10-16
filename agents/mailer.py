"""
agents/mailer.py

the mail agent.
the llm only writes the subject and a short intro.
the rest of the email is built by plain code, so the summaries and links
go out exactly as the research agents wrote them.

input:  state["topic"], state["subtopics"], state["findings"]
output: state["subject"], state["body"]
"""

from pydantic import BaseModel, Field

from llm import llm
from state import State


class Email(BaseModel):
    subject: str = Field(description="short email subject, under 8 words")
    intro: str = Field(description="2 to 3 friendly sentences introducing the digest")


PROMPT = """you are writing an email to students in an AI cohort.

this study digest is about: {topic}
it covers: {subtopics}

write a subject line and a short intro. plain and casual, no hype."""

structured_llm = llm.with_structured_output(Email)


def mail_agent(state: State) -> dict:
    email = structured_llm.invoke(
        PROMPT.format(topic=state["topic"], subtopics=", ".join(state["subtopics"]))
    )

    # {name} stays as a placeholder. the send step swaps in each person's name.
    parts = ["hi {name},", "", email.intro, ""]

    # go in the list agent's order (basic to advanced), not the order research finished in
    for i, sub in enumerate(state["subtopics"], start=1):
        finding = state["findings"][sub]
        parts.append(f"{i}. {sub}")
        parts.append(finding["summary"])
        parts.append("read more:")
        parts.extend(f"- {url}" for url in finding["sources"])
        parts.append("")

    parts.append("see you in class!")

    print("\n[mail agent] draft ready")
    return {"subject": email.subject, "body": "\n".join(parts)}