from langchain_core.embeddings import Embeddings


class EmbeddingService:
    """Provides document and query embedding operations."""

    def __init__(self, model: Embeddings) -> None:
        self._model = model

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Convert multiple documents into embedding vectors."""
        return self._model.embed_documents(texts)

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        """Convert a query into an embedding vector."""
        return self._model.embed_query(text)