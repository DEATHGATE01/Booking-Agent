# Railway Deployment Guide - Docker Fix

## Issue: Railway Using Nixpacks Instead of Docker

If Railway is still using Nixpacks instead of Docker despite our configuration, follow these steps:

### Step 1: Force Docker Usage

1. **Delete any existing Railway deployments** for this project
2. **Remove `.railway/` directory** if it exists (contains cached settings)
3. **Ensure these files are in place:**
   - Root `railway.toml` (multi-service config)
   - `backend/Dockerfile` and `frontend/Dockerfile`
   - `backend/Procfile` and `frontend/Procfile`
   - Root `.dockerignore`

### Step 2: Manual Railway Configuration

1. **Create New Railway Project:**
   ```bash
   railway login
   railway init
   ```

2. **Deploy Backend Service:**
   ```bash
   cd backend
   railway up --service backend
   ```

3. **Deploy Frontend Service:**
   ```bash
   cd ../frontend
   railway up --service frontend
   ```

### Step 3: Environment Variables

**Backend Service:**
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`: (your service account JSON as string)
- `GEMINI_API_KEY`: (your Gemini API key)
- `PYTHONPATH`: `/app`
- `PORT`: (Railway sets this automatically)

**Frontend Service:**
- `BACKEND_URL`: (URL of your deployed backend service)
- `PORT`: (Railway sets this automatically)

### Step 4: Build Settings (In Railway Dashboard)

**For Backend:**
- Build Command: `docker build -t backend .`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Builder: `DOCKERFILE`

**For Frontend:**
- Build Command: `docker build -t frontend .`
- Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
- Builder: `DOCKERFILE`

### Step 5: Manual Docker Build (If Railway Still Uses Nixpacks)

If Railway continues to ignore Docker, you can force it:

1. **Go to Railway Dashboard**
2. **Service Settings > Builder**
3. **Select "Dockerfile"**
4. **Set Dockerfile Path: "Dockerfile"**
5. **Save and Redeploy**

### Alternative: Single Service Deployment

If multi-service deployment fails, deploy as separate projects:

1. **Backend Project:**
   ```bash
   railway init booking-agent-backend
   cd backend
   railway up
   ```

2. **Frontend Project:**
   ```bash
   railway init booking-agent-frontend
   cd frontend
   railway up
   ```

### Troubleshooting

**"pip not found" error = Nixpacks is being used**
- Manually set Builder to "Dockerfile" in Railway dashboard
- Delete `.railway/` directory and redeploy
- Try deploying backend and frontend as separate Railway projects

**Build fails on requirements.txt:**
- Check that Dockerfile exists in the service directory
- Verify railway.toml points to correct Dockerfile path
- Ensure Python 3.11 base image is being used

**Port issues:**
- Railway automatically sets $PORT environment variable
- Our Dockerfiles and start commands use $PORT
- Don't hardcode port numbers

### Success Indicators

✅ Build logs show "Building with Dockerfile"
✅ No "Using Nixpacks" messages
✅ Python 3.11 environment
✅ All dependencies install correctly
✅ Services start on Railway-assigned ports

## Quick Deploy Commands

```bash
# Clean deployment
rm -rf .railway/
git add .
git commit -m "Force Docker deployment"
git push

# Backend
cd backend && railway up --service backend

# Frontend  
cd frontend && railway up --service frontend
```
