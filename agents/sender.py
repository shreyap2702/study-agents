"""
agents/sender.py

the send step. no llm here, on purpose.
agents decide what to say. plain code does the risky action.
"""

import csv
import smtplib
from email.message import EmailMessage

import config
from state import State


def load_cohort(path: str = "cohort.csv") -> list[dict]:
    """read cohort.csv into a list of {name, email}."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def send_mail(state: State) -> dict:
    people = load_cohort()

    if config.DRY_RUN:
        print(f"\n[send] dry run, not sending. would have mailed {len(people)} people:")
        for person in people:
            print(f"  - {person['name']} <{person['email']}>")
        return {"sent": 0}

    # log in to gmail once, then send one personalised email per person
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)

        for person in people:
            msg = EmailMessage()
            msg["From"] = config.GMAIL_ADDRESS
            msg["To"] = person["email"]
            msg["Subject"] = state["subject"]
            msg.set_content(state["body"].replace("{name}", person["name"]))

            server.send_message(msg)
            print(f"[send] sent to {person['email']}")

    return {"sent": len(people)}