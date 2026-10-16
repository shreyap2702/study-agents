# step-4: reviewer + retry loop

## what this branch does

adds a reviewer agent that checks every summary. weak ones go back to the research agent with feedback on what to fix. only the rejected subtopics get redone, and only once.

```
START -> list -> research (x N) -> reviewer
reviewer -> research (only rejected ones)   if something was rejected
reviewer -> END                             if all good, or out of tries
```

## run it

```bash
uv run main.py "RAG"
```

you should see the reviewer's verdict (how many approved, how many rejected and why). if anything is rejected, you'll see `redo:` lines and then a second review.

## what changed from step-3

| file | change |
|---|---|
| `agents/reviewer.py` | **new.** the reviewer agent |
| `state.py` | **changed.** adds `rejected`, `feedback` and `attempts`. `ResearchTask` gets `feedback` |
| `agents/researcher.py` | **changed.** adds the reviewer's feedback to the prompt on a redo |
| `graph.py` | **changed.** research → reviewer, plus `after_review()` to loop back or finish |

## why each piece matters

- **the reviewer uses structured output** (`approved: bool`, `reason: str`), so the graph can branch on it with plain code.
- **targeted retries:** only rejected subtopics go back. that saves tokens and time compared to redoing the whole batch.
- **feedback travels with the retry**, so the research agent knows what to fix instead of guessing.
- **`MAX_REVIEWS` stops infinite loops.** without a limit, a strict reviewer and a weak model can loop forever.
- **the reducer pays off here:** a redo overwrites only that subtopic's old finding.
- **reviews after the first only check redone subtopics**, so approved ones don't get re-judged.


# step-5: mail agent + human approval + gmail send

## what this branch does

completes the system. a mail agent writes the digest, the graph **pauses** to show you the draft, and only if you say yes does it email everyone in `cohort.csv`.

```
START -> list -> research (x N) -> reviewer -> (redo loop)
      -> mail -> approval (pauses for you) -> send -> END
                                           -> END (if you say no)
```

## run it

1. keep `DRY_RUN=true` in `.env` for the first run

```bash
   uv run main.py "RAG"
```

   read the draft and type `yes`. it prints who it **would** have mailed.

2. for a real send, set `DRY_RUN=false`, keep only your own email in `cohort.csv`, and run again. check your spam folder too.

## what changed from step-4

| file | change |
|---|---|
| `agents/mailer.py` | **new.** the mail agent writes the subject and intro, and code builds the rest |
| `agents/approval.py` | **new.** `interrupt()` pauses the graph for a human yes/no |
| `agents/sender.py` | **new.** reads `cohort.csv`, sends through gmail smtp, handles dry run |
| `config.py` | **changed.** adds `DRY_RUN` |
| `.env.example` | **changed.** adds `DRY_RUN=true` |
| `state.py` | uses `subject`, `body`, `approved`, `sent` |
| `graph.py` | **changed.** adds mail → approval → send, the checkpointer, and `after_approval()` |
| `main.py` | **changed.** catches the pause, shows the draft, asks you, resumes with `Command(resume=...)` |

## why each piece matters

- **the llm writes only the subject and intro.** summaries and links go out exactly as researched, so nothing gets rewritten or made up at the last step.
- **`{name}` placeholder:** one draft, personalised per person with no extra llm calls.
- **`interrupt()` is human in the loop.** the graph stops and waits. agents can draft, but a human approves anything that leaves the system.
- **the checkpointer (`InMemorySaver`) and `thread_id`** save the state at the pause, so the graph can resume from exactly where it stopped.
- **sending is plain code, not an llm.** agents decide, deterministic code does the risky action.
- **no retry on `send`.** a retry after a half-finished send would email people twice.
- **`DRY_RUN`** lets you test the whole pipeline without mailing anyone.