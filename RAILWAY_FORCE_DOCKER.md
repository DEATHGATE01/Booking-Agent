# Complete Railway Deployment Fix Script

## ISSUE: Railway keeps using Nixpacks instead of Docker

This is a common Railway issue. Here are multiple solutions:

## Solution 1: Manual Dashboard Configuration (RECOMMENDED)

1. **Go to Railway Dashboard**
2. **Delete existing services** (if any)
3. **Create new service from GitHub**
4. **In Service Settings:**
   - Builder: **DOCKERFILE**
   - Root Directory: `backend` (for backend) or `frontend` (for frontend)
   - Dockerfile Path: `Dockerfile`
   - Build Command: (leave empty)
   - Start Command: 
     - Backend: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Frontend: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

## Solution 2: Deploy from CLI with Force

```bash
# Clean any Railway cache
rm -rf .railway/

# Backend deployment
cd backend
railway login
railway init booking-agent-backend
railway up --detach

# Frontend deployment  
cd ../frontend
railway init booking-agent-frontend
railway up --detach
```

## Solution 3: Monorepo Split

Deploy backend and frontend as completely separate Railway projects:

1. **Create new GitHub repos:**
   - `booking-agent-backend` (copy just /backend contents to root)
   - `booking-agent-frontend` (copy just /frontend contents to root)

2. **Deploy each separately on Railway**

## Solution 4: Alternative Platforms

If Railway continues to have issues:

### Fly.io (Recommended)
```bash
# Install flyctl
# Backend
cd backend
fly launch --dockerfile Dockerfile
fly deploy

# Frontend
cd frontend  
fly launch --dockerfile Dockerfile
fly deploy
```

### Render
- Works well with our existing configuration
- No Docker build issues
- Supports both services

### Vercel (Frontend only)
- Deploy frontend to Vercel
- Backend to Railway/Fly.io

## Files Added for Railway Fix:

- `nixpacks.toml` (disables Nixpacks)
- Root `Dockerfile` (forces Docker detection)
- Updated `railway.toml` files
- `Procfile` backup commands

## Environment Variables:

**Backend:**
```
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type": "service_account",...}
GEMINI_API_KEY=your_key_here
PYTHONPATH=/app
```

**Frontend:**
```
BACKEND_URL=https://your-backend-service.railway.app
```

## Debugging Railway Build:

1. Check build logs for "Using Nixpacks" vs "Building with Dockerfile"
2. If still using Nixpacks: manually set Builder in dashboard
3. Verify Dockerfile exists in correct location
4. Try deploying backend and frontend as separate projects

## Success Indicators:

✅ Build logs show "Building with Dockerfile"
✅ No "Using Nixpacks" messages
✅ Python 3.11 environment
✅ pip install works correctly
✅ Services start successfully

## Last Resort: Copy Template

If nothing works, I can create a minimal working template that Railway definitely recognizes as a Docker project.
