# step-1: shared state + list agent

## what this branch does

adds the first agent. you give it a topic, and it returns 4 to 6 subtopics, ordered from basic to advanced.

```
START -> list -> END
```

## run it

```bash
uv run main.py "RAG"
```

you should see a numbered list of subtopics, then the final state with `topic` and `subtopics` in it.

## what changed from step-0

| file | change |
|---|---|
| `state.py` | **new.** the shared state: `topic` and `subtopics` |
| `agents/__init__.py` | **new.** makes `agents` a python package |
| `agents/lister.py` | **new.** the list agent |
| `graph.py` | **new.** wires agents into a langgraph graph |
| `main.py` | **changed.** takes a topic and runs the graph instead of the key check |
| `llm.py` | **changed.** `max_retries=5` so busy (503) or rate limit (429) errors retry on their own |

## why each piece matters

- **`State`** is the shared memory. every agent reads from it and writes back to it, and it grows as agents work.
- **pydantic + `with_structured_output`** forces the llm to return a real python list instead of text we'd have to parse. agents pass data to each other, so the data needs a fixed shape.
- **agents return only the fields they changed** (`{"subtopics": ...}`). langgraph merges that into the state.
- **`RetryPolicy`** in `graph.py` reruns a whole agent if it fails. `max_retries` in `llm.py` retries a single api call. those are two different layers.