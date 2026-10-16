"""
tools.py

tools are plain functions that agents use to act on the world.
an agent decides, a tool does.
"""

from tavily import TavilyClient

import config

client = TavilyClient(api_key=config.TAVILY_API_KEY)


def web_search(query: str, max_results: int = 3) -> list[dict]:
    """search the web and return a list of {title, url, content}."""
    response = client.search(query=query, max_results=max_results)

    return [
        {"title": r["title"], "url": r["url"], "content": r["content"]}
        for r in response["results"]
    ]