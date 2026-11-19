import tiktoken
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from procurement_assistant.rag.ingestion.models import (
    ChunkingConfig,
    DocumentChunk,
    LoadedDocument,
)


class DocumentProcessor:
    """Processes loaded documents into structured chunks."""

    def __init__(
        self,
        config: ChunkingConfig | None = None,
    ) -> None:
        self.config = config or ChunkingConfig()

        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
            ],
            strip_headers=True,
        )

        self.recursive_splitter = (
            RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                encoding_name="cl100k_base",
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
            )
        )

    def count_tokens(self, text: str) -> int:
        """Return the number of tokens in a text."""
        return len(self.tokenizer.encode(text))

    def process(
        self,
        document: LoadedDocument,
    ) -> list[DocumentChunk]:
        """Split a document into structured chunks."""

        sections = self.header_splitter.split_text(document.content)

        chunks: list[DocumentChunk] = []

        for section_document in sections:
            section_content = section_document.page_content.strip()

            if not section_content:
                continue

            section_parts = [
                section_document.metadata[key]
                for key in ("h1", "h2", "h3")
                if section_document.metadata.get(key)
            ]

            section_path = " > ".join(section_parts) or None

            token_count = self.count_tokens(section_content)

            if token_count <= self.config.chunk_size:
                chunk_contents = [section_content]
            else:
                chunk_contents = self.recursive_splitter.split_text(
                    section_content
                )

            for chunk_content in chunk_contents:
                chunks.append(
                    DocumentChunk(
                        content=chunk_content,
                        metadata=document.metadata,
                        section=section_path,
                        chunk_index=len(chunks),
                    )
                )

        return chunks
