"""
config.py

loads everything from .env in one place,
so the rest of the code never calls os.getenv directly.
"""

import os

from dotenv import load_dotenv

# read the .env file and put its values into environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
MODEL = os.getenv("MODEL", "gemini-3.8-flash")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
# true = show the email but don't send it. set DRY_RUN=false in .env to really send.
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"


def check_keys() -> bool:
    """print which keys are set and which are missing. returns True if all are set."""
    keys = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "TAVILY_API_KEY": TAVILY_API_KEY,
        "GMAIL_ADDRESS": GMAIL_ADDRESS,
        "GMAIL_APP_PASSWORD": GMAIL_APP_PASSWORD,
    }

    all_set = True
    for name, value in keys.items():
        if value:
            print(f"  [ok]      {name}")
        else:
            print(f"  [missing] {name}")
            all_set = False

    return all_set