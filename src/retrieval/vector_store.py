"""pgvector-based semantic search over startup knowledge."""


class VectorStore:
    async def search(self, query: str, top_k: int = 5) -> list[dict]: ...
