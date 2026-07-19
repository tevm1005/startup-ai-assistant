"""Build prompt with retrieved context and query LLM."""


class ResponseGenerator:
    async def generate(self, question: str, context: list[dict]) -> str: ...
