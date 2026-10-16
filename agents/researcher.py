"""
agents/researcher.py

the research agent.
each copy of this agent researches ONE subtopic.
the graph starts one copy per subtopic, all in parallel.

input:  a ResearchTask {topic, subtopic}
output: state["findings"] (just its own subtopic)
"""

from llm import llm
from state import ResearchTask
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


def research_agent(task: ResearchTask) -> dict:
    """research one subtopic. many of these run at the same time."""
    subtopic = task["subtopic"]

    print(f"[research agent] start: {subtopic}")
    finding = research_one(task["topic"], subtopic)
    print(f"[research agent] done:  {subtopic}")

    # only return this agent's own piece. the reducer merges all of them.
    return {"findings": {subtopic: finding}}