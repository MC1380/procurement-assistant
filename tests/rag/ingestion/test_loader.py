
import hashlib

import pytest

from procurement_assistant.rag.ingestion.loader import MarkdownDocumentLoader
from procurement_assistant.rag.ingestion.models import DocumentMetadata


VALID_MARKDOWN = """---
document_id: TEST-DOC-001
document_version: "1.0"
document_type: technical_document
knowledge_type: product_specific
category_key: industrial_motor
source_type: synthetic
verification_status: unverified
language: en
sku: MOTOR-001
---

# Motor Specifications

Motor voltage is 400 V.
"""


def test_valid_markdown_is_loaded_correctly(tmp_path):
    file_path = tmp_path / "test_document.md"
    file_path.write_text(VALID_MARKDOWN, encoding="utf-8")

    loader = MarkdownDocumentLoader()
    document = loader.load(file_path)

    assert document.content == (
        "# Motor Specifications\n\nMotor voltage is 400 V."
    )
    assert isinstance(document.metadata, DocumentMetadata)
    assert document.metadata.document_id == "TEST-DOC-001"
    assert document.metadata.sku == "MOTOR-001"
    assert document.source_path == str(file_path.resolve())


def test_content_hash_is_calculated_correctly(tmp_path):
    file_path = tmp_path / "test_document.md"
    file_path.write_text(VALID_MARKDOWN, encoding="utf-8")

    document = MarkdownDocumentLoader().load(file_path)

    expected_hash = hashlib.sha256(
        VALID_MARKDOWN.encode("utf-8")
    ).hexdigest()

    assert document.content_hash == expected_hash


def test_missing_file_raises_file_not_found_error(tmp_path):
    file_path = tmp_path / "missing.md"

    with pytest.raises(FileNotFoundError):
        MarkdownDocumentLoader().load(file_path)


def test_unsupported_file_extension_raises_value_error(tmp_path):
    file_path = tmp_path / "document.txt"
    file_path.write_text("Some content", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported document format"):
        MarkdownDocumentLoader().load(file_path)


def test_missing_frontmatter_raises_value_error(tmp_path):
    file_path = tmp_path / "document.md"
    file_path.write_text(
        "# Motor Specifications\n\nVoltage is 400 V.",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="frontmatter"):
        MarkdownDocumentLoader().load(file_path)



def test_invalid_yaml_raises_value_error(tmp_path):
    file_path = tmp_path / "invalid_yaml.md"
    file_path.write_text(
        "---\ndocument_id: [invalid\n---\nSome content",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid document metadata"):
        MarkdownDocumentLoader().load(file_path)


def test_invalid_metadata_raises_value_error(tmp_path):
    invalid_metadata = """---
document_version: "1.0"
document_type: technical_document
knowledge_type: product_specific
category_key: industrial_motor
source_type: synthetic
verification_status: unverified
language: en
---

Some content.
"""

    file_path = tmp_path / "invalid_metadata.md"
    file_path.write_text(invalid_metadata, encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid document metadata"):
        MarkdownDocumentLoader().load(file_path)


def test_empty_document_content_raises_value_error(tmp_path):
    file_path = tmp_path / "empty_content.md"
    file_path.write_text(
        """---
document_id: TEST-DOC-001
document_version: "1.0"
document_type: technical_document
knowledge_type: product_specific
category_key: industrial_motor
source_type: synthetic
verification_status: unverified
language: en
---
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Document content cannot be empty"):
        MarkdownDocumentLoader().load(file_path)



def test_utf8_bom_is_handled_correctly(tmp_path):
    file_path = tmp_path / "bom_document.md"

    file_path.write_text(
        VALID_MARKDOWN,
        encoding="utf-8-sig",
    )

    document = MarkdownDocumentLoader().load(file_path)

    assert document.metadata.document_id == "TEST-DOC-001"
    assert document.content.startswith("# Motor Specifications")
