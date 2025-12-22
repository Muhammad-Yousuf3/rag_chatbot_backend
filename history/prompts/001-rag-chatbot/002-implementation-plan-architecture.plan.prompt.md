---
id: 002
title: Implementation Plan and Architecture
stage: plan
date: 2025-12-16
surface: agent
model: claude-opus-4-5-20251101
feature: 001-rag-chatbot
branch: 001-rag-chatbot
user: muhammad-yousuf
command: /sp.plan
labels: ["plan", "architecture", "rag", "fastapi", "openai-agents", "qdrant"]
links:
  spec: specs/001-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-rag-chatbot/plan.md
  - specs/001-rag-chatbot/research.md
  - specs/001-rag-chatbot/data-model.md
  - specs/001-rag-chatbot/quickstart.md
  - specs/001-rag-chatbot/contracts/openapi.yaml
tests:
  - N/A
---

## Prompt

Create:
- System architecture sketch (Book UI ↔ FastAPI ↔ OpenAI Agents ↔ Qdrant/Neon)
- Backend and frontend integration plan
- Agent and RAG workflow definition
- Deployment and environment configuration plan

Phases:
1. Backend foundation
   - FastAPI service setup
   - OpenAI Agent / ChatKit SDK integration
   - CORS and API contract definition

2. Knowledge layer
   - Book content ingestion and chunking
   - Embeddings and indexing in Qdrant
   - Retrieval validation

3. RAG intelligence
   - Agent prompts and tools
   - Book-only answering enforcement
   - Selected-text-only query handling

4. Frontend integration
   - Chat UI component in Docusaurus
   - API wiring and error handling
   - UX for selected-text queries

5. Enhancements (optional / bonus)
   - Subagents and reusable skills
   - better-auth signup and profiling
   - Personalized chapter rewriting
   - Urdu translation toggle

Decisions needing documentation:
- Chunking size vs retrieval accuracy
- Single vs multi-agent orchestration
- Server-side personalization vs client-side
- Translation via agent vs static i18n

Testing strategy:
- Verify answers are sourced from book content only
- Confirm selected-text restriction works
- Validate fallback response: "Not covered in this book"
- API integration and CORS checks
- Manual UI and agent behavior review

## Response snapshot

Created comprehensive implementation plan with:

**System Architecture**:
- Book UI (Docusaurus) → FastAPI Backend → OpenAI Agents → Qdrant/Neon
- ASCII diagram showing all component relationships
- Clear separation of concerns per constitution

**RAG Workflows**:
- Full-book Q&A flow: Embed → Vector Search → Confidence Gate → RAG Agent → Response
- Selected-text flow: Bypass RAG → Use selection as context → Agent → Response

**Key Architectural Decisions**:
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Chunking | 512 tokens, 50 overlap | Balance precision/context |
| Agent Architecture | Single orchestrator with tools | Simpler for MVP scope |
| Personalization | Server-side | Secure, consistent |
| Translation | Agent-based, on-demand | Flexible, cacheable |
| Embedding Model | text-embedding-3-small | Cost-effective |
| LLM | gpt-4o-mini | Fast, sufficient quality |

**Generated Artifacts**:
- research.md - 10 architectural decisions documented
- data-model.md - 5 tables with full schema
- contracts/openapi.yaml - Complete REST API specification
- quickstart.md - Developer setup guide

**Constitution Check**: All 6 principles PASS

## Outcome

- Impact: Complete architecture and contracts ready for task generation
- Tests: N/A (planning document)
- Files: plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml
- Next prompts: /sp.tasks to generate implementation tasks, /sp.adr for chunking/agent decisions
- Reflection: Plan provides clear technical direction while maintaining constitution compliance

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check PASS - all 6 principles verified
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - plan complete
