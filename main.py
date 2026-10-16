"""
main.py

run it with:
  uv run main.py "RAG"
"""

import sys
import time

from graph import build_graph


def main():
    # take the topic from the command line, or ask for it
    topic = " ".join(sys.argv[1:]) or input("topic: ").strip()

    app = build_graph()

    start = time.time()
    final_state = app.invoke({"topic": topic})
    took = time.time() - start

    for subtopic, finding in final_state["findings"].items():
        print(f"\n## {subtopic}")
        print(finding["summary"])
        for url in finding["sources"]:
            print(f"  - {url}")

    print(f"\ntook {took:.1f}s")


if __name__ == "__main__":
    main()