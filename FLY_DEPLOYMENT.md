# Fly.io Deployment Guide - Alternative to Railway

## Why Fly.io?
- Excellent Docker support (never ignores Dockerfiles)
- Reliable builds with Python 3.11
- Simple deployment process
- Great for both backend and frontend

## Prerequisites
1. Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/
2. Create Fly.io account

## Backend Deployment

```bash
# Navigate to backend
cd backend

# Login to Fly.io
fly auth login

# Initialize and deploy
fly launch --dockerfile Dockerfile --name booking-agent-backend

# Set environment variables
fly secrets set GOOGLE_APPLICATION_CREDENTIALS_JSON='{"type": "service_account",...}'
fly secrets set GEMINI_API_KEY="your_gemini_key_here"
fly secrets set PYTHONPATH="/app"

# Deploy
fly deploy
```

## Frontend Deployment

```bash
# Navigate to frontend
cd ../frontend

# Initialize and deploy
fly launch --dockerfile Dockerfile --name booking-agent-frontend

# Set environment variables
fly secrets set BACKEND_URL="https://booking-agent-backend.fly.dev"

# Deploy
fly deploy
```

## Fly.io Configuration Files

I'll create `fly.toml` files for both services that ensure proper deployment.

## Advantages over Railway:
- ✅ Always uses Dockerfiles
- ✅ Better Python/Docker support
- ✅ More reliable builds
- ✅ Global edge deployment
- ✅ Easy scaling

## Cost:
- Free tier available
- Pay-as-you-scale pricing
- Similar to Railway costs
