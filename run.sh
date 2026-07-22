#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# ── First-run setup ──────────────────────────────────────────
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "[ok] created .env from .env.example — edit it to customise settings"
    else
        echo "[warn] no .env or .env.example found — using defaults"
    fi
fi

# Export env vars from .env (but don't clobber what's already set)
if [ -f .env ]; then
    set -a
    # shellcheck source=/dev/null
    . .env 2>/dev/null || true
    set +a
fi

# Default model names (used by curl pulls below)
SA_LLM_MODEL="${SA_LLM_MODEL:-llama3.2:1b}"
SA_EMBEDDING_MODEL="${SA_EMBEDDING_MODEL:-nomic-embed-text}"

# ── PostgreSQL ────────────────────────────────────────────────
if pg_isready -h /tmp/pgsock &>/dev/null; then
    echo "[ok] PostgreSQL already running"
else
    echo "[..] Starting PostgreSQL..."
    pg_ctl -D /tmp/pgdata -o "-k /tmp/pgsock" start &>/tmp/pgdata/logfile
    sleep 2
    echo "[ok] PostgreSQL started"
fi

# ── Ollama ────────────────────────────────────────────────────
if curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "[ok] Ollama already running"
else
    echo "[..] Starting Ollama..."
    ollama serve &>/tmp/ollama.log &
    sleep 3
    echo "[ok] Ollama started"
fi

# Pull models before starting (idempotent — cached if already present)
echo "[..] Pulling LLM model: $SA_LLM_MODEL ..."
curl -s -X POST http://localhost:11434/api/pull \
  -d "{\"name\":\"$SA_LLM_MODEL\"}" > /dev/null
echo "[ok] $SA_LLM_MODEL ready"

echo "[..] Pulling embedding model: $SA_EMBEDDING_MODEL ..."
curl -s -X POST http://localhost:11434/api/pull \
  -d "{\"name\":\"$SA_EMBEDDING_MODEL\"}" > /dev/null
echo "[ok] $SA_EMBEDDING_MODEL ready"

export SA_OLLAMA_BASE_URL=http://localhost:11434
export SA_LLM_MODEL
export SA_EMBEDDING_MODEL

# ── Mode selection ────────────────────────────────────────────
MODE="${1:-cli}"

case "$MODE" in
    cli)
        echo "[..] Launching CLI assistant..."
        .venv/bin/python -m src.cli
        ;;
    server)
        echo "[..] Launching API server on http://0.0.0.0:8000 ..."
        .venv/bin/uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
        ;;
    *)
        echo "Usage: $0 [cli|server]"
        echo "  cli      — REPL interface (default)"
        echo "  server   — FastAPI webhook server on :8000"
        exit 1
        ;;
esac
