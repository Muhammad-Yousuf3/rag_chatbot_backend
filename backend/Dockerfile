FROM python:3.11-slim

WORKDIR /app

# Copy requirements from backend folder
COPY backend/requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend ./backend

# Set Python path so "src" is importable
ENV PYTHONPATH=/app/backend

EXPOSE 8080

# Railway provides PORT automatically
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
