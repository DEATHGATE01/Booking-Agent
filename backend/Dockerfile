# Backend Dockerfile for TailorTalk Booking Agent
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY credentials/ ./credentials/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose port (Railway will override with $PORT)
EXPOSE $PORT

# Start command (Railway will use its own command or the one in railway.toml)
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
