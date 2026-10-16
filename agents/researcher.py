"""
agents/researcher.py

the research agent.
each copy researches ONE subtopic. the graph runs one copy per subtopic, in parallel.
on a redo, it also gets the reviewer's feedback.

input:  a ResearchTask {topic, subtopic, feedback}
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
{feedback}
search results:
{results}"""


def research_one(topic: str, subtopic: str, feedback: str = "") -> dict:
    """research a single subtopic: search the web, then summarize."""
    results = web_search(f"{subtopic} in {topic}")

    # turn the search results into plain text the llm can read
    results_text = "\n\n".join(
        f"[{i}] {r['title']}\n{r['content']}" for i, r in enumerate(results, start=1)
    )

    # only add the feedback line if the reviewer sent this back
    feedback_line = f"\na reviewer rejected your last try. fix this: {feedback}\n" if feedback else ""

    reply = llm.invoke(
        PROMPT.format(topic=topic, subtopic=subtopic, feedback=feedback_line, results=results_text)
    )

    return {
        "summary": reply.text,
        # sources come from the search tool, not the llm, so they can't be made up
        "sources": [r["url"] for r in results],
    }


def research_agent(task: ResearchTask) -> dict:
    subtopic = task["subtopic"]
    feedback = task.get("feedback", "")

    label = "redo" if feedback else "start"
    print(f"[research agent] {label}: {subtopic}")
    finding = research_one(task["topic"], subtopic, feedback)
    print(f"[research agent] done:  {subtopic}")

    return {"findings": {subtopic: finding}}