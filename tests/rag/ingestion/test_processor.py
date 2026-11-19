
from procurement_assistant.rag.ingestion.models import (
    ChunkingConfig,
    DocumentMetadata,
    LoadedDocument,
)
from procurement_assistant.rag.ingestion.processor import DocumentProcessor


def create_document(content: str) -> LoadedDocument:
    """Create a test document with valid metadata."""

    metadata = DocumentMetadata(
        document_id="TEST-DOC-001",
        document_version="1.0",
        document_type="technical_document",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="synthetic",
        verification_status="unverified",
        language="en",
        sku="MOTOR-001",
    )

    return LoadedDocument(
        content=content,
        metadata=metadata,
        source_path="test_document.md",
        content_hash="test-hash",
    )


def test_short_section_remains_one_chunk():
    document = create_document(
        "# Introduction\n\nIndustrial motor specifications."
    )

    processor = DocumentProcessor(
        ChunkingConfig(chunk_size=500, chunk_overlap=75)
    )

    chunks = processor.process(document)

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].content == "Industrial motor specifications."


def test_long_section_is_split_into_multiple_chunks():
    long_text = "Industrial motor specifications. " * 200

    document = create_document(
        f"# Electrical Specifications\n\n{long_text}"
    )

    processor = DocumentProcessor(
        ChunkingConfig(chunk_size=100, chunk_overlap=20)
    )

    chunks = processor.process(document)

    assert len(chunks) > 1
    assert all(
        processor.count_tokens(chunk.content) <= 100
        for chunk in chunks
    )


def test_chunk_indexes_are_continuous():
    document = create_document(
        "# Introduction\n\nShort introduction.\n\n"
        "# Specifications\n\n" +
        "Motor electrical specifications. " * 100
    )

    processor = DocumentProcessor(
        ChunkingConfig(chunk_size=100, chunk_overlap=20)
    )

    chunks = processor.process(document)

    indexes = [chunk.chunk_index for chunk in chunks]

    assert indexes == list(range(len(chunks)))


def test_metadata_is_preserved():
    document = create_document(
        "# Specifications\n\nMotor voltage is 400 V."
    )

    processor = DocumentProcessor()
    chunks = processor.process(document)

    assert chunks[0].metadata.document_id == "TEST-DOC-001"
    assert chunks[0].metadata.sku == "MOTOR-001"


def test_section_path_is_preserved():
    document = create_document(
        "# Product\n\n"
        "Introduction.\n\n"
        "## Electrical Specifications\n\n"
        "Voltage is 400 V."
    )

    processor = DocumentProcessor()
    chunks = processor.process(document)

    electrical_chunk = next(
        chunk
        for chunk in chunks
        if "Voltage is 400 V." in chunk.content
    )

    assert electrical_chunk.section == (
        "Product > Electrical Specifications"
    )


def test_empty_sections_are_skipped():
    document = create_document(
        "# Introduction\n\n"
        "# Specifications\n\n"
        "Voltage is 400 V."
    )

    processor = DocumentProcessor()
    chunks = processor.process(document)

    assert len(chunks) == 1
    assert chunks[0].content == "Voltage is 400 V."
