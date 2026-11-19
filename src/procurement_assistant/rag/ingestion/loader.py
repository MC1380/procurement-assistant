import hashlib
from pathlib import Path

import yaml
from pydantic import ValidationError

from procurement_assistant.rag.ingestion.models import (
    DocumentMetadata,
    LoadedDocument,
)


class MarkdownDocumentLoader:
    """Loads Markdown documents and validates their frontmatter."""

    def load(self, file_path: str | Path) -> LoadedDocument:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        if path.suffix.lower() != ".md":
            raise ValueError(f"Unsupported document format: {path.suffix}")

        raw_content = path.read_text(encoding="utf-8-sig")

        parts = raw_content.split("---", 2)


        if len(parts) != 3 or parts[0].strip():
            raise ValueError("Invalid or missing YAML frontmatter.")

        raw_metadata, content = parts[1], parts[2].strip()

        if not content:
            raise ValueError("Document content cannot be empty.")

        try:
            metadata_data = yaml.safe_load(raw_metadata)

            if not isinstance(metadata_data, dict):
                raise ValueError("Frontmatter must contain a YAML mapping.")

            metadata = DocumentMetadata.model_validate(metadata_data)

        except (yaml.YAMLError, ValidationError) as exc:
            raise ValueError(f"Invalid document metadata: {exc}") from exc

        content_hash = hashlib.sha256(
            raw_content.encode("utf-8")
        ).hexdigest()

        return LoadedDocument(
            content=content,
            metadata=metadata,
            source_path=str(path.resolve()),
            content_hash=content_hash,
        )
