---
title: Rag Chatbot With Book
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# RAG Chatbot API

Book-grounded RAG chatbot with personalization and translation capabilities.

## Features

- FastAPI-based REST API
- Vector search using Qdrant
- Google Gemini AI integration
- User authentication with JWT
- Rate limiting and CORS support
- PostgreSQL/SQLite database support

## Environment Variables

Configure the following secrets in your Hugging Face Space settings:

### Required Variables
- `GEMINI_API_KEY` - Your Google Gemini API key
- `QDRANT_URL` - Your Qdrant instance URL
- `QDRANT_API_KEY` - Your Qdrant API key
- `JWT_SECRET_KEY` - Secret key for JWT token generation

### Optional Variables
- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `OPENAI_API_KEY` - OpenAI API key (optional fallback)
- `ENVIRONMENT` - Environment name (default: production)
- `LOG_LEVEL` - Logging level (default: INFO)
- `CORS_ORIGINS` - Comma-separated allowed origins
- `QDRANT_COLLECTION_NAME` - Qdrant collection name (default: book_chunks)
- `CONFIDENCE_THRESHOLD` - RAG confidence threshold (default: 0.7)
- `EMBEDDING_MODEL` - Embedding model name (default: models/embedding-001)
- `CHAT_MODEL` - Chat model name (default: gemini-2.5-flash)
- `MAX_CONTEXT_CHUNKS` - Maximum chunks to retrieve (default: 5)

## API Documentation

Once deployed, visit:
- `/docs` - Swagger UI documentation
- `/redoc` - ReDoc documentation
- `/health` - Health check endpoint

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure your variables

3. Run the server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
