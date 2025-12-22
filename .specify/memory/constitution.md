<!--
=======================================================================
SYNC IMPACT REPORT
=======================================================================
Version Change: 0.0.0 → 1.0.0 (MAJOR - initial ratification)

Modified Principles: N/A (initial creation)

Added Sections:
- Core Principles (6 principles)
- Technology Standards
- Development Workflow
- Governance

Removed Sections: N/A (initial creation)

Templates Status:
- .specify/templates/plan-template.md       ✅ compatible (Constitution Check section exists)
- .specify/templates/spec-template.md       ✅ compatible (no constitution-specific refs)
- .specify/templates/tasks-template.md      ✅ compatible (no constitution-specific refs)

Deferred Items: None

Follow-up TODOs: None
=======================================================================
-->

# AI-Spec-Driven Technical Book with Embedded RAG Chatbot Constitution

## Core Principles

### I. Spec-First Development

All development MUST follow the spec-driven development lifecycle in strict order:
- Constitution defines non-negotiable principles and standards
- Specification captures requirements and user scenarios before implementation
- Plan documents technical architecture, decisions, and contracts
- Tasks break down work into testable, independently deliverable units
- Implementation follows tasks exactly as specified

**Rationale**: This discipline prevents scope creep, ensures traceable decisions, and enables
parallel work streams. Skipping stages leads to rework and inconsistent outcomes.

### II. Accuracy & Grounding

AI responses MUST be grounded strictly in indexed book content:
- Every AI answer MUST cite or derive from actual book material
- When the knowledge base lacks coverage, AI MUST respond: "Not covered in this book"
- Selected-text queries MUST restrict answers to the provided text only
- No synthesized, inferred, or hallucinated content outside the indexed corpus

**Rationale**: The primary value of the embedded chatbot is trustworthy, accurate assistance.
Hallucinations undermine user trust and defeat the purpose of a curated technical resource.

### III. Separation of Concerns

The system MUST maintain clear boundaries between the Book UI and Chatbot Backend:
- **Book (Frontend)**: Docusaurus-based static site with React components
- **Chatbot (Backend)**: FastAPI service handling RAG queries and agent orchestration
- API contracts MUST be explicit; no implicit coupling between layers
- Frontend components MUST be Docusaurus-compatible (no arbitrary React dependencies)

**Rationale**: Clean separation enables independent deployment, testing, and scaling of each
layer. It also allows the book to function as a standalone resource without the chatbot.

### IV. Reusability & Modularity

Agents, prompts, and skills MUST be designed for reuse:
- Prompts MUST be parameterized templates, not hardcoded strings
- Agents MUST be composable and testable in isolation
- Skills MUST have clear interfaces and single responsibilities
- Shared logic MUST be extracted into reusable modules

**Rationale**: The RAG system will evolve. Modular design reduces maintenance cost and
enables rapid experimentation with new capabilities without rewriting core infrastructure.

### V. Personalization

Content and responses MUST adapt based on authenticated user profile when enabled:
- User preferences, history, and context inform response tailoring
- Personalization MUST NOT compromise accuracy (Principle II takes precedence)
- Unauthenticated users receive generic but still accurate responses
- User data MUST be stored securely in Neon Serverless Postgres

**Rationale**: Personalization increases engagement and learning outcomes. However, it is
an enhancement layer—never an excuse to deviate from grounded, accurate responses.

### VI. No Hallucination Policy

The system MUST implement explicit guardrails against AI hallucination:
- RAG retrieval MUST precede answer generation
- Confidence thresholds MUST gate responses (low confidence → "Not covered" fallback)
- Selected-text mode MUST ignore broader context and answer only from selection
- All AI outputs MUST be auditable and traceable to source documents

**Rationale**: This is the enforcement mechanism for Principle II. Technical guardrails
ensure the policy is implemented, not merely aspirational.

## Technology Standards

The following technology choices are MANDATORY for this project:

| Layer | Technology | Notes |
|-------|------------|-------|
| Book UI | Docusaurus | Static site generator with React components |
| Backend | FastAPI | Python async framework for chatbot API |
| RAG Orchestration | OpenAI Agents SDK / ChatKit SDK | MANDATORY - required per project constraints |
| Vector Search | Qdrant Cloud | Free tier, vector similarity for retrieval |
| Database | Neon Serverless Postgres | User data, state, conversation history |
| Authentication | better-auth | When auth is enabled |
| Deployment (Book) | GitHub Pages | Static hosting for Docusaurus build |

**Constraints**:
- No hallucinated content outside indexed book material
- Frontend limited to Docusaurus-compatible React components
- Clear API boundaries between book UI and chatbot service
- Secrets and tokens MUST use environment variables (`.env`), never hardcoded

## Development Workflow

### Code Quality Gates

1. **Spec Compliance**: Every PR MUST reference a task from `tasks.md`
2. **API Contracts**: Backend changes MUST update OpenAPI spec if endpoints change
3. **Test Coverage**: Critical paths (RAG retrieval, answer generation) MUST have tests
4. **No Hardcoded Secrets**: CI MUST fail if secrets detected in code

### Success Criteria (Project-Level)

- [ ] Book deployed on GitHub Pages and accessible
- [ ] Embedded chatbot answers correctly using RAG pipeline
- [ ] Selected-text-only answering works (isolated context mode)
- [ ] OpenAI Agent SDK used for reasoning and orchestration
- [ ] Codebase follows Spec-Kit Plus generated structure and tasks
- [ ] "Not covered in this book" response works for out-of-scope queries

### Prohibited Practices

- Inventing APIs, data schemas, or contracts without spec approval
- Skipping the spec → plan → tasks workflow
- Committing secrets or tokens to version control
- Refactoring unrelated code in feature branches
- Deploying without passing CI checks

## Governance

### Amendment Process

1. Propose amendment with rationale in a PR
2. Document impact on existing features and templates
3. Update affected templates and artifacts
4. Obtain approval before merging
5. Increment version according to semantic versioning

### Versioning Policy

- **MAJOR**: Backward incompatible changes to principles or removal of principles
- **MINOR**: New principles, sections, or material expansions
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

### Compliance

- All PRs MUST pass Constitution Check (see plan-template.md)
- Violations MUST be documented in Complexity Tracking with justification
- Constitution supersedes all other project documentation when conflicts arise

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
