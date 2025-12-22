# Quickstart Guide: RAG Chatbot

**Feature**: 001-rag-chatbot
**Date**: 2025-12-16

This guide helps you set up the RAG Chatbot development environment and run the system locally.

---

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+ (for frontend)
- **Git**: 2.30+
- **Docker**: (optional, for containerized development)

### External Services (Free Tiers)

You'll need accounts for:
1. **OpenAI API** - [platform.openai.com](https://platform.openai.com)
2. **Qdrant Cloud** - [cloud.qdrant.io](https://cloud.qdrant.io)
3. **Neon Postgres** - [neon.tech](https://neon.tech)

---

## 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd RAG_CHATBOT

# Checkout feature branch
git checkout 001-rag-chatbot
```

---

## 2. Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.3 Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required environment variables:**

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.cloud
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres
NEON_DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# CORS (add your frontend URL)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CONFIDENCE_THRESHOLD=0.7
```

### 2.4 Initialize Database

```bash
# Run migrations
alembic upgrade head
```

### 2.5 Ingest Book Content

```bash
# Index book content into Qdrant
python scripts/ingest_book.py --source ../docs
```

This script will:
1. Read markdown files from the book
2. Chunk content (512 tokens, 50 overlap)
3. Generate embeddings via OpenAI
4. Upload to Qdrant collection

### 2.6 Start Backend Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --port 8000
```

**Verify**: Open http://localhost:8000/docs for Swagger UI

---

## 3. Frontend Setup

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Configure API Endpoint

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.3 Start Development Server

```bash
npm run dev
```

**Verify**: Open http://localhost:3000

---

## 4. Quick Verification

### 4.1 Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-16T12:00:00Z",
  "services": {
    "database": "up",
    "qdrant": "up",
    "openai": "up"
  }
}
```

### 4.2 Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this book about?"}'
```

Expected response:
```json
{
  "message": "This book covers...",
  "conversation_id": "uuid-here",
  "sources": [
    {"chapter": "chapter-1-introduction", "section": "Overview", "relevance": 0.95}
  ],
  "is_covered": true
}
```

### 4.3 Test "Not Covered" Response

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is quantum computing?"}'
```

Expected response (assuming not in book):
```json
{
  "message": "Not covered in this book.",
  "conversation_id": "uuid-here",
  "sources": [],
  "is_covered": false
}
```

### 4.4 Test Selected-Text Mode

```bash
curl -X POST http://localhost:8000/api/chat/selected \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize this text",
    "selected_text": "Python is a high-level programming language known for its readability and versatility."
  }'
```

---

## 5. Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/contract/ -v

# Frontend tests
cd frontend
npm test
```

### Code Formatting

```bash
# Backend
cd backend
black src/ tests/
isort src/ tests/
ruff check src/ tests/

# Frontend
cd frontend
npm run lint
npm run format
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 6. Docker Development (Optional)

### Build and Run

```bash
# Build images
docker-compose build

# Start all services
docker-compose up

# Start in background
docker-compose up -d
```

### Docker Compose Services

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

## 7. Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY not set` | Check `.env` file exists and is loaded |
| `Qdrant connection failed` | Verify URL and API key; check firewall |
| `Database connection error` | Check Neon connection string; verify SSL |
| `CORS error in browser` | Add frontend URL to `CORS_ORIGINS` |
| `Empty search results` | Run `ingest_book.py` to index content |

### Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend
```

### Reset Database

```bash
# Drop and recreate tables
alembic downgrade base
alembic upgrade head
```

### Re-index Book Content

```bash
# Clear Qdrant collection and re-index
python scripts/ingest_book.py --clear --source ../docs
```

---

## 8. Next Steps

1. **Run the test suite** to verify setup
2. **Try the chat widget** in the frontend
3. **Test selected-text mode** by highlighting text
4. **Review the API docs** at `/docs`

For implementation details, see:
- [plan.md](./plan.md) - Architecture overview
- [data-model.md](./data-model.md) - Database schema
- [contracts/openapi.yaml](./contracts/openapi.yaml) - API specification
