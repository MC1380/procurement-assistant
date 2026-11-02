# ProcureFlow AI — Architecture

## 1. Project Goal

ProcureFlow AI is a portfolio AI Agent that simulates industrial procurement workflows. It evaluates purchase requests, checks business rules, retrieves procurement policies, and requests manager approval when required.

All external business systems are simulated. No real purchase is executed.

## 2. Technology Stack

- **Python:** Core application logic
- **LangGraph:** Workflow orchestration, conditional routing, and human-in-the-loop
- **LangChain:** LLM integration, tools, and RAG
- **MCP:** Standardized access to external and simulated tools
- **SQLite + SQLAlchemy:** Persistent business data
- **FastAPI:** Backend API
- **Gradio:** Simple interactive demo
- **pytest:** Automated testing

## 3. Main Components

- **Domain layer:** Purchase requests, suppliers, budgets, policies, and business rules
- **Workflow layer:** Purchase evaluation, routing, and manager approval
- **Data layer:** Persistent storage for business entities
- **Knowledge layer:** Retrieval of procurement policies and documents
- **Tool layer:** Simulated inventory and supplier operations, including MCP integration
- **Interface layer:** Gradio demo and FastAPI endpoints

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