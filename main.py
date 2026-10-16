"""
main.py

step-0: just check that the setup works.
  1. are all keys in .env?
  2. can we talk to the llm?

run it with:
  uv run main.py
"""

import config


def main():
    print("checking .env ...")
    if not config.check_keys():
        print("\nsome keys are missing. copy .env.example to .env and fill them in.")
        return

    print("\nchecking the llm ...")
    from llm import llm  # imported here so a missing key fails with a clear message above

    reply = llm.invoke("say hi to the cohort in one short line")
    print(f"  llm says: {reply.content}")

    print("\nsetup done. checkout step-1 next.")


if __name__ == "__main__":
    main()