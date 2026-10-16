"""
llm.py

one shared llm object that every agent imports.
if you want to switch models, you only change it here (or in .env).
"""

from langchain_google_genai import ChatGoogleGenerativeAI

import config

llm = ChatGoogleGenerativeAI(
    model=config.MODEL,
    api_key=config.GOOGLE_API_KEY,
    temperature=0.3,  # low = more focused, less random
    max_retries=5,    # retry automatically if google is busy (503) or rate limits us (429)
)