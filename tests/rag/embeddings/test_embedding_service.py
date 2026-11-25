from unittest.mock import create_autospec

from langchain_core.embeddings import Embeddings

from procurement_assistant.rag.embeddings.embedding_service import (
    EmbeddingService,
)



class FakeEmbeddings(Embeddings):
    """A fake embedding provider for unit testing."""

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return [0.4, 0.5, 0.6]


def test_embed_documents_returns_vectors():
    model = FakeEmbeddings()
    service = EmbeddingService(model)

    result = service.embed_documents(
        ["Industrial motor", "Industrial pump"]
    )

    assert result == [
        [0.1, 0.2, 0.3],
        [0.1, 0.2, 0.3],
    ]


def test_embed_query_returns_vector():
    model = FakeEmbeddings()
    service = EmbeddingService(model)

    result = service.embed_query("Industrial motor")

    assert result == [0.4, 0.5, 0.6]


def test_embed_query_delegates_to_model():
    model = create_autospec(
        Embeddings,
        instance=True,
    )
    model.embed_query.return_value = [0.4, 0.5, 0.6]

    service = EmbeddingService(model)

    result = service.embed_query("industrial motor")

    assert result == [0.4, 0.5, 0.6]

    model.embed_query.assert_called_once_with(
        "industrial motor"
    )