# RAG Chatbot with Personalization

A full-stack RAG (Retrieval-Augmented Generation) chatbot application for technical books with personalization features, Urdu translation, and selected-text answering capabilities.

## Features

- **Book-Grounded Q&A**: Ask questions and receive accurate answers derived from indexed book content
- **Selected-Text Answering**: Select text and ask questions restricted to that selection
- **Urdu Translation**: AI-generated Urdu translations with caching
- **User Personalization**: Experience-level-aware responses and conversation history
- **Source Citations**: All answers include references to the original book content

## Architecture

```
RAG_CHATBOT/
├── backend/                 # FastAPI Python backend
│   ├── src/
│   │   ├── api/            # REST API endpoints
│   │   ├── agents/         # OpenAI Agents SDK integration
│   │   ├── services/       # Business logic services
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── middleware/     # Rate limiting, etc.
│   │   └── utils/          # Logging, helpers
│   ├── tests/              # Unit, integration, contract tests
│   └── scripts/            # Book ingestion scripts
├── frontend/               # React components for Docusaurus
│   ├── src/
│   │   ├── components/     # ChatWidget, TextSelector, etc.
│   │   ├── hooks/          # useChat, useAuth, useTranslation
│   │   └── services/       # API client
│   └── tests/
└── docker-compose.yml      # Multi-container orchestration
```

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI Agents SDK**: Agent orchestration
- **Qdrant Cloud**: Vector database for semantic search
- **Neon Postgres**: Serverless PostgreSQL
- **SQLAlchemy**: Async ORM
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI components
- **TypeScript**: Type safety
- **Docusaurus**: Documentation site integration

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### External Services (Free Tiers)

1. **OpenAI API**: [platform.openai.com](https://platform.openai.com)
2. **Qdrant Cloud**: [cloud.qdrant.io](https://cloud.qdrant.io)
3. **Neon Postgres**: [neon.tech](https://neon.tech)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Ingest book content
python scripts/ingest_book.py --source ../docs

# Start server
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run start
```

### Docker Setup (Alternative)

```bash
# Build and run all services
docker-compose up --build

# Or run in background
docker-compose up -d
```

## API Endpoints

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a chat message (full book mode) |
| POST | `/api/chat/selected` | Send a message about selected text |
| GET | `/api/chat/conversations` | Get user's conversations |
| GET | `/api/chat/conversations/{id}` | Get conversation detail |

### Translation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/translate/{chapterSlug}` | Get cached translation |
| POST | `/api/translate/{chapterSlug}` | Request new translation |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user |
| PUT | `/api/auth/preferences` | Update user preferences |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service health status |

## Configuration

Key environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `QDRANT_URL` | Qdrant Cloud cluster URL | Yes |
| `QDRANT_API_KEY` | Qdrant API key | Yes |
| `DATABASE_URL` | Neon Postgres connection string | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | Yes |
| `CONFIDENCE_THRESHOLD` | RAG retrieval threshold (default: 0.7) | No |

See `backend/.env.example` for all configuration options.

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/contract/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend formatting and linting
cd backend
black src/ tests/
ruff check src/ tests/

# Frontend linting
cd frontend
npm run lint
npm run format
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## User Stories

1. **US1 - Book-Grounded Q&A**: Users can ask questions and receive accurate answers from indexed book content
2. **US2 - Selected-Text Answering**: Users can select text and ask questions restricted to that selection
3. **US3 - Urdu Translation**: Users can request AI-generated Urdu translations of chapters
4. **US4 - Personalization**: Users can set experience levels and get adapted responses

## API Documentation

When running in development mode, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

1. Create a feature branch from `001-rag-chatbot`
2. Make changes following the existing code style
3. Write tests for new functionality
4. Submit a pull request

## License

MIT License
