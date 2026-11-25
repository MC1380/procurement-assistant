
from procurement_assistant.rag.ingestion.models import (
    DocumentChunk,
    DocumentMetadata,
)


def create_metadata(
    document_version: str = "1.0",
) -> DocumentMetadata:
    return DocumentMetadata(
        document_id="motor-manual",
        document_version=document_version,
        document_type="technical_manual",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="manufacturer",
        verification_status="verified",
        language="en",
        sku="MOTOR-001",
    )


def test_chunk_id_contains_document_identity():
    chunk = DocumentChunk(
        content="Rated power: 7.5 kW",
        metadata=create_metadata(),
        chunk_index=0,
    )

    assert chunk.chunk_id == "motor-manual:1.0:0"


def test_different_document_versions_have_different_chunk_ids():
    first_version = DocumentChunk(
        content="Rated power: 7.5 kW",
        metadata=create_metadata("1.0"),
        chunk_index=0,
    )

    second_version = DocumentChunk(
        content="Rated power: 11 kW",
        metadata=create_metadata("2.0"),
        chunk_index=0,
    )

    assert first_version.chunk_id != second_version.chunk_id


def test_different_chunk_indexes_have_different_chunk_ids():
    first_chunk = DocumentChunk(
        content="Rated power: 7.5 kW",
        metadata=create_metadata(),
        chunk_index=0,
    )

    second_chunk = DocumentChunk(
        content="Rated voltage: 400 V",
        metadata=create_metadata(),
        chunk_index=1,
    )

    assert first_chunk.chunk_id != second_chunk.chunk_id
