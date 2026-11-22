# ProcureFlow AI

**An AI-powered industrial procurement assistant built around reliable, human-supervised workflows.**

ProcureFlow AI is a portfolio project that explores how LLM-powered agents can support real-world procurement processes. It combines deterministic business rules, structured data, document-based technical knowledge, and human approval checkpoints.

The system currently focuses on simulating industrial purchasing workflows. External business systems are simulated, and **no real purchase orders, payments, or supplier transactions are executed**.

## Project Goals

- Collect and validate industrial purchase requests from natural-language conversations.
- Check inventory and product information stored in relational data.
- Apply deterministic procurement policies and approval rules.
- Orchestrate multi-step workflows with LangGraph.
- Retrieve technical knowledge from product and category documents using RAG.
- Evaluate LLM extraction and retrieval components with repeatable datasets and tests.
- Provide a foundation for standardized external tool integration through MCP and an API/UI layer.

## Current Implementation

### Procurement and Agent Workflows

- **Purchase workflow:** LangGraph-based orchestration for procurement decisions, including business-rule checks and human-in-the-loop manager approval.
- **Conversation layer:** Structured request models and a conversation service for collecting required purchase information, handling missing fields, and protecting existing values from unconfirmed corrections.
- **Business rules:** Deterministic policies remain authoritative; the LLM does not approve purchases or override business constraints.
- **Persistence:** SQLite and SQLAlchemy for business data.

### LLM Integration and Evaluation

- LangChain-based LLM integration and structured extraction with Pydantic models.
- An extraction evaluation dataset and evaluation workflow for measuring intent, field, and category accuracy, structured-output success, and latency.
- Automated tests with pytest.

### RAG Foundation

The RAG subsystem supports two knowledge scopes through a shared ingestion design:

- **Category knowledge:** General technical information about a product category.
- **Product-specific knowledge:** Information tied to an individual product or SKU.

Implemented:

- Markdown document loading.
- YAML frontmatter parsing and Pydantic metadata validation.
- SHA-256 content hashing.
- Structure-aware chunking with Markdown headings and token-based splitting.
- Preservation of document metadata and section information in chunks.
- Retrieval evaluation dataset models and JSONL loading.
- Deterministic evidence normalization.
- Ground-truth resolution from expected evidence to the actual document chunks, with automated tests for matching, overlap, multiple evidence items, document boundaries, and missing evidence.

Not implemented yet:

- Embedding generation.
- ChromaDB vector storage and semantic retrieval.
- Retrieval metrics and an end-to-end retrieval evaluation runner.
- Document lifecycle registry and safe document-version replacement.

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.12+ |
| Agent orchestration | LangGraph |
| LLM integration | LangChain |
| Structured data validation | Pydantic |
| Business data persistence | SQLite, SQLAlchemy |
| Document processing | LangChain Text Splitters, tiktoken, PyYAML |
| Automated testing | pytest |
| Planned vector database | ChromaDB |
| Planned external tool integration | MCP |
| Planned backend | FastAPI |
| Planned demo UI | Gradio |

## Architecture

The codebase is organized by responsibility:

```text
src/procurement_assistant/
├── agent/        # LangGraph workflows and agent state
├── config/       # Application and model configuration
├── database/     # SQLAlchemy models and database management
├── domain/       # Domain models and business rules
├── evaluation/   # LLM extraction evaluation
├── rag/          # Document ingestion and retrieval evaluation
├── services/     # Application services
└── cli.py        # Command-line entry point
```

For more detail, see:

- [Architecture](docs/architecture.md)
- [LLM Evaluation](docs/evaluation.md)

## Getting Started

### Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

### Install dependencies

```bash
uv sync
```

### Run the test suite

```bash
uv run pytest
```

LLM-backed workflows may require provider credentials and application configuration. Configure secrets locally; do not commit API keys or other credentials.

## Development Roadmap

1. Complete and stabilize the RAG ingestion and retrieval-evaluation foundation.
2. Implement embeddings and ChromaDB-backed vector retrieval.
3. Add retrieval metrics and a repeatable evaluation runner.
4. Connect RAG retrieval to the LangGraph conversation and procurement workflows.
5. Add MCP integrations for simulated external procurement tools.
6. Expose application capabilities through FastAPI.
7. Build an interactive Gradio demo.
8. Expand end-to-end evaluation, observability, and regression coverage.

Implementation status may evolve as the project progresses. The architecture document is the detailed reference for current design decisions.

## Safety and Scope

- All supplier, inventory, and external-system interactions are simulated unless explicitly stated otherwise.
- No real purchase order or payment is created.
- Manager approval checkpoints are part of the workflow where required.
- Deterministic business rules take precedence over LLM-generated suggestions.
- Synthetic or unverified technical documents are educational test data, not authoritative specifications for real industrial, installation, or safety decisions.

## Project Status

ProcureFlow AI is under active development. The current focus is building a testable RAG foundation before introducing vector retrieval and connecting it to the agent workflow.
