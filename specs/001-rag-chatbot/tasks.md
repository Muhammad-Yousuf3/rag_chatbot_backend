# Tasks: RAG Chatbot and Personalization Layer

**Input**: Design documents from `/specs/001-rag-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Tests are included as they support critical RAG accuracy requirements per constitution (Principle II, VI).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- Paths follow web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md at backend/
- [x] T002 Create frontend directory structure per plan.md at frontend/
- [x] T003 [P] Initialize Python project with requirements.txt at backend/requirements.txt
- [x] T004 [P] Initialize frontend package.json at frontend/package.json
- [x] T005 [P] Create .env.example with all required environment variables at backend/.env.example
- [x] T006 [P] Create config.py for environment configuration at backend/src/config.py
- [x] T007 [P] Configure linting (ruff) and formatting (black) at backend/pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create FastAPI app entry point with CORS at backend/src/main.py
- [x] T009 [P] Setup SQLAlchemy database connection at backend/src/db/database.py
- [x] T010 [P] Create Qdrant client wrapper at backend/src/services/qdrant_client.py
- [x] T011 [P] Create OpenAI client wrapper at backend/src/services/openai_client.py
- [x] T012 Create database models __init__.py at backend/src/models/__init__.py
- [x] T013 [P] Create Conversation model at backend/src/models/conversation.py
- [x] T014 [P] Create Message model at backend/src/models/message.py
- [x] T015 Create initial Alembic migration for conversations/messages at backend/src/db/migrations/
- [x] T016 Create embedding service for text-embedding-3-small at backend/src/services/embedding_service.py
- [x] T017 Create health check endpoint at backend/src/api/health.py
- [x] T018 [P] Create API router initialization at backend/src/api/__init__.py
- [x] T019 Create book ingestion script for Qdrant indexing at backend/scripts/ingest_book.py
- [x] T020 [P] Create frontend API client service at frontend/src/services/api.ts

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Book-Grounded Q&A (Priority: P1) MVP

**Goal**: Enable users to ask questions and receive accurate answers derived solely from indexed book content

**Independent Test**: Ask book-covered questions → get accurate answers with sources. Ask out-of-scope questions → get "Not covered in this book" response.

### Tests for User Story 1

- [x] T021 [P] [US1] Create unit test for RAG retrieval service at backend/tests/unit/test_rag_service.py
- [x] T022 [P] [US1] Create unit test for RAG agent at backend/tests/unit/test_rag_agent.py
- [x] T023 [P] [US1] Create integration test for chat endpoint at backend/tests/integration/test_chat_endpoint.py
- [x] T024 [P] [US1] Create contract test for /api/chat at backend/tests/contract/test_chat_contract.py

### Implementation for User Story 1

- [x] T025 [US1] Create RAG system prompt template at backend/src/agents/prompts/rag_system.txt
- [x] T026 [US1] Create RAG retrieval service with confidence threshold at backend/src/services/rag_service.py
- [x] T027 [US1] Create RAG agent using OpenAI Agents SDK at backend/src/agents/rag_agent.py
- [x] T028 [US1] Create agent service orchestration layer at backend/src/services/agent_service.py
- [x] T029 [US1] Implement /api/chat POST endpoint at backend/src/api/chat.py
- [x] T030 [US1] Add "Not covered in this book" fallback logic in rag_service.py
- [x] T031 [US1] Add conversation context preservation in agent_service.py
- [x] T032 [US1] Add source citation generation in rag_agent.py
- [x] T033 [P] [US1] Create useChat React hook at frontend/src/hooks/useChat.ts
- [x] T034 [P] [US1] Create ChatMessage component at frontend/src/components/ChatWidget/ChatMessage.tsx
- [x] T035 [P] [US1] Create ChatInput component at frontend/src/components/ChatWidget/ChatInput.tsx
- [x] T036 [US1] Create ChatWidget main component at frontend/src/components/ChatWidget/index.tsx
- [x] T037 [US1] Add error handling and loading states in ChatWidget
- [x] T038 [US1] Wire ChatWidget to Docusaurus layout

**Checkpoint**: User Story 1 (Book-Grounded Q&A) is fully functional and testable independently

---

## Phase 4: User Story 2 - Selected-Text Answering (Priority: P2)

**Goal**: Allow users to select text and ask questions restricted to that selection only

**Independent Test**: Select a paragraph → ask question → answer references only selected text. Ask about content outside selection → "Not in selected text" response.

### Tests for User Story 2

- [x] T039 [P] [US2] Create unit test for selected-text mode at backend/tests/unit/test_selected_text.py
- [x] T040 [P] [US2] Create integration test for /api/chat/selected at backend/tests/integration/test_selected_text_endpoint.py
- [x] T041 [P] [US2] Create contract test for /api/chat/selected at backend/tests/contract/test_selected_contract.py

### Implementation for User Story 2

- [x] T042 [US2] Create selected-text prompt template at backend/src/agents/prompts/selected_text.txt
- [x] T043 [US2] Add selected-text mode to RAG agent at backend/src/agents/rag_agent.py
- [x] T044 [US2] Implement /api/chat/selected POST endpoint at backend/src/api/chat.py
- [x] T045 [US2] Add selected-text validation (min/max length) in chat.py
- [x] T046 [P] [US2] Create useTextSelection React hook at frontend/src/hooks/useTextSelection.ts
- [x] T047 [P] [US2] Create TextSelector component at frontend/src/components/TextSelector/index.tsx
- [x] T048 [US2] Integrate TextSelector with ChatWidget
- [x] T049 [US2] Add selected-text mode indicator in ChatWidget UI
- [x] T050 [US2] Add exit selected-text mode functionality

**Checkpoint**: User Story 2 (Selected-Text Answering) is fully functional and testable independently

---

## Phase 5: User Story 3 - Urdu Chapter Translation (Priority: P3)

**Goal**: Provide AI-generated Urdu translations of chapters with caching

**Independent Test**: Request Urdu translation → receive translated content. Request same chapter again → load from cache instantly.

### Tests for User Story 3

- [x] T051 [P] [US3] Create unit test for translation service at backend/tests/unit/test_translation_service.py
- [x] T052 [P] [US3] Create unit test for translate agent at backend/tests/unit/test_translate_agent.py
- [x] T053 [P] [US3] Create integration test for /api/translate at backend/tests/integration/test_translate_endpoint.py

### Implementation for User Story 3

- [x] T054 [US3] Create Translation model at backend/src/models/translation.py
- [x] T055 [US3] Add Translation model to migrations at backend/src/db/migrations/
- [x] T056 [US3] Create translate prompt template at backend/src/agents/prompts/translate.txt
- [x] T057 [US3] Create translate agent at backend/src/agents/translate_agent.py
- [x] T058 [US3] Create translation service with caching at backend/src/services/translation_service.py
- [x] T059 [US3] Implement GET /api/translate/{chapterSlug} endpoint at backend/src/api/translate.py
- [x] T060 [US3] Implement POST /api/translate/{chapterSlug} endpoint at backend/src/api/translate.py
- [x] T061 [US3] Add translation progress tracking for long requests
- [x] T062 [P] [US3] Create useTranslation React hook at frontend/src/hooks/useTranslation.ts
- [x] T063 [P] [US3] Create TranslateButton component at frontend/src/components/TranslateButton/index.tsx
- [x] T064 [US3] Add translation loading indicator and progress UI
- [x] T065 [US3] Wire TranslateButton to chapter pages

**Checkpoint**: User Story 3 (Urdu Translation) is fully functional and testable independently

---

## Phase 6: User Story 4 - User Personalization (Priority: P4)

**Goal**: Store user preferences and adapt responses based on experience level and reading history

**Independent Test**: Login as beginner → get simpler explanations. Login as advanced → get technical explanations. Unauthenticated → get default responses.

### Tests for User Story 4

- [x] T066 [P] [US4] Create unit test for auth service at backend/tests/unit/test_auth_service.py
- [x] T067 [P] [US4] Create unit test for personalization at backend/tests/unit/test_personalization.py
- [x] T068 [P] [US4] Create integration test for auth endpoints at backend/tests/integration/test_auth_endpoint.py

### Implementation for User Story 4

- [x] T069 [US4] Create User model at backend/src/models/user.py
- [x] T070 [US4] Create UserPreference model at backend/src/models/user.py
- [x] T071 [US4] Add User/UserPreference to migrations at backend/src/db/migrations/
- [x] T072 [US4] Create auth service with JWT handling at backend/src/services/auth_service.py
- [x] T073 [US4] Implement POST /api/auth/register endpoint at backend/src/api/auth.py
- [x] T074 [US4] Implement POST /api/auth/login endpoint at backend/src/api/auth.py
- [x] T075 [US4] Implement GET /api/auth/me endpoint at backend/src/api/auth.py
- [x] T076 [US4] Implement PUT /api/auth/preferences endpoint at backend/src/api/auth.py
- [x] T077 [US4] Add personalization context to RAG agent prompts
- [x] T078 [US4] Add experience-level-aware response generation in rag_agent.py
- [x] T079 [US4] Track chapters read in user preferences
- [x] T080 [US4] Implement GET /api/chat/conversations endpoint at backend/src/api/chat.py
- [x] T081 [US4] Implement GET /api/chat/conversations/{id} endpoint at backend/src/api/chat.py
- [x] T082 [P] [US4] Create auth components at frontend/src/components/Auth/
- [x] T083 [P] [US4] Create useAuth React hook at frontend/src/hooks/useAuth.ts
- [x] T084 [US4] Add authentication state to ChatWidget
- [x] T085 [US4] Add user preference settings UI

**Checkpoint**: User Story 4 (Personalization) is fully functional and testable independently

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T086 [P] Add comprehensive error handling across all endpoints
- [x] T087 [P] Add request validation with Pydantic schemas at backend/src/schemas/
- [x] T088 [P] Add rate limiting middleware at backend/src/middleware/rate_limit.py
- [x] T089 [P] Add structured logging at backend/src/utils/logging.py
- [x] T090 [P] Create Dockerfile at backend/Dockerfile
- [x] T091 [P] Create docker-compose.yml at repository root
- [x] T092 [P] Add frontend build configuration for Docusaurus integration
- [x] T093 Run full test suite and fix any failures
- [x] T094 Run quickstart.md validation steps
- [x] T095 Update README with setup and usage instructions

**Checkpoint**: All Polish & Cross-Cutting tasks complete - Project ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on at least US1 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 2 - Reuses RAG agent from US1
- **User Story 3 (P3)**: Can start after Phase 2 - Independent translation system
- **User Story 4 (P4)**: Can start after Phase 2 - Requires auth infrastructure

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Phase 2 completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel

---

## Parallel Example: Phase 2 Foundation

```bash
# These can run in parallel after T008 completes:
T009: Setup SQLAlchemy database connection
T010: Create Qdrant client wrapper
T011: Create OpenAI client wrapper

# These can run in parallel after models setup:
T013: Create Conversation model
T014: Create Message model
```

## Parallel Example: User Story 1

```bash
# Launch all tests together (TDD):
T021: Unit test for RAG retrieval service
T022: Unit test for RAG agent
T023: Integration test for chat endpoint
T024: Contract test for /api/chat

# Launch frontend components in parallel with backend:
T033: useChat React hook
T034: ChatMessage component
T035: ChatInput component
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Book-Grounded Q&A)
4. **STOP and VALIDATE**: Test US1 independently
5. Deploy/demo if ready - this is a functional MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Test independently → Deploy
4. Add User Story 3 → Test independently → Deploy
5. Add User Story 4 → Test independently → Deploy
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (RAG Q&A)
   - Developer B: User Story 3 (Translation) - independent
3. After US1 complete:
   - Developer A: User Story 2 (Selected-Text)
   - Developer C: User Story 4 (Auth/Personalization)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution compliance verified at each phase checkpoint
