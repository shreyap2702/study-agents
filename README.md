# step-0: setup

## what this branch does

sets up the project and checks that everything works before we write any agents: python packages, api keys, and one test call to the llm.

## run it

1. install uv: https://docs.astral.sh/uv/getting-started/installation/

2. install packages

```bash
   uv sync
```

3. make your `.env`

```bash
   cp .env.example .env
```

   fill in:
   - `GOOGLE_API_KEY`: https://aistudio.google.com/apikey
   - `TAVILY_API_KEY`: https://app.tavily.com
   - `GMAIL_ADDRESS`: your gmail
   - `GMAIL_APP_PASSWORD`: turn on 2-step verification, then make one at https://myaccount.google.com/apppasswords (16 letters, no spaces)
   - `MODEL`: `gemini-3.5-flash-lite`

4. make `cohort.csv` in the root folder

```
   name,email
   yourname,you@gmail.com
```

5. run

```bash
   uv run main.py
```

you should see all 4 keys as `[ok]` and a one-line hi from the llm.

## what's in this branch

| file | why it's here |
|---|---|
| `pyproject.toml` | every package for all steps, installed once so nothing breaks mid-session |
| `.env.example` | template for your keys. you copy it to `.env`, which never gets pushed |
| `.gitignore` | keeps `.env` (keys) and `cohort.csv` (real emails) off github |
| `config.py` | reads `.env` in one place, so no other file touches `os.getenv` |
| `llm.py` | one shared llm every agent imports. change the model here or in `.env` |
| `main.py` | checks the keys and makes one test call to the llm |

## worth knowing

- model names change often. keeping `MODEL` in `.env` makes a model change a one-line fix.
- newer gemini models return a list of blocks, so we use `reply.text` instead of `reply.content`.