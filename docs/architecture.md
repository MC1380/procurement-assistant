# ProcureFlow AI — Architecture

## 1. Project Goal

ProcureFlow AI is a portfolio AI Agent that simulates industrial procurement workflows. It evaluates purchase requests, checks business rules, retrieves procurement policies, and requests manager approval when required.

All external business systems are simulated. No real purchase is executed.

## 2. Technology Stack

### Implemented

- **Python:** Core application logic
- **LangGraph:** Workflow orchestration, conditional routing, and human-in-the-loop
- **LangChain:** LLM integration and structured information extraction
- **Pydantic:** Data validation and structured models
- **SQLite + SQLAlchemy:** Persistent business data
- **pytest:** Automated testing
- **PyYAML:** YAML frontmatter parsing for document metadata
- **LangChain Text Splitters + tiktoken:** Structure-aware document chunking and token counting
### Planned

- **MCP:** Standardized access to external and simulated tools
- **FastAPI:** Backend API
- **Gradio:** Interactive application demo
- **ChromaDB:** Vector storage and semantic retrieval
- **Embedding Models:** Convert document chunks into vector representations
## 3. Project Structure and Main Components

The application code is organized into the following modules:

- **agent/**: LangGraph workflows and their state definitions.
- **domain/**: Business models, conversation models, and deterministic business rules.
- **services/**: Application services for conversation processing, inventory, product knowledge, LLM extraction, and purchase suggestions.
- **database/**: SQLAlchemy models and database connection management.
- **evaluation/**: Evaluation datasets, metrics, execution, and report generation.
- **config/**: LLM and application configuration.
- **cli.py**: Command-line application entry point.

### Architectural Boundaries

- Domain models are independent of database persistence models.
- Agent workflows coordinate application services and business logic.
- Services encapsulate specific application operations.
- Evaluation modules assess LLM extraction performance independently of the main workflow.
- External integrations must remain simulated until explicitly implemented and authorized.

### 3.1 Source Code Layout

src/procurement_assistant/
├── agent/
├── config/
├── database/
├── domain/
├── evaluation/
├── rag/
│   └── ingestion/
├── services/
├── cli.py
└── __init__.py

## 4. Purchase Workflow

1. Receive a purchase request.
2. Check inventory, supplier eligibility, budget, and procurement policies.
3. Determine whether the request can proceed automatically or requires manager review.
4. Pause for manager approval when required.
5. Continue or stop based on the manager's decision.
6. Record the outcome and relevant business data.

## 5. Safety and Scope

- No real purchase orders or payments.
- Manager approval is required for sensitive or restricted requests.
- The LLM must not override deterministic business rules.
- External tools operate in simulation mode.
- Automated tests verify important business and workflow scenarios.

## 6. Development Principles

- Implement small, testable increments.
- Run tests before meaningful commits.
- Keep architecture documentation updated.
- Add technologies only when they serve a clear project requirement.
- Production deployment is outside the current scope.

## 7. Conversation Workflow

The Conversation Workflow collects and validates the information
required to create a purchase request.

It is separate from the Purchase Workflow.

### 7.1 Conversation Models

The conversation layer uses Pydantic models:

- `RequestExtraction`: Structured information extracted from a user message.
- `RequestDraft`: The current draft of the purchase request.
- `ConversationMessage`: A user or assistant message with a timestamp.
- `ConversationStatus`: The current status of information collection.
- `MessageIntent`: The detected intent of a user message.

### 7.2 Conversation State

`ConversationState` stores the information needed throughout a conversation:

- `conversation_id`: Unique conversation identifier.
- `messages`: Conversation message history.
- `request_data`: Current purchase request draft.
- `missing_information`: Required information that has not been provided.
- `clarification_fields`: Fields that need user clarification.
- `status`: Current conversation status.

The messages field uses a LangGraph reducer to append new messages
instead of replacing the existing history.

### 7.3 Conversation Service

`conversation_service.py` contains the core business logic for
processing user messages.

Its responsibilities include:

1. Merging newly extracted information with the existing request draft.
2. Preserving previously collected information.
3. Checking required basic and product-specific attributes.
4. Detecting ambiguous or conflicting information.
5. Managing corrections to previously collected values.
6. Determining whether the request needs more information or is
   ready for review.

Product-specific required attributes are retrieved from the
product knowledge database.

### 7.4 Safe Information Updates

Extracting a new value does not automatically authorize changing
an existing value.

When a correction conflicts with previously collected information,
the existing value is preserved until the correction is confirmed.

The `confirmed_corrections` input identifies fields that are
authorized to be updated.

The LLM is not trusted to authorize its own corrections.

### 7.5 Current Implementation Scope

The Conversation Service currently receives a structured
`RequestExtraction` object as input.

LLM-based extraction and the interactive clarification process
have not yet been integrated.

The service is currently implemented and tested independently.
Integration with the LangGraph conversation workflow is a
subsequent development step.

A request marked `READY_FOR_REVIEW` means the required information
has been collected. It does not mean that the purchase is approved
or executed.

## 8. Retrieval-Augmented Generation (RAG)

The RAG subsystem provides access to technical product knowledge and supporting procurement documents.

It is designed to support two knowledge scopes:

- **Category Knowledge:** General technical knowledge about product categories, such as industrial motors, pumps, and bearings.
- **Product-Specific Knowledge:** Technical information associated with a specific product or SKU, such as datasheets and product manuals.

Both knowledge scopes share the same ingestion and retrieval architecture. Metadata is used to distinguish their scope and support filtering.

### 8.1 Document Ingestion

The ingestion pipeline transforms source documents into structured chunks suitable for embedding and retrieval.

The initial implementation includes:

- `MarkdownDocumentLoader`: Reads Markdown documents, parses YAML frontmatter, validates metadata, and calculates a SHA-256 content hash.
- `DocumentMetadata`: Defines the structured metadata associated with each source document.
- `LoadedDocument`: Represents a validated source document.
- `DocumentProcessor`: Splits documents into semantically meaningful sections and smaller chunks.

### 8.2 Chunking Strategy

The processor uses a two-stage strategy:

1. `MarkdownHeaderTextSplitter` separates documents according to their heading structure.
2. `RecursiveCharacterTextSplitter` splits sections that exceed the configured token limit.

The initial configuration uses:

- Chunk size: 500 tokens
- Chunk overlap: 75 tokens

These values are experimental baselines and will be evaluated against retrieval quality.

Each chunk preserves its source document metadata, section path, and sequential chunk index.

### 8.3 Knowledge Sources and Trust

Documents are stored under:

- `data/documents/category/`
- `data/documents/product_specific/`

Document metadata identifies the knowledge type, source type, and verification status.

Synthetic or unverified documents must not be treated as authoritative technical specifications or used for real industrial purchasing and safety decisions.

### 8.4 Planned RAG Components

The following components are not implemented yet:

- Embedding generation
- Vector storage and semantic retrieval using ChromaDB
- Document lifecycle registry
- Safe document version replacement
- Retrieval evaluation

### 8.5 Retrieval and Data Boundaries

Structured business information, such as inventory quantities, remains the responsibility of the relational database.

Technical knowledge contained in documents is retrieved through RAG.

Product-specific specifications must be supported by product-specific sources. General category knowledge must not be used to invent missing specifications for an individual product.

For questions requiring both structured business data and technical knowledge, the application may combine database queries and document retrieval.