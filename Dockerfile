# Root Dockerfile - Forces Railway to use Docker
# This is a fallback to ensure Railway uses Docker instead of Nixpacks

FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . .

# This Dockerfile exists only to force Docker detection
# Actual builds should use backend/Dockerfile or frontend/Dockerfile

# Default to backend if no specific service is selected
CMD ["echo", "Please deploy backend and frontend as separate services"]
