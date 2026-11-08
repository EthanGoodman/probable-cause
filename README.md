# probable-cause

[![CI](https://github.com/EthanGoodman/probable-cause/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/EthanGoodman/probable-cause/actions/workflows/ci.yml)

An agentic RAG system over NTSB aviation accident data.

Ask questions about US aviation accidents (2019–2024) and get answers grounded in official NTSB records, with a citation to the accident ID for every claim:

- **Specific accidents:** "What caused the accident involving N12345?"
- **Patterns:** "What are common factors in fuel exhaustion accidents during cruise?"
- **Statistics:** "How many fatal Cessna 172 accidents were there in 2022?"

When the data doesn't cover a question, the agent says so instead of guessing.

> **Status:** early development. See the GitHub milestones for progress.

## Architecture

_TBD._ In short: structured accident data lives in Postgres for counts and filters. Narrative text is chunked, embedded, and searched with hybrid (vector + full-text) retrieval in pgvector. A LangGraph agent chains a `sql_query` tool and a `search_reports` tool to answer questions. See `docs/architecture.md` (coming soon).

## Quickstart

Prerequisites: [Docker](https://docs.docker.com/get-docker/) and [uv](https://docs.astral.sh/uv/). uv installs the right Python version for you.

```bash
cp .env.example .env      # then set POSTGRES_PASSWORD (and API keys when needed)
docker compose up -d      # start Postgres 16 + pgvector
uv sync                   # create .venv and install dependencies
uv run pre-commit install # one-time: ruff on commit, pytest on push
uv run pytest             # run tests
```

## Evaluation

_TBD._ An automated eval suite will score routing, retrieval hit rate, answer accuracy, faithfulness, refusals, latency, and cost by question type. See `docs/eval.md` (coming soon).

## Project structure

```
src/probable_cause/   # application code (db, ingest, retrieval, agent, api)
tests/                # unit and integration tests
evals/                # evaluation dataset and runner
notebooks/            # data exploration
docs/                 # design and data documentation
```

## Data

Data comes from the [NTSB aviation accident database](https://www.ntsb.gov/safety/data/Pages/data_stats.aspx). Raw and processed data are not committed to this repo.

## License

[MIT](LICENSE)
