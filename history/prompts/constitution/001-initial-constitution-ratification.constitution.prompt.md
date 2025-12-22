---
id: 001
title: Initial Constitution Ratification
stage: constitution
date: 2025-12-16
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: muhammad-yousuf
command: /sp.constitution
labels: ["constitution", "governance", "rag-chatbot", "spec-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

Project: AI-Spec-Driven Technical Book with Embedded RAG Chatbot

Core principles:
- Spec-first development (constitution → plan → tasks → implementation)
- Accuracy: AI responses must be grounded strictly in book content
- Separation of concerns: Book (Docusaurus UI) and Chatbot (FastAPI backend)
- Reusability: Agents, prompts, and skills must be modular and reusable
- Personalization: Content adapts based on authenticated user profile

Key standards:
- Book authored using Claude Code + Spec-Kit Plus
- RAG implemented using OpenAI Agents / ChatKit SDK (mandatory)
- Vector search via Qdrant Cloud (free tier)
- State & user data stored in Neon Serverless Postgres
- Backend framework: FastAPI
- AI must say "Not covered in this book" if knowledge is unavailable
- Selected-text queries must restrict answers to provided text only

Constraints:
- No hallucinated content outside indexed book material
- Auth handled via better-auth (when enabled)
- Frontend limited to Docusaurus-compatible React components
- Clear API boundaries between book UI and chatbot service

Success criteria:
- Book deployed on GitHub Pages
- Embedded chatbot answers correctly using RAG
- Selected-text-only answering works
- OpenAI Agent SDK used for reasoning and orchestration
- Codebase follows Spec-Kit generated structure and tasks

## Response snapshot

Created the initial project constitution v1.0.0 with 6 core principles:

1. **Spec-First Development** - Strict lifecycle ordering
2. **Accuracy & Grounding** - AI responses tied to book content
3. **Separation of Concerns** - Book UI vs Chatbot Backend boundaries
4. **Reusability & Modularity** - Composable agents/prompts/skills
5. **Personalization** - User profile-based adaptation
6. **No Hallucination Policy** - Technical guardrails for accuracy

Added Technology Standards table (Docusaurus, FastAPI, OpenAI Agents SDK, Qdrant, Neon Postgres, better-auth, GitHub Pages).

Added Development Workflow with code quality gates, success criteria checklist, and prohibited practices.

Added Governance section with amendment process, versioning policy (SemVer), and compliance requirements.

## Outcome

- Impact: Foundation document established for all future development
- Tests: N/A (governance document)
- Files: .specify/memory/constitution.md (created/updated)
- Next prompts: /sp.specify to create first feature spec, or /sp.plan for implementation planning
- Reflection: Constitution captures all user-provided principles and constraints comprehensively

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS - all placeholders filled, principles testable
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - initial constitution complete
