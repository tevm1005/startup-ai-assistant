#!/usr/bin/env python3
"""REPL prototype — test the ingestion → retrieval → response loop locally."""

from __future__ import annotations

import asyncio
from pathlib import Path

from src.ingestion.pipeline import IngestionPipeline
from src.knowledge import KnowledgeStore


def _default_seed() -> str | None:
    candidates = [
        Path("data/knowledge.json"),
        Path("scripts/knowledge.json"),
        Path.home() / ".config/startup-assistant/knowledge.json",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


async def async_main():
    seed = _default_seed()
    knowledge = KnowledgeStore(seed)

    if seed:
        print(f"Loaded {knowledge.count()} knowledge entries from {seed}")
    else:
        print("No knowledge file found. Use /load <path> to seed data.")

    pipeline = IngestionPipeline(knowledge=knowledge)

    print("\nStartup AI Assistant REPL (type /help for commands)\n")

    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        if line.startswith("/"):
            cmd, *args = line[1:].split()
            match cmd:
                case "help":
                    print("Commands:")
                    print("  /load <path>   load knowledge JSON")
                    print("  /quit          exit")
                case "load":
                    if args:
                        knowledge.load(args[0])
                        print(f"Loaded {knowledge.count()} entries")
                    else:
                        print("Usage: /load <path>")
                case "quit":
                    break
                case _:
                    print(f"Unknown command: /{cmd}")
            continue

        answer = await pipeline.run(line)
        print(f"assistant> {answer}\n")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
