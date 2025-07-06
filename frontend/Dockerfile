# Frontend Dockerfile for TailorTalk Booking Agent
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
COPY streamlit_app.py .
COPY .streamlit/ .streamlit/

# Set environment variables
ENV PORT=8501

# Expose port (Railway will override with $PORT)
EXPOSE $PORT

# Start command (Railway will use its own command or the one in railway.toml)
CMD streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
