# Startup AI Assistant

Multi-platform AI assistant: reads messages from WhatsApp (phase 1) → Facebook, Instagram, TikTok, queries knowledge base, and replies with startup info.

## Quick start

```bash
# 1. First run — no .env needed, run.sh creates it for you
./run.sh

# Or run as API server:
./run.sh server
```

Requirements:
- **PostgreSQL** with pgvector (or let `run.sh` start a local instance from `/tmp/pgdata`)
- **Ollama** installed → `run.sh` auto-pulls `llama3.2:1b` and `nomic-embed-text` on first run
- `.venv/` with dependencies (`pip install -r requirements.txt`)

## Prototype status

| Component | Working | Notes |
|---|---|---|---|
| KnowledgeStore (keyword search) | ✅ | |
| LLMClient (Ollama) | ✅ | Falls back to mock if Ollama is unreachable |
| IngestionPipeline | ✅ | |
| ResponseGenerator | ✅ | Delegates to LLMClient |
| EmbeddingClient (Ollama) | ✅ | Falls back to mock if Ollama is unreachable |
| VectorStore (pgvector) | ✅ | Uses cosine_distance on `knowledge_embeddings` |
| seed_knowledge.py | ✅ | Embeds + inserts into pgvector |
| WhatsAppAdapter | ✅ | httpx-based, needs credentials |
| FastAPI server | ✅ | `POST /ask`, `POST /webhook/whatsapp` |
| Conversation memory | ✅ | Configurable max turns, per-conversation |
| Smart PDF chunking | ✅ | Paragraph-aware with overlap |
| Content hashing | ✅ | SHA256 skips unchanged PDFs on re-ingest |
| Alembic migration | ✅ | Initial schema created |

Ollama is the default LLM backend. Set `SA_OLLAMA_BASE_URL` in `.env` to change endpoint.

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
