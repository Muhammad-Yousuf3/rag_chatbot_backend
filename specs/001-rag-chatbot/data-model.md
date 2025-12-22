# Data Model: RAG Chatbot and Personalization Layer

**Feature**: 001-rag-chatbot
**Date**: 2025-12-16
**Database**: Neon Serverless Postgres

## Overview

This document defines the data entities, relationships, and validation rules for the RAG Chatbot system. The schema supports user management, conversation history, and translation caching.

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────┐
│     users       │       │  user_preferences   │
├─────────────────┤       ├─────────────────────┤
│ id (PK)         │◄──────│ user_id (FK)        │
│ email           │   1:1 │ experience_level    │
│ password_hash   │       │ preferred_language  │
│ created_at      │       │ chapters_read       │
│ updated_at      │       │ created_at          │
└────────┬────────┘       │ updated_at          │
         │                └─────────────────────┘
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│  conversations  │       │    messages     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ conversation_id │
│ user_id (FK)?   │   1:N │ id (PK)         │
│ mode            │       │ role            │
│ created_at      │       │ content         │
│ updated_at      │       │ source_refs     │
└─────────────────┘       │ created_at      │
                          └─────────────────┘

┌─────────────────┐
│  translations   │
├─────────────────┤
│ id (PK)         │
│ chapter_slug    │  (standalone cache table)
│ target_language │
│ content         │
│ created_at      │
│ expires_at      │
└─────────────────┘
```

---

## Entities

### 1. User

Represents an authenticated reader of the book.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password (bcrypt) |
| created_at | TIMESTAMP | NOT NULL, default NOW() | Account creation time |
| updated_at | TIMESTAMP | NOT NULL, default NOW() | Last update time |

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email must be unique (case-insensitive)
- Password must meet minimum complexity (handled at API layer)

**Indexes**:
- `idx_users_email` on `email` (unique)

---

### 2. UserPreference

Stores user preferences for personalization.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → users.id, UNIQUE | Reference to user |
| experience_level | ENUM | NOT NULL, default 'intermediate' | beginner, intermediate, advanced |
| preferred_language | VARCHAR(10) | NOT NULL, default 'en' | Language code (en, ur) |
| chapters_read | TEXT[] | NOT NULL, default '{}' | Array of chapter slugs read |
| created_at | TIMESTAMP | NOT NULL, default NOW() | Record creation time |
| updated_at | TIMESTAMP | NOT NULL, default NOW() | Last update time |

**Validation Rules**:
- One preference record per user (1:1 relationship)
- experience_level must be one of: 'beginner', 'intermediate', 'advanced'
- preferred_language must be supported: 'en', 'ur'

**Indexes**:
- `idx_user_preferences_user_id` on `user_id` (unique)

---

### 3. Conversation

Represents a chat session between user and chatbot.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| user_id | UUID | FK → users.id, NULLABLE | User (null for anonymous) |
| mode | ENUM | NOT NULL, default 'full_book' | full_book, selected_text |
| selected_text | TEXT | NULLABLE | Text selected (if mode=selected_text) |
| created_at | TIMESTAMP | NOT NULL, default NOW() | Session start time |
| updated_at | TIMESTAMP | NOT NULL, default NOW() | Last activity time |

**Validation Rules**:
- mode must be one of: 'full_book', 'selected_text'
- If mode='selected_text', selected_text should be non-empty
- Anonymous conversations (user_id=NULL) are allowed

**Indexes**:
- `idx_conversations_user_id` on `user_id`
- `idx_conversations_created_at` on `created_at`

---

### 4. Message

Individual message in a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| conversation_id | UUID | FK → conversations.id, NOT NULL | Parent conversation |
| role | ENUM | NOT NULL | user, assistant |
| content | TEXT | NOT NULL | Message content |
| source_refs | JSONB | NULLABLE | Source citations (for assistant) |
| created_at | TIMESTAMP | NOT NULL, default NOW() | Message timestamp |

**Validation Rules**:
- role must be one of: 'user', 'assistant'
- content must not be empty
- source_refs only populated for assistant messages

**Source Refs Schema**:
```json
{
  "sources": [
    {
      "chapter": "chapter-1-introduction",
      "section": "Getting Started",
      "relevance": 0.92
    }
  ]
}
```

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id`
- `idx_messages_created_at` on `created_at`

---

### 5. Translation

Cached chapter translations.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique identifier |
| chapter_slug | VARCHAR(255) | NOT NULL | Chapter identifier |
| target_language | VARCHAR(10) | NOT NULL | Language code (ur) |
| content | TEXT | NOT NULL | Translated content |
| created_at | TIMESTAMP | NOT NULL, default NOW() | Translation time |
| expires_at | TIMESTAMP | NULLABLE | Cache expiration (optional) |

**Validation Rules**:
- Unique constraint on (chapter_slug, target_language)
- target_language currently only supports 'ur' (Urdu)
- content must not be empty

**Indexes**:
- `idx_translations_chapter_lang` on `(chapter_slug, target_language)` (unique)
- `idx_translations_expires_at` on `expires_at`

---

## Enums

### ExperienceLevel
```sql
CREATE TYPE experience_level AS ENUM ('beginner', 'intermediate', 'advanced');
```

### ConversationMode
```sql
CREATE TYPE conversation_mode AS ENUM ('full_book', 'selected_text');
```

### MessageRole
```sql
CREATE TYPE message_role AS ENUM ('user', 'assistant');
```

---

## Migrations

### Initial Migration (001_initial_schema.sql)

```sql
-- Enums
CREATE TYPE experience_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE conversation_mode AS ENUM ('full_book', 'selected_text');
CREATE TYPE message_role AS ENUM ('user', 'assistant');

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- User Preferences
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    experience_level experience_level NOT NULL DEFAULT 'intermediate',
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'en',
    chapters_read TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- Conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    mode conversation_mode NOT NULL DEFAULT 'full_book',
    selected_text TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    source_refs JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Translations
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_slug VARCHAR(255) NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    UNIQUE(chapter_slug, target_language)
);

CREATE INDEX idx_translations_chapter_lang ON translations(chapter_slug, target_language);
CREATE INDEX idx_translations_expires_at ON translations(expires_at);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Vector Storage (Qdrant)

Book content is stored in Qdrant Cloud as vector embeddings. This is separate from the relational schema above.

### Collection: book_chunks

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique chunk identifier |
| vector | float[1536] | text-embedding-3-small embedding |
| payload.chapter_slug | string | Chapter identifier |
| payload.section | string | Section title |
| payload.content | string | Original text content |
| payload.chunk_index | int | Position within chapter |

**Collection Configuration**:
```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  }
}
```

---

## State Transitions

### Conversation Lifecycle

```
[Created] ──── user sends message ────► [Active]
    │                                       │
    │                                       │
    │                                       ▼
    │                               [Message Added]
    │                                       │
    │                                       │
    └───────────────────────────────────────┘
                                            │
                                            │ (no activity for 30 min)
                                            ▼
                                       [Inactive]
```

### Translation Cache Lifecycle

```
[Not Cached] ── request ──► [Generating] ── complete ──► [Cached]
                                │                            │
                                │ (error)                    │ (expires_at reached)
                                ▼                            ▼
                            [Failed]                   [Expired] ── request ──► [Generating]
```
