# Startup AI Assistant

Multi-platform AI assistant that reads messages from WhatsApp (phase 1) → Facebook, Instagram, TikTok, queries a knowledge base via pgvector, and replies with startup info.

## Architecture

Three decoupled pipelines:
- **Ingestion** — receive → classify → store message
- **Retrieval** — embed question → pgvector similarity search on `knowledge_embeddings`
- **Response** — prompt + context → LLM → send reply

All platform adapters implement `MessageSource` protocol (`src/core/interfaces.py`).

## Structure

```
src/
├── core/           # interfaces, types (Platform, MessageDirection, etc.)
├── ingestion/      # ingestion pipeline
├── retrieval/      # pgvector semantic search
├── response/       # LLM prompt builder
├── platforms/      # adapter per platform (whatsapp/, later fb/, ig/, tiktok/)
├── database/       # SQLAlchemy async models + connection
│   ├── connection.py   # async engine, session factory, init_db()
│   ├── models.py       # KnowledgeEntry, Conversation, MessageLog
```                                                               

## Commands

```bash
pip install -r requirements.txt          # install deps

source .env.example > .env && vi .env    # configure (all SA_ prefixed)

pytest tests/                            # run tests
pytest tests/ -k test_core -v            # focused test

alembic upgrade head                     # run migrations

python scripts/seed_knowledge.py <file>  # seed vector store
```

## Database

- `KnowledgeEntry` — content + embedding + JSONB metadata for vector search
- `Conversation` — platform thread, linked to messages
- `MessageLog` — individual messages with direction, status, metadata

## Multi-Agent Workflow

This project uses a planner → implementor → reviewer pipeline:

1. `@planner` — designs step-by-step plan, asks clarifying questions
2. *(user approves)*
3. `@implementor` — executes the plan, runs tests, reports
4. `@reviewer` — checks implementation against plan and conventions
5. `@supervisor` — orchestrates the full pipeline and tracks state in WORKFLOW_STATE.md

Invoke with: `@supervisor <feature description>`

## Conventions

- Config via `pydantic-settings`, env prefix `SA_` (see `src/config.py`)
- Async everywhere (asyncpg + SQLAlchemy async sessions)
- New platform = implement `MessageSource` in `src/platforms/<name>/adapter.py`
- Commit `AGENTS.md` to git
