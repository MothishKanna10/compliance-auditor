#!/bin/sh
set -e

CHROMA_DIR="${CHROMA_PERSIST_DIR:-chroma_db}"

if [ ! -d "$CHROMA_DIR" ] || [ -z "$(ls -A "$CHROMA_DIR" 2>/dev/null)" ]; then
    echo "Building vector database..."
    python -m app.ingestion
fi

exec uvicorn app.api:app --host 0.0.0.0 --port "${PORT:-8000}"
