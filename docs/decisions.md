# ProcureFlow AI — Architecture Decision Log

This file records durable architectural decisions and their rationale. Add a new dated decision when a choice materially affects system boundaries, dependencies, safety, or long-term maintainability.

## ADR-001 — Deterministic business rules remain authoritative

**Status:** Accepted

**Decision**

Inventory, supplier eligibility, budget, procurement policy, and approval rules are enforced by deterministic application logic. The LLM may interpret user intent and help gather information, but it cannot approve a purchase or override business constraints.

**Rationale**

LLM output is probabilistic. Business constraints and authorization decisions must be explicit, testable, and predictable.

**Consequences**

- Keep business rules outside prompts and model-generated decisions.
- Validate tool inputs and outputs.
- Test rule boundaries independently from LLM behavior.
- Require the appropriate human approval for sensitive operations.

## ADR-002 — Conversation collection and procurement execution are separate responsibilities

**Status:** Accepted

**Decision**

The conversation workflow gathers and clarifies request information; the procurement workflow evaluates a sufficiently complete request against business rules and approval requirements.

**Rationale**

Separating interaction management from business execution reduces coupling and makes both workflows easier to test and evolve.

**Consequences**

- Keep conversation state and procurement decision state conceptually distinct.
- Pass validated structured request data between the workflows.
- A request being ready for review does not imply approval or execution.

## ADR-003 — SQLite is the initial business-data store

**Status:** Accepted for the current project scope

**Decision**

Use SQLite with SQLAlchemy for the initial simulated procurement database.

**Rationale**

SQLite is sufficient for the current single-application educational and portfolio scope, keeps local development simple, and allows focus on agent behavior and software architecture.

**Consequences**

- Keep persistence access behind clear application boundaries.
- Avoid introducing a production database before concurrency or deployment requirements justify it.
- Reassess if multi-user deployment or operational constraints require a different database.

## ADR-004 — External procurement operations remain simulated

**Status:** Accepted

**Decision**

The project does not create real purchase orders, payments, or supplier transactions. External systems and integrations are simulated.

**Rationale**

The project is a portfolio and learning system. Safe simulation allows realistic workflow design without causing real-world financial or operational effects.

**Consequences**

- Make simulation boundaries explicit in tool descriptions and documentation.
- Do not expose real transaction credentials or endpoints.
- Preserve approval and permission checks in the simulated workflow.

## ADR-005 — Structured business facts and document knowledge use different retrieval paths

**Status:** Accepted

**Decision**

Relational database queries remain the source for structured operational facts such as inventory. RAG is used for unstructured technical and policy documents.

**Rationale**

A vector search is not a substitute for exact queries over structured business data. Separating the paths improves correctness and makes retrieval behavior easier to evaluate.

**Consequences**

- Route inventory questions to the database.
- Route document-grounded technical questions to RAG.
- Combine both paths only when a question genuinely requires both.
- Do not infer product-specific specifications from generic category documents.

## ADR-006 — Add infrastructure only when a concrete requirement justifies it

**Status:** Accepted

**Decision**

Introduce technologies such as ChromaDB, MCP, FastAPI, Gradio, Redis, PostgreSQL, and deployment infrastructure incrementally, when the next project capability needs them.

**Rationale**

A portfolio project should demonstrate sound engineering decisions, not the number of frameworks in its dependency list.

**Consequences**

- Explain the problem and trade-offs before adding a dependency.
- Prefer the simplest design that meets current requirements.
- Revisit decisions when scale, reliability, security, or deployment requirements change.

## Decision record template

For future decisions, record:

- **ADR number and title**
- **Date**
- **Status:** Proposed, Accepted, Superseded, or Rejected
- **Context:** The problem and constraints
- **Decision:** What was selected
- **Alternatives:** Relevant options considered
- **Consequences:** Benefits, costs, and follow-up work
