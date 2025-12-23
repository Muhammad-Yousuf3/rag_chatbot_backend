# Base Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy backend dependencies first (for caching)
COPY backend/requirements.txt ./backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy the entire backend
COPY backend/ ./backend/

# Expose the port FastAPI will run on
EXPOSE 8000

# Start FastAPI
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
