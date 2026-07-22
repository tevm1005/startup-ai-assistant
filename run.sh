#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

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

export SA_OLLAMA_BASE_URL=http://localhost:11434

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
