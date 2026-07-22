#!/bin/bash
set -e

echo "==> Running migrations..."
alembic upgrade head

echo "==> Pulling Ollama models..."
curl -s -X POST http://ollama:11434/api/pull \
  -d '{"name":"'"$SA_LLM_MODEL"'"}' > /dev/null
curl -s -X POST http://ollama:11434/api/pull \
  -d '{"name":"'"$SA_EMBEDDING_MODEL"'"}' > /dev/null
echo "==> Ollama models ready"

exec "$@"
