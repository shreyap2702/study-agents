"""
agents/researcher.py

the research agent.
input:  state["topic"], state["subtopics"]
output: state["findings"]
"""

from llm import llm
from state import State
from tools import web_search

PROMPT = """you are writing one section of a study digest for students in an AI cohort.

main topic: {topic}
subtopic: {subtopic}

using only the search results below, explain the subtopic in 80 to 120 words.
write simply, for a beginner. start directly with the explanation.

search results:
{results}"""


def research_one(topic: str, subtopic: str) -> dict:
    """research a single subtopic: search the web, then summarize."""
    results = web_search(f"{subtopic} in {topic}")

    # turn the search results into plain text the llm can read
    results_text = "\n\n".join(
        f"[{i}] {r['title']}\n{r['content']}" for i, r in enumerate(results, start=1)
    )

    reply = llm.invoke(
        PROMPT.format(topic=topic, subtopic=subtopic, results=results_text)
    )

    return {
        "summary": reply.text,
        # sources come from the search tool, not the llm.
        # if we asked the llm for links, it could make them up.
        "sources": [r["url"] for r in results],
    }


def research_agent(state: State) -> dict:
    """research every subtopic, one after another."""
    findings = {}

    for subtopic in state["subtopics"]:
        print(f"\n[research agent] researching: {subtopic}")
        findings[subtopic] = research_one(state["topic"], subtopic)

    return {"findings": findings}