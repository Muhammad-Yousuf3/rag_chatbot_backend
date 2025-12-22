# Research: RAG Chatbot and Personalization Layer

**Feature**: 001-rag-chatbot
**Date**: 2025-12-16
**Status**: Complete

## Overview

This document captures architectural research and decisions made during the planning phase. All decisions align with the project constitution and spec requirements.

---

## 1. Chunking Strategy for RAG

### Decision
**512 tokens with 50 token overlap**

### Rationale
- **512 tokens** provides enough context for meaningful Q&A without overwhelming the LLM context window
- **50 token overlap** ensures concepts spanning chunk boundaries are captured in at least one chunk
- Technical book content typically has self-contained sections that fit well in this size
- Balances retrieval precision (smaller chunks = more precise) with context completeness (larger chunks = more context)

### Alternatives Considered

| Strategy | Pros | Cons | Why Rejected |
|----------|------|------|--------------|
| 256 tokens, 25 overlap | Higher precision | Fragments concepts, more retrieval calls | Too fragmented for explanatory content |
| 1024 tokens, 100 overlap | More complete context | Less precise retrieval, higher token cost | Too broad, reduces relevance |
| Semantic chunking | Natural boundaries | Complex implementation, inconsistent sizes | Adds complexity without clear benefit for MVP |

### Validation
- Test with sample chapters to verify chunk quality
- Measure retrieval accuracy with held-out questions
- Adjust threshold if needed based on empirical results

---

## 2. Agent Architecture: Single vs Multi-Agent

### Decision
**Single orchestrator agent with tools**

### Rationale
- **Simplicity**: One agent with multiple tools (RAG retrieval, translation, personalization) is easier to debug and maintain
- **Sufficient for scope**: The feature set (Q&A, selected-text, translation) doesn't require complex multi-agent coordination
- **OpenAI Agents SDK**: Designed for tool-based single agents; multi-agent requires additional orchestration
- **Latency**: Single agent avoids inter-agent communication overhead

### Alternatives Considered

| Architecture | Pros | Cons | Why Rejected |
|--------------|------|------|--------------|
| Multi-agent (RAG, Translate, Personalize) | Separation of concerns | Complex coordination, higher latency | Overhead not justified for MVP scope |
| LangGraph multi-agent | State machine control | Learning curve, dependency | Adds complexity without clear benefit |
| No agents (direct API calls) | Maximum control | Loses SDK benefits, more boilerplate | Violates constitution (must use OpenAI Agents SDK) |

### Future Consideration
If feature scope expands significantly (e.g., complex reasoning chains, multi-step research), revisit multi-agent architecture.

---

## 3. Personalization: Server-side vs Client-side

### Decision
**Server-side personalization**

### Rationale
- **Security**: User preferences and history stored server-side cannot be tampered with
- **Consistency**: All users get consistent experience regardless of browser/device
- **Constitution compliance**: Principle V requires secure storage in Neon Postgres
- **Simpler frontend**: Frontend only sends user token; backend handles personalization logic

### Alternatives Considered

| Approach | Pros | Cons | Why Rejected |
|----------|------|------|--------------|
| Client-side (localStorage) | No server round-trip | Insecure, inconsistent across devices | Security concerns |
| Hybrid (cache client, store server) | Performance | Complex sync logic | Unnecessary complexity |
| No personalization | Simpler | Doesn't meet spec requirements | Violates FR-014 to FR-017 |

### Implementation Notes
- User profile loaded on authentication
- Profile passed to agent as context parameter
- Personalization affects prompt (experience level → explanation depth)

---

## 4. Translation: Agent-based vs Static i18n

### Decision
**Agent-based, on-demand translation**

### Rationale
- **Flexibility**: Can translate any chapter without pre-generating all translations
- **Quality**: LLM translation typically higher quality than static translation tools
- **Caching**: Results cached in Neon Postgres, avoiding regeneration
- **Reuses infrastructure**: Same agent pattern as Q&A, no new dependencies
- **Cost-effective**: Only translate chapters users actually request

### Alternatives Considered

| Approach | Pros | Cons | Why Rejected |
|----------|------|------|--------------|
| Static i18n (pre-translated files) | Instant load | Requires manual translation, doesn't scale | Violates "AI-generated" requirement |
| Real-time translation (no cache) | Always fresh | High latency, high cost | Impractical for chapters |
| Third-party translation API | Potentially cheaper | Another dependency, may not meet quality | Adds complexity |

### Implementation Notes
- Translation request → check cache → if miss, invoke translate agent → store result
- TTL-based cache invalidation (e.g., 30 days or manual refresh)
- Progress feedback via streaming or polling for long chapters

---

## 5. Embedding Model Selection

### Decision
**text-embedding-3-small**

### Rationale
- **Cost-effective**: $0.02 per 1M tokens vs $0.13 for large model
- **Sufficient quality**: 1536 dimensions, good performance on semantic similarity
- **Book size**: Single book (~50 chapters) doesn't need highest-quality embeddings
- **Qdrant compatible**: Standard embedding dimensions, no special configuration

### Alternatives Considered

| Model | Dimensions | Cost | Why Rejected |
|-------|------------|------|--------------|
| text-embedding-3-large | 3072 | $0.13/1M | Overkill for book size |
| text-embedding-ada-002 | 1536 | $0.10/1M | Older, same price as 3-small with worse quality |
| Open-source (e.g., sentence-transformers) | Varies | Free | Requires hosting, lower quality |

### Validation
- Benchmark retrieval accuracy against test questions
- Monitor similarity scores to tune confidence threshold

---

## 6. LLM Selection for Responses

### Decision
**gpt-4o-mini**

### Rationale
- **Fast**: Lower latency than gpt-4o, meets <5s response goal
- **Cost-effective**: ~10x cheaper than gpt-4o
- **Sufficient for Q&A**: Book-grounded answers don't require advanced reasoning
- **Context window**: 128k tokens, sufficient for retrieved chunks + conversation history

### Alternatives Considered

| Model | Pros | Cons | Why Rejected |
|-------|------|------|--------------|
| gpt-4o | Highest quality | Higher cost, slower | Unnecessary for Q&A task |
| gpt-3.5-turbo | Cheapest | Quality may suffer for nuanced answers | Quality concern |
| Claude 3 | Good quality | Different SDK, not OpenAI | Violates "OpenAI Agents SDK" requirement |

### Implementation Notes
- Use structured output for consistent response format
- Set temperature=0.3 for factual, consistent answers
- Include source citations in response schema

---

## 7. Confidence Threshold for "Not Covered" Response

### Decision
**0.7 similarity threshold (configurable)**

### Rationale
- **0.7** is a commonly effective threshold for semantic similarity
- Below this, retrieved chunks are likely not relevant enough
- Configurable via environment variable for tuning
- Constitution requires explicit fallback ("Not covered in this book")

### Implementation
```python
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

if max_similarity < CONFIDENCE_THRESHOLD:
    return "Not covered in this book"
```

### Tuning Strategy
1. Collect sample questions (in-scope and out-of-scope)
2. Measure similarity scores for each
3. Adjust threshold to maximize true positives/negatives
4. Monitor in production and adjust as needed

---

## 8. Database Schema Design

### Decision
**5 tables: users, user_preferences, conversations, messages, translations**

### Rationale
- **Normalized**: Avoids duplication, supports complex queries
- **Separation**: User data separate from conversation data
- **Caching**: Translations stored separately for efficient lookup
- **Scalable**: Can add indexes as query patterns emerge

### Schema Overview

```
users
├── id (PK)
├── email
├── password_hash
├── created_at
└── updated_at

user_preferences
├── id (PK)
├── user_id (FK → users)
├── experience_level (enum)
├── preferred_language
└── chapters_read (array)

conversations
├── id (PK)
├── user_id (FK → users, nullable)
├── mode (enum: full_book, selected_text)
├── created_at
└── updated_at

messages
├── id (PK)
├── conversation_id (FK → conversations)
├── role (enum: user, assistant)
├── content
├── source_refs (JSON, nullable)
└── created_at

translations
├── id (PK)
├── chapter_slug
├── target_language
├── content
├── created_at
└── expires_at
```

---

## 9. CORS Configuration

### Decision
**Whitelist GitHub Pages domain + localhost for development**

### Rationale
- **Security**: Only allow requests from known origins
- **Flexibility**: Environment-based configuration
- **Development**: Include localhost for local testing

### Implementation
```python
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

---

## 10. Error Handling Strategy

### Decision
**Structured error responses with fallback behavior**

### Rationale
- **User-friendly**: Clear messages for frontend to display
- **Debugging**: Error codes for troubleshooting
- **Resilience**: Graceful degradation when services unavailable

### Error Response Schema
```json
{
  "error": {
    "code": "RETRIEVAL_FAILED",
    "message": "Unable to search book content. Please try again.",
    "details": "Qdrant connection timeout"
  }
}
```

### Fallback Behaviors
| Scenario | Fallback |
|----------|----------|
| Qdrant unavailable | Return error, suggest retry |
| OpenAI rate limit | Queue request, notify user of delay |
| Translation fails | Offer retry, show English content |
| Auth service down | Allow unauthenticated access |

---

## Summary of Decisions

| Area | Decision | ADR Candidate? |
|------|----------|----------------|
| Chunking | 512 tokens, 50 overlap | Yes |
| Agent Architecture | Single orchestrator with tools | Yes |
| Personalization | Server-side | No (straightforward) |
| Translation | Agent-based, cached | No (straightforward) |
| Embedding Model | text-embedding-3-small | No (cost decision) |
| LLM | gpt-4o-mini | No (cost decision) |
| Confidence Threshold | 0.7 (configurable) | No (tunable) |
| Database | 5-table normalized schema | No (standard pattern) |
| CORS | Whitelist-based | No (standard security) |
| Error Handling | Structured responses + fallbacks | No (standard pattern) |

---

## ADR Suggestions

Based on this research, the following decisions warrant formal Architecture Decision Records:

1. **Chunking Strategy** - Impacts retrieval quality significantly
2. **Agent Architecture** - Defines system extensibility

📋 Architectural decision detected: Chunking strategy (512 tokens with overlap) and single-agent architecture. Document reasoning and tradeoffs? Run `/sp.adr "RAG Chunking and Agent Architecture"`
