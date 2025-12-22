#!/bin/bash
# Startup script for RAG Chatbot Backend
# Runs database migrations before starting the server

set -e

echo "Starting RAG Chatbot Backend..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Migrations complete. Starting server..."

# Start the FastAPI application
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
