from pydantic import BaseModel, ConfigDict, Field, model_validator


class DocumentMetadata(BaseModel):
    """Validated metadata extracted from a document's frontmatter."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    document_version: str
    document_type: str
    knowledge_type: str
    category_key: str
    source_type: str
    verification_status: str
    language: str

    sku: str | None = None
    product_model: str | None = None


class LoadedDocument(BaseModel):
    """A document loaded from its source file."""

    content: str = Field(min_length=1)
    metadata: DocumentMetadata
    source_path: str
    content_hash: str


class DocumentChunk(BaseModel):
    """Represents a processed chunk of a source document."""

    content: str = Field(min_length=1)
    metadata: DocumentMetadata
    section: str | None = None
    chunk_index: int = Field(ge=0)


class ChunkingConfig(BaseModel):
    """Configuration for document chunking."""

    model_config = ConfigDict(frozen=True)

    chunk_size: int = Field(default=500, gt=0)
    chunk_overlap: int = Field(default=75, ge=0)

    @model_validator(mode="after")
    def validate_overlap(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        return self