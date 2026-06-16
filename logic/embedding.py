import httpx
from structlog.stdlib import get_logger

logger = get_logger()


class TextEmbeddingService:
    def __init__(self, base_url: str = 'http://ollama:11434', model: str = 'nomic-embed-text') -> None:
        self.base_url = base_url
        self.model = model

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            response = await client.post(
                '/api/embed',
                json={'model': self.model, 'input': text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings: list[list[float]] = data['embeddings']
            return embeddings[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=120.0) as client:
            response = await client.post(
                '/api/embed',
                json={'model': self.model, 'input': texts},
            )
            response.raise_for_status()
            data = response.json()
            embeddings: list[list[float]] = data['embeddings']
            return embeddings
