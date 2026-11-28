# ProcureFlow AI — Architecture

## 1. Purpose and Scope

ProcureFlow AI is a portfolio project for an AI-assisted industrial procurement workflow. It combines conversational information collection, deterministic procurement rules, structured business data, and document-grounded technical knowledge.

The application is a simulation. It does not create real purchase orders, payments, or supplier transactions.

## 2. Technology Status

### Implemented in the repository

- **Python:** Application implementation.
- **LangGraph:** Procurement and conversation workflow orchestration.
- **LangChain / langchain-openai:** Chat-model and embedding-model integration.
- **Pydantic / pydantic-settings:** Domain data validation and environment-based configuration.
- **SQLite / SQLAlchemy:** Simulated business-data persistence.
- **PyYAML:** YAML frontmatter parsing.
- **LangChain Text Splitters / tiktoken:** Heading-aware document chunking and token counting.
- **pytest:** Automated test suite and test doubles for external dependencies.

### Planned or not yet integrated

- **ChromaDB or another vector store:** Persistent vector indexing and semantic retrieval.
- **MCP:** Standardized external tool integration.
- **FastAPI:** HTTP API layer.
- **Gradio:** Interactive demo.
- **Docker and deployment tooling:** Reproducible packaging and deployment.

A library or configuration component being present does not mean the corresponding end-to-end capability is complete. In particular, embedding configuration and an embedding service exist, but vector indexing and semantic retrieval are not yet integrated.

## 3. Codebase Boundaries

The application source is organized by responsibility:

```text
src/procurement_assistant/
├── agent/
│   ├── conversation/   # Conversation graph, state, routing, and nodes
│   └── ...             # Procurement workflow
├── config/             # Provider and model configuration
├── database/           # SQLAlchemy models and database management
├── domain/             # Domain models and business rules
├── evaluation/         # LLM extraction evaluation
├── rag/
│   ├── embeddings/     # Embedding service
│   ├── evaluation/     # Retrieval-evaluation datasets and evidence utilities
│   └── ingestion/      # Document loading, metadata, and chunking
├── services/           # Application services
└── cli.py              # Command-line entry point
```

Architectural boundaries:

- Domain rules must not depend on LLM output.
- Agent graphs orchestrate application operations; they should not become repositories for business logic.
- Services encapsulate application capabilities behind explicit dependencies.
- Configuration is centralized and separated by responsibility.
- External providers should be replaceable and isolated in unit tests.
- Structured operational facts and unstructured document knowledge use different access paths.

## 4. Procurement Workflow

The procurement workflow is responsible for evaluating a sufficiently complete purchase request.

At a high level it:

1. Receives structured request data.
2. Checks inventory and applicable supplier, budget, and policy constraints.
3. Determines whether the request can proceed or requires manager review.
4. Pauses for the required human decision.
5. Continues or stops according to that decision.
6. Records the simulated outcome.

The LLM may help interpret user language and extract information. It must not override deterministic business rules or authorize a purchase.

## 5. Conversation Workflow

The conversation workflow is implemented as a LangGraph state graph.

### Main components

- `state.py`: Defines `ConversationState`, including conversation messages, request data, missing information, clarification fields, status, and message-related state.
- `router.py`: Selects the next conversation route.
- `graph.py`: Builds and compiles the graph.
- `nodes/`: Contains nodes for processing messages, collecting information, handling cancellation, handling unrecognized input, and answering inventory questions.

### Current routing behavior

The graph routes processed messages to:

- `collect_information`
- `handle_cancellation`
- `handle_unrecognized`
- `answer_question` (currently implemented through the inventory-question node)
- `handoff_to_procurement` (currently a placeholder route node)

The graph and individual nodes exist, but this should not be interpreted as a fully integrated end-to-end conversational procurement experience. Continue to verify each route and its tests as the workflow evolves.

The conversation layer and procurement decision workflow have separate responsibilities: collecting information does not approve or execute a purchase.

## 6. Configuration and Model Integration

Provider connection settings and model-specific settings are separated.

- `config/providers.py` contains shared OpenAI-compatible connection settings such as API key and base URL.
- `config/embeddings.py` contains embedding-specific model configuration and constructs the embedding model using the provider settings.
- Chat-model configuration is maintained separately from embedding-model configuration.

This separation avoids coupling an embedding model's configuration to chat-specific concerns and supports reuse of provider connection details.

Secrets must be supplied through environment configuration and must never be committed.

## 7. RAG Architecture

The RAG subsystem is being developed to answer questions from category-level and product-specific documents.

### Knowledge scopes

- **Category knowledge:** General knowledge associated with a product category.
- **Product-specific knowledge:** Information associated with an individual product or SKU.

### Ingestion

The current ingestion foundation includes:

- `MarkdownDocumentLoader`: Reads Markdown documents, parses YAML frontmatter, validates metadata, and calculates a SHA-256 content hash.
- `DocumentMetadata` and `LoadedDocument`: Represent validated document metadata and loaded content.
- `DocumentProcessor`: Splits content by Markdown heading structure and then uses recursive token-aware splitting for oversized sections.
- Chunk metadata preserves source-document information, section context, and chunk ordering.

The initial chunking configuration uses a 500-token target and 75-token overlap. These are experimental baseline values, not proven optimal settings.

Synthetic documents are stored under:

- `data/documents/category/`
- `data/documents/product_specific/`

Synthetic or unverified documents are test material, not authoritative industrial specifications.

### Embeddings

The repository contains:

- Embedding-specific settings in `config/embeddings.py`.
- An embedding-model factory using shared provider connection settings.
- `EmbeddingService`, which exposes document and query embedding operations through the LangChain `Embeddings` interface.

These components provide the embedding boundary. They are not yet connected to a persistent vector index or an end-to-end retrieval pipeline.

### Retrieval evaluation foundation

The RAG evaluation package currently includes dataset models and loading, evidence normalization, and ground-truth evidence resolution utilities. A complete retrieval runner and retrieval-quality metrics remain future work.

### Planned RAG flow

The intended next stages are:

1. Generate embeddings for processed chunks.
2. Define the minimum vector-store abstraction required by the application.
3. Index chunks in a local vector store.
4. Implement semantic retrieval and metadata filtering.
5. Evaluate retrieval quality with repeatable datasets and metrics.
6. Connect document retrieval to the conversation graph.

Structured facts such as inventory quantities must continue to come from relational database queries. RAG is for document-based knowledge. Product-specific claims require product-specific evidence.

## 8. Safety and Trust Boundaries

- No real purchase, payment, or supplier transaction is performed.
- Deterministic business rules remain authoritative.
- Sensitive actions require explicit authorization and appropriate human approval.
- Validate inputs and outputs at application and tool boundaries.
- Treat retrieved documents and model responses as untrusted data.
- Do not treat synthetic or unverified technical documents as authoritative specifications.
- Keep credentials out of source code, logs, and Git history.

## 9. Development Principles

- Implement small, testable increments.
- Inspect existing code before changing architecture.
- Introduce dependencies only when a concrete requirement justifies them.
- Isolate external services from unit tests.
- Add integration and evaluation tests where unit tests are insufficient.
- Keep this document aligned with the code that actually exists.

## 10. Related Documentation

- [Development Progress](progress.md)
- [Architecture Decision Log](decisions.md)
- [LLM Evaluation](evaluation.md)
