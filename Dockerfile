# Root Dockerfile - Backend Service for Railway
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY ./backend/app/ ./app/

# Create empty credentials directory (will be populated via environment variables)
RUN mkdir -p ./credentials

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start command for backend
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
