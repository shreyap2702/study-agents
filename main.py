"""
main.py

run it with:
  uv run main.py "RAG"
"""

import sys

from graph import build_graph


def main():
    # take the topic from the command line, or ask for it
    topic = " ".join(sys.argv[1:]) or input("topic: ").strip()

    app = build_graph()
    final_state = app.invoke({"topic": topic})

    print("\nfinal state:")
    print(final_state)


if __name__ == "__main__":
    main()