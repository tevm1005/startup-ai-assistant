# Startup AI Assistant

Multi-platform AI assistant: reads messages from WhatsApp (phase 1) → Facebook, Instagram, TikTok, queries knowledge base, and replies with startup info.

## Prototype status

The project is early-stage. Many components are stubs — only the in-memory path works:

| Component | Working | Stub |
|---|---|---|
| KnowledgeStore (keyword search) | ✅ | |
| LLMClient (mock) | ✅ | |
| IngestionPipeline (wires above) | ✅ | |
| VectorStore (pgvector) | | stub |
| ResponseGenerator | | stub |
| WhatsAppAdapter | | stub |
| seed_knowledge.py | | stub |
| Alembic migrations dir | | empty |

Enable real LLM by setting `SA_LLM_API_KEY` in `.env` (currently falls back to mock).

## Entrypoints

- **CLI REPL**: `startup-assistant` (defined in `pyproject.toml`) or `python -m src.cli`
- **IngestionPipeline.run(question)** at `src/ingestion/pipeline.py:15` — main "ask" path

## Commands

```bash
.venv/bin/pytest tests/ -v                         # all tests
.venv/bin/pytest tests/test_core.py -v              # focused test
.venv/bin/pytest tests/ -k "test_core" -v           # keyword filter
.venv/bin/alembic upgrade head                      # run migrations
cp .env.example .env && vi .env                     # configure (SA_ prefix)
python scripts/seed_knowledge.py <file>             # seed vector store (stub)
```

Use `.venv/bin/pytest`, not bare `pytest`. The `.venv/` is the venv directory.

## Architecture

Three decoupled pipelines:
- **Ingestion** — receive → classify → store message
- **Retrieval** — embed question → pgvector similarity search on `knowledge_embeddings`
- **Response** — prompt + context → LLM → send reply

Current working path bypasses DB: `IngestionPipeline` uses in-memory `KnowledgeStore` (keyword-based, `src/knowledge/store.py:30`) + mock `LLMClient` (`src/llm/client.py:21`).

Platform adapters implement `MessageSource` protocol from `src/core/interfaces.py:20`.

## Conventions

- Config via `pydantic-settings`, env prefix `SA_` (`src/config.py`)
- Async everywhere (asyncpg + SQLAlchemy async sessions)
- New platform = implement `MessageSource` in `src/platforms/<name>/adapter.py`
- No linter/formatter/typechecker configured yet — `pyproject.toml` has no such config
- All functions should have type hints (code-review skill enforces this)
