# step-3: parallel research with Send

## what this branch does

instead of one research agent going through every subtopic, each subtopic now gets its **own** research agent, and they all run at the same time.

```
START -> list -> research (x N, in parallel) -> END
```

## run it

```bash
uv run main.py "RAG"
```

you'll see all the `start:` lines first, then the `done:` lines in random order. compare the time with step-2, it should be much faster.

## what changed from step-2

| file | change |
|---|---|
| `state.py` | **changed.** `findings` now has a reducer (`merge_findings`), and there's a new `ResearchTask` type |
| `agents/researcher.py` | **changed.** `research_agent` handles one subtopic instead of looping over all of them |
| `graph.py` | **changed.** `send_to_research()` fans out with `Send`, and list → research is now a conditional edge |

## why each piece matters

- **`Send` is fan-out.** the number of agents isn't hardcoded. it's however many subtopics the list agent returned.
- **`ResearchTask`**: each parallel agent gets only the input it needs, not the whole state.
- **the reducer is fan-in.** several agents write to `findings` at once, and `merge_findings` tells langgraph how to combine them. without it, langgraph throws `InvalidUpdateError`.
- **langgraph waits for every research agent** to finish before moving to the next node.
- **trade-off:** parallel means more llm calls at the same moment, so you're more likely to hit rate limits. `max_retries` covers that.

## try this

remove `Annotated[..., merge_findings]` from `findings` in `state.py` and run it. you'll get `InvalidUpdateError`. put it back.