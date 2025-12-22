# Implementation Plan: RAG Chatbot and Personalization Layer

**Branch**: `001-rag-chatbot` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

## Summary

Build an AI-powered RAG chatbot embedded in an existing Docusaurus technical book. The system enables book-grounded Q&A (answers strictly from indexed content), selected-text-only answering, Urdu translation, and user personalization. The architecture follows a clean separation: Docusaurus frontend communicates with a FastAPI backend that orchestrates OpenAI Agents for RAG retrieval from Qdrant and persists user data in Neon Postgres.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/JavaScript (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, Qdrant Client, SQLAlchemy, React (Docusaurus-compatible)
**Storage**: Qdrant Cloud (vectors), Neon Serverless Postgres (relational data)
**Testing**: pytest (backend), Jest (frontend components)
**Target Platform**: Linux server (backend), GitHub Pages (frontend static hosting)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <5s response time for queries, 50 concurrent users
**Constraints**: <200ms p95 for cached responses, RAG retrieval must precede all answers
**Scale/Scope**: Single book (~50 chapters), ~1000 daily users target

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-First Development | ✅ PASS | Spec complete before plan; plan before implementation |
| II. Accuracy & Grounding | ✅ PASS | FR-002, FR-003 enforce book-only answers; FR-007 restricts selected-text mode |
| III. Separation of Concerns | ✅ PASS | Clear frontend/backend split; API contracts defined in `/contracts/` |
| IV. Reusability & Modularity | ✅ PASS | Agents, prompts, skills designed as composable modules |
| V. Personalization | ✅ PASS | FR-014 to FR-017 cover personalization with accuracy precedence |
| VI. No Hallucination Policy | ✅ PASS | RAG retrieval required; confidence thresholds planned; fallback defined |

**Technology Standards Compliance**:
- ✅ Docusaurus for Book UI
- ✅ FastAPI for Backend
- ✅ OpenAI Agents SDK for RAG Orchestration
- ✅ Qdrant Cloud for Vector Search
- ✅ Neon Serverless Postgres for Database
- ✅ better-auth for Authentication (when enabled)
- ✅ GitHub Pages for Book Deployment

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BOOK UI (Docusaurus)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Chapter View │  │ Chat Widget  │  │ Text Select  │  │ Translate UI │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                    │                                        │
│                           [HTTP/REST API]                                   │
│                          GitHub Pages Host                                  │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI Service)                           │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         API Layer (CORS enabled)                      │  │
│  │  /api/chat  │  /api/chat/selected  │  /api/translate  │  /api/auth   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│         │                 │                    │                 │          │
│         ▼                 ▼                    ▼                 ▼          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    OpenAI Agents Orchestration                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ RAG Agent  │  │ Translate  │  │ Personalize│  │ Fallback   │    │   │
│  │  │            │  │   Agent    │  │   Agent    │  │  Handler   │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                 │                    │                            │
│         ▼                 ▼                    ▼                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐     │
│  │   Qdrant    │  │   OpenAI    │  │      Neon Postgres              │     │
│  │   Client    │  │     API     │  │  (users, conversations, cache)  │     │
│  └─────────────┘  └─────────────┘  └─────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Qdrant Cloud   │      │   OpenAI API    │      │  Neon Postgres  │
│  (Vector Store) │      │  (Embeddings +  │      │  (Serverless)   │
│                 │      │   Completions)  │      │                 │
│  - Book chunks  │      │  - text-embed   │      │  - users        │
│  - Embeddings   │      │  - gpt-4o-mini  │      │  - conversations│
│                 │      │                 │      │  - translations │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output - architectural decisions
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - setup guide
├── contracts/           # Phase 1 output - API specifications
│   └── openapi.yaml     # REST API contract
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User, UserPreference
│   │   ├── conversation.py  # Conversation, Message
│   │   └── translation.py   # Translation cache
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py   # RAG retrieval logic
│   │   ├── agent_service.py # OpenAI Agents orchestration
│   │   ├── embedding_service.py  # Embedding generation
│   │   └── translation_service.py # Urdu translation
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── rag_agent.py     # Book Q&A agent
│   │   ├── translate_agent.py # Translation agent
│   │   └── prompts/         # Parameterized prompt templates
│   │       ├── rag_system.txt
│   │       ├── selected_text.txt
│   │       └── translate.txt
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py          # /api/chat endpoints
│   │   ├── translate.py     # /api/translate endpoints
│   │   └── auth.py          # /api/auth endpoints
│   └── db/
│       ├── __init__.py
│       ├── database.py      # SQLAlchemy setup
│       └── migrations/      # Alembic migrations
├── tests/
│   ├── contract/            # API contract tests
│   ├── integration/         # End-to-end tests
│   └── unit/                # Unit tests
├── scripts/
│   └── ingest_book.py       # Book content indexing script
├── requirements.txt
├── .env.example
└── Dockerfile

frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget/
│   │   │   ├── index.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   └── ChatInput.tsx
│   │   ├── TextSelector/
│   │   │   └── index.tsx
│   │   └── TranslateButton/
│   │       └── index.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useTextSelection.ts
│   │   └── useTranslation.ts
│   └── services/
│       └── api.ts           # Backend API client
├── tests/
│   └── components/          # Component tests
└── package.json
```

**Structure Decision**: Web application structure selected due to clear frontend (Docusaurus + React) and backend (FastAPI + Python) separation. Frontend components are designed to be Docusaurus-compatible plugins.

## RAG Workflow

### Full-Book Q&A Flow (P1)

```
User Question
     │
     ▼
┌─────────────────┐
│ Embed Question  │ ← OpenAI text-embedding-3-small
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Vector Search   │ ← Qdrant: top-k similar chunks
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Confidence Gate │ ← If similarity < threshold → "Not covered"
└─────────────────┘
     │ (pass)
     ▼
┌─────────────────┐
│  RAG Agent      │ ← OpenAI Agents SDK
│  - Context: retrieved chunks
│  - Prompt: book-only instruction
│  - User profile (if authenticated)
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Response + Refs │ ← Answer with source citations
└─────────────────┘
```

### Selected-Text Mode Flow (P2)

```
Selected Text + Question
     │
     ▼
┌─────────────────┐
│ Bypass RAG      │ ← Use selected text directly as context
└─────────────────┘
     │
     ▼
┌─────────────────┐
│  RAG Agent      │ ← Same agent, different prompt
│  - Context: ONLY selected text
│  - Prompt: selection-only instruction
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Response        │ ← Answer scoped to selection
└─────────────────┘
```

## Key Architectural Decisions

| Decision | Choice | Rationale | Alternatives Rejected |
|----------|--------|-----------|----------------------|
| Chunking Strategy | 512 tokens, 50 token overlap | Balance between context and precision | 256 (too fragmented), 1024 (too broad) |
| Agent Architecture | Single orchestrator agent with tools | Simpler, sufficient for MVP scope | Multi-agent (overhead not justified yet) |
| Personalization Location | Server-side | Secure, consistent, no client state | Client-side (security concerns, inconsistent) |
| Translation Approach | Agent-based, on-demand | Flexible, cacheable, uses same infra | Static i18n (doesn't scale, manual effort) |
| Embedding Model | text-embedding-3-small | Cost-effective, good quality | text-embedding-3-large (overkill for book size) |
| LLM for Responses | gpt-4o-mini | Fast, cost-effective, sufficient quality | gpt-4o (unnecessary cost for Q&A) |

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Complexity Level | Justification |
|--------|-----------------|---------------|
| Agent Architecture | Low | Single agent with tools, not multi-agent |
| Database Schema | Low | 5 tables, straightforward relationships |
| Frontend Integration | Medium | Custom React components in Docusaurus |
| RAG Pipeline | Medium | Standard retrieval pattern |

## Implementation Phases

### Phase 1: Backend Foundation
- FastAPI service setup with CORS
- OpenAI Agents SDK integration
- API contract definition (OpenAPI)
- Environment configuration

### Phase 2: Knowledge Layer
- Book content ingestion script
- Chunking and embedding generation
- Qdrant collection setup
- Retrieval validation tests

### Phase 3: RAG Intelligence
- RAG agent implementation
- Book-only answering enforcement
- Confidence threshold and fallback
- Selected-text query handling

### Phase 4: Frontend Integration
- Chat widget component
- Text selection component
- API client service
- Error handling and loading states

### Phase 5: Enhancements (Optional/Bonus)
- User authentication (better-auth)
- Personalization based on profile
- Urdu translation agent
- Conversation history persistence

## Testing Strategy

| Test Type | Coverage | Tools |
|-----------|----------|-------|
| Contract Tests | API endpoints match OpenAPI spec | pytest, schemathesis |
| Unit Tests | Services, agents, utilities | pytest |
| Integration Tests | RAG pipeline end-to-end | pytest |
| Frontend Tests | Component behavior | Jest, React Testing Library |
| Manual Review | Agent behavior, UX | Checklist-based |

**Critical Test Cases**:
1. Book-covered question → accurate answer with source
2. Out-of-scope question → "Not covered in this book"
3. Selected-text question → answer from selection only
4. Selected-text out-of-scope → "Not in selected text"
5. Empty/invalid queries → appropriate error messages
6. CORS preflight → allowed from book domain

## Environment Configuration

```bash
# .env.example
OPENAI_API_KEY=sk-...
QDRANT_URL=https://xxx.qdrant.cloud
QDRANT_API_KEY=...
NEON_DATABASE_URL=postgresql://...
CORS_ORIGINS=https://yourbook.github.io
ENVIRONMENT=development
LOG_LEVEL=INFO
CONFIDENCE_THRESHOLD=0.7
```

## Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  GitHub Pages   │     │   Railway/      │     │  Managed        │
│  (Frontend)     │────▶│   Render/       │────▶│  Services       │
│                 │     │   Fly.io        │     │                 │
│  - Static HTML  │     │   (Backend)     │     │  - Qdrant Cloud │
│  - React bundle │     │                 │     │  - Neon Postgres│
│                 │     │  - FastAPI      │     │  - OpenAI API   │
└─────────────────┘     │  - Docker       │     └─────────────────┘
                        └─────────────────┘
```
