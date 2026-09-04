import logging

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingClient:
    def __init__(self):
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_API_BASE,
        )
        self._model = getattr(settings, "EMBEDDING_MODEL", "text-embedding-v3")
        self._dimensions = getattr(settings, "EMBEDDING_DIMENSIONS", 1536)

    async def embed_text(self, text: str) -> list[float] | None:
        if not text or not text.strip():
            return None

        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=text.strip()[:8000],
                dimensions=self._dimensions,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Embedding generation failed: %s", e)
            return None

    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]:
        results: list[list[float] | None] = []
        for text in texts:
            embedding = await self.embed_text(text)
            results.append(embedding)
        return results
