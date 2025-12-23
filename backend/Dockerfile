FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Set Python path to include the app directory
ENV PYTHONPATH=/app

EXPOSE 8000

# Use PORT env variable for Railway compatibility
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
