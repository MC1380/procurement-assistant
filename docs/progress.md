# ProcureFlow AI — Development Progress

> This file is a concise status snapshot. Code and test results are the source of truth. Do not mark a capability complete without implementation evidence and relevant verification.

## Current focus

Complete the RAG embedding-to-retrieval path, beginning with a clear vector-store boundary and then implementing indexing and semantic retrieval.

## Implemented

### Procurement and conversation foundations

- LangGraph procurement workflow with deterministic business-rule checks and manager approval flow.
- Conversation graph with message processing and routes for information collection, cancellation, unrecognized input, inventory questions, and procurement handoff.
- Conversation state and routing modules.
- Conversation nodes for collecting information, handling cancellation and unrecognized input, and answering inventory questions.
- SQLite and SQLAlchemy persistence for simulated business data.

**Scope note:** The procurement-handoff route is currently a placeholder node. Do not describe the conversation graph as a complete end-to-end procurement experience.

### LLM integration and configuration

- LangChain-based chat-model integration and structured extraction with Pydantic.
- Centralized provider connection configuration.
- Separate embedding-model settings and factory, reusing provider connection settings without coupling embedding configuration to chat-specific settings.
- pytest test coverage for configuration and application components.

### RAG ingestion

- Markdown loading and YAML frontmatter parsing/validation.
- SHA-256 source-content hashing.
- Heading-aware document splitting and recursive token-aware chunking.
- Configurable chunk size and overlap (current baseline: 500 tokens and 75-token overlap).
- Synthetic category-level and product-specific knowledge documents.

### Embedding boundary

- Embedding model factory based on LangChain's `Embeddings` interface.
- `EmbeddingService` exposing document and query embedding operations.
- Unit-test coverage using fake/mock embedding implementations.

### RAG evaluation foundation

- Retrieval evaluation dataset models and JSONL loading.
- Evidence normalization.
- Ground-truth evidence resolution from expected evidence to source chunks.
- Tests covering core evaluation utilities.

## In progress / not yet complete

- End-to-end embedding generation over ingested document chunks.
- Vector-store interface and ChromaDB-backed implementation.
- Persistent indexing and index update behavior.
- Semantic retrieval and metadata filtering.
- Retrieval metrics and a repeatable end-to-end evaluation runner.
- Document lifecycle management and safe document-version replacement.
- Integration of document retrieval into the LangGraph conversation workflow.
- Full end-to-end verification of conversation-to-procurement handoff.

## Planned sequence

1. Define the requirements and minimal contract for the vector-store boundary.
2. Implement and test local vector indexing.
3. Implement semantic retrieval and metadata filtering.
4. Build retrieval metrics and a repeatable evaluation runner.
5. Evaluate chunking and retrieval choices using the RAG evaluation dataset.
6. Connect database-backed inventory questions and document-grounded questions through explicit conversation routing.
7. Implement simulated procurement MCP server(s) and integrate an MCP client.
8. Expose application capabilities through FastAPI.
9. Build a Gradio demo.
10. Expand integration tests, observability, packaging, and deployment readiness.

Revisit this order only when a dependency or concrete requirement justifies it.

## Definition of done

A capability is complete only when:

- Its responsibility and boundaries are clear.
- Relevant automated tests exist and pass.
- External dependencies are isolated or mocked in unit tests.
- AI behavior has evaluation evidence where appropriate.
- Documentation reflects the actual implementation.
- Changes are committed with a meaningful message.

## Update protocol

At the end of each meaningful development session:

- Move work to **Implemented** only after checking the code and relevant test results.
- Keep incomplete or unverified work under **In progress / not yet complete**.
- Record material architectural decisions in [decisions.md](decisions.md).
- Include relevant test commands/results and commit references when they are known.
- Do not invent test results or treat this status file as more authoritative than the repository.
