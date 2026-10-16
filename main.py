"""
main.py

run it with:
  uv run main.py "RAG"
"""

import sys
import uuid

from langgraph.types import Command

from graph import build_graph


def main():
    topic = " ".join(sys.argv[1:]) or input("topic: ").strip()

    app = build_graph()

    # a thread id lets the checkpointer find this run again when we resume
    run_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    result = app.invoke({"topic": topic}, run_config)

    # the graph paused at the approval step. show the draft and ask.
    if "__interrupt__" in result:
        draft = result["__interrupt__"][0].value

        print("\n" + "=" * 60)
        print(f"subject: {draft['subject']}\n")
        print(draft["body"].replace("{name}", "<name>"))
        print("=" * 60)

        answer = input("\nsend this to the cohort? (yes/no): ")

        # resume the graph from where it paused, with your answer
        result = app.invoke(Command(resume=answer), run_config)

    print(f"\ndone. emails sent: {result.get('sent', 0)}")


if __name__ == "__main__":
    main()