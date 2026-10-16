# Study Agents

A multi-agent system built with LangGraph. Give it a topic and it researches the topic, reviews the research, writes an email digest, asks for your approval, and mails it to your cohort.

```bash
uv run main.py "RAG"
```

## Graph

```
                 START
                   │
                   ▼
                 list
                   │
                   │  send_to_research()  ── fan-out with Send
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   research    research    research      one node instance per subtopic
       └───────────┼───────────┘
                   │                     fan-in via merge_findings reducer
                   ▼
               reviewer
                   │
                   │  after_review()
          ┌────────┴────────┐
          │                 │
   rejected and        all approved or
   attempts < 2        out of attempts
          │                 │
          ▼                 ▼
   research (only         mail
   rejected ones)           │
          │                 ▼
          └──► reviewer  approval        interrupt() pauses the graph
                            │
                            │  after_approval()
                     ┌──────┴──────┐
                    yes            no
                     │             │
                     ▼             ▼
                   send           END
                     │
                     ▼
                    END
```

## Nodes

| Node | Type | Reads | Writes |
|---|---|---|---|
| `list` | LLM, structured output | `topic` | `subtopics` |
| `research` | LLM + Tavily tool | `ResearchTask` | `findings[subtopic]` |
| `reviewer` | LLM, structured output | `findings` | `rejected`, `feedback`, `attempts` |
| `mail` | LLM, structured output | `subtopics`, `findings` | `subject`, `body` |
| `approval` | Human (`interrupt`) | `subject`, `body` | `approved` |
| `send` | Plain code, no LLM | `subject`, `body`, `cohort.csv` | `sent` |

## Edges

| From | To | Type |
|---|---|---|
| `START` | `list` | Normal |
| `list` | `research` | Conditional, returns one `Send` per subtopic |
| `research` | `reviewer` | Normal, waits for all parallel branches |
| `reviewer` | `research` or `mail` | Conditional, `after_review()` |
| `mail` | `approval` | Normal |
| `approval` | `send` or `END` | Conditional, `after_approval()` |
| `send` | `END` | Normal |

## State

All agents share one `State` object. Each node returns only the fields it changes, and LangGraph merges them in.

```python
class State(TypedDict):
    topic: str
    subtopics: list[str]
    findings: Annotated[dict[str, Finding], merge_findings]  # reducer
    rejected: list[str]
    feedback: dict[str, str]
    attempts: int
    subject: str
    body: str
    approved: bool
    sent: int
```

- **`findings` has a reducer.** Parallel research agents write to it at the same time, and `merge_findings` combines their results into one dict.
- **`findings` is keyed by subtopic,** so a redo overwrites the old finding instead of adding a duplicate.
- **Parallel agents get a `ResearchTask`** (`topic`, `subtopic`, `feedback`), not the full state.

## Patterns Used

| Pattern | Where | How |
|---|---|---|
| Orchestrator and workers | `list` → `research` | The list agent plans, and the workers execute in parallel |
| Fan-out / fan-in | `send_to_research()`, `merge_findings` | `Send` spawns workers, and the reducer merges their output |
| Reflection loop | `reviewer` → `research` | Rejected work goes back with feedback, capped by `MAX_REVIEWS` |
| Human in the loop | `approval` | `interrupt()` pauses, and `Command(resume=...)` continues |
| Checkpointing | `graph.compile()` | `InMemorySaver` and a `thread_id` save state across the pause |
| Structured output | `list`, `reviewer`, `mail` | Pydantic schemas force typed responses that code can branch on |

## Design Decisions

- **Agents decide, code acts.** Sending email is plain code behind human approval, never an LLM call.
- **Sources come from the search tool, not the LLM,** so links can't be made up.
- **The mail agent writes only the subject and intro.** The summaries and links are assembled by code exactly as researched.
- **Targeted retries.** Only rejected subtopics are researched again, which saves tokens and time.
- **Bounded loops.** `MAX_REVIEWS = 2` prevents the reviewer from looping forever.
- **No retry on `send`.** A retry after a partial send would email people twice.
- **Two retry layers.** `max_retries` in `llm.py` retries a single API call, and `RetryPolicy` in `graph.py` retries a whole node.
- **`DRY_RUN` defaults to `true`,** so the full pipeline can be tested without sending anything.

## File Structure

```
study-agents/
├── main.py              CLI entry. Runs the graph, handles the approval pause and resume
├── graph.py             Nodes, edges, routing functions, checkpointer
├── state.py             Shared State, Finding, ResearchTask, merge_findings reducer
├── config.py            Loads .env in one place
├── llm.py               Shared Gemini client used by every agent
├── tools.py             web_search() via Tavily
├── agents/
│   ├── lister.py        List agent
│   ├── researcher.py    Research agent
│   ├── reviewer.py      Reviewer agent
│   ├── mailer.py        Mail agent
│   ├── approval.py      Human approval with interrupt()
│   └── sender.py        Gmail SMTP send and dry run
├── .env.example         Template for API keys and settings
├── cohort.csv           Recipients (gitignored)
└── pyproject.toml       Dependencies
```

## Setup

```bash
git clone https://github.com/shreyap2702/study-agents.git
cd study-agents
uv sync
cp .env.example .env
```

Fill in `.env`:

- `GOOGLE_API_KEY` from [AI Studio](https://aistudio.google.com/apikey)
- `TAVILY_API_KEY` from [Tavily](https://app.tavily.com)
- `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` (turn on 2-step verification, then create an [app password](https://myaccount.google.com/apppasswords))

Create `cohort.csv` in the root folder:

```
name,email
Shreya,you@gmail.com
```

Run:

```bash
uv run main.py "RAG"
```

Set `DRY_RUN=false` in `.env` to send real emails.

## Branches

Each branch adds one piece of the system and has its own README.

| Branch | Adds |
|---|---|
| `step-0` | Setup and key check |
| `step-1` | Shared state and list agent |
| `step-2` | Research agent with web search |
| `step-3` | Parallel research with `Send` |
| `step-4` | Reviewer agent and retry loop |
| `step-5` | Mail agent, human approval, and Gmail send |

## Stack

LangGraph, Gemini, Tavily, Gmail SMTP, uv