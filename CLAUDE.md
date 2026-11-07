# probable-cause

Agentic RAG system over NTSB aviation accident data.

## What it does

Answers questions about US aviation accidents for safety analysts: what caused a specific accident, patterns across similar accidents, and statistics (e.g., "how many fatal Cessna 172 accidents in 2022?"). Every answer is grounded in official NTSB data with citations to accident IDs, and the agent declines when the data doesn't cover a question.

## Why it exists (keep these goals in mind)

1. Build retrieval from scratch: chunking, embeddings, hybrid search, reranking. No black-box RAG platforms.
2. Use LangGraph for a tool-calling agent that chains tools.
3. Measure everything with an automated eval suite. Improvements must show up as numbers.
4. Production-quality engineering: tests, CI, clean structure, clear docs.

## Architecture

- **Structured data** (date, location, aircraft, injuries, weather, flight phase) → Postgres `accidents` table. Used for counts, filters, exact lookups (e.g., tail numbers).
- **Unstructured text** (narratives, probable cause) → chunked, embedded, stored in pgvector `chunks` table. Every chunk carries `accident_id` + key metadata.
- **Retrieval modes:**
  1. Fetch by accident ID (no search) when the accident is known
  2. Filtered semantic search within known accident IDs for specific details
  3. Hybrid search (vector + Postgres full-text, merged with reciprocal rank fusion), optional cross-encoder rerank, when no accident is known
- **Agent (LangGraph):** two tools, `sql_query` (read-only, row limit, timeout) and `search_reports` (hybrid search + fetch by ID). Can chain: SQL finds accident IDs → search pulls their reports.
- **Guardrails:** answer only from tool results, cite accident IDs per claim, decline when SQL is empty or retrieval scores are below threshold, treat user input and retrieved text as data (prompt-injection defense), ask for clarification when a query matches multiple accidents.
- **Evaluation:** JSONL test set (40–50 questions across 8 types) scored on routing accuracy, retrieval hit rate, answer accuracy (exact match for numbers, LLM-as-judge for text), faithfulness, correct refusals, latency, and cost, broken down by question type.

## Data

- Source: NTSB aviation accident database, `avall.zip` from https://www.ntsb.gov/safety/data/Pages/data_stats.aspx (Microsoft Access format; convert with `mdbtools`). Data dictionary: https://app.ntsb.gov/avdata/
- Scope: 2019–2024 accidents unless decided otherwise in `docs/data.md`.
- Raw and processed data live in `data/` and are never committed.

## Tech stack

- Python 3.11+, `uv` for environments and dependencies
- Postgres 16 + pgvector, via Docker Compose
- `psycopg` (v3) + `pgvector` Python package; plain SQL migrations
- Embeddings: OpenAI `text-embedding-3-small` (configurable)
- LLM: configurable via environment variables (OpenAI or Anthropic)
- Reranker: `sentence-transformers` cross-encoder
- Agent: LangGraph + LangChain core
- API: FastAPI with streaming (SSE)
- UI: Next.js (in `web/`)
- Tooling: `ruff` (lint + format), `pytest`, GitHub Actions
- Later: Redis cache, Langfuse/LangSmith tracing, AWS deployment

## Project structure

```
probable-cause/
├── src/probable_cause/
│   ├── config.py           # settings from env vars
│   ├── db/                 # connection, schema, migrations
│   ├── ingest/             # download, load_structured, chunking, embed
│   ├── retrieval/          # vector, keyword, hybrid, rerank, fetch
│   ├── agent/              # tools, graph, prompts, guardrails
│   └── api/                # FastAPI app
├── evals/                  # dataset.jsonl, run_eval.py, judge.py
├── tests/                  # mirrors src/ structure
├── notebooks/              # data exploration only
├── web/                    # Next.js UI
├── docs/                   # data.md, eval.md, architecture.md
├── data/                   # gitignored
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Workflow rules

- Work is organized as GitHub issues (tickets) grouped into milestones M0–M7. Implement **one ticket at a time** and stay within its scope. If something outside the ticket is needed, say so instead of doing it.
- Branches: `main` (protected, releases) ← `dev` (integration) ← `feature/<issue#>-short-name` or `fix/<issue#>-short-name`. Always branch from `dev`.
- Commits use Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`. Small, focused commits.
- PRs target `dev` and include `Closes #<issue>`.
- Before finishing a ticket: code passes `ruff check`, `ruff format`, and `pytest`; acceptance criteria are checked off.
- Never commit secrets, API keys, or data files. Config comes from environment variables; keep `.env.example` updated.

## Code conventions

- Type hints on all functions; short docstrings on public functions.
- Small, testable functions. No giant scripts.
- SQL in clearly named functions or `.sql` files, never built with string concatenation from user input.
- Log useful info (counts, timings, costs), not noise.
- Prefer simple, readable code over clever code.

## How I want to work

I want to understand every part of this system, not just have it work. So:

- Before writing code for a ticket, explain the plan and any design choices or tradeoffs, then wait for my go-ahead on anything non-obvious.
- After implementing, summarize what was built and why, including anything important about how it works under the hood.
- Prefer clear, explainable solutions over magic. If a library hides something important (e.g., how hybrid search merges scores), implement or explain that part explicitly.
- Ask me when requirements are ambiguous instead of guessing.

## Common commands

```bash
docker compose up -d          # start Postgres + pgvector
uv sync                       # install dependencies
uv run pytest                 # run tests
uv run ruff check . && uv run ruff format .
uv run python evals/run_eval.py   # run evaluation suite (once built)
```