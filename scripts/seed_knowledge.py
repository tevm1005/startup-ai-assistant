#!/usr/bin/env python3
"""Seed the vector store with startup knowledge entries.

Usage:
    python scripts/seed_knowledge.py data/knowledge.json
"""

import json
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: seed_knowledge.py <knowledge.json>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        entries = json.load(f)

    print(f"Loaded {len(entries)} knowledge entries from {path}")
    # TODO: embed and insert into pgvector
