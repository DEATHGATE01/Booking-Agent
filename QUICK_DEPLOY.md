# 🚀 Quick Railway Deployment Guide

## Step 1: Prepare Environment Variables

Create these environment variables for Railway deployment:

### Backend Environment Variables:
```
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/service-account-key.json
GOOGLE_CALENDAR_ID=imdeathgate@gmail.com
GEMINI_API_KEY=AIzaSyCbZ0sh8YwnLDS9AOp-ggjyoPs9QeAvSEE
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
TIMEZONE=UTC
```

### Frontend Environment Variables:
```
API_BASE_URL=https://your-backend-url.railway.app/api/v1
STREAMLIT_PORT=8501
```

## Step 2: Deploy Backend First

1. Go to https://railway.app
2. Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Select "backend" as root directory
7. Add all backend environment variables
8. Upload service-account-key.json file
9. Deploy and save the backend URL

## Step 3: Deploy Frontend

1. Create new Railway service
2. Same repository, select "frontend" as root directory  
3. Add frontend environment variables (use backend URL from step 2)
4. Deploy

## Step 4: Test Deployment

Visit your frontend URL and test:
- "Book a meeting tomorrow at 2 PM"
- Should get proper responses and calendar integration

## Alternative: Render Deployment

If Railway doesn't work, try Render.com:
1. Connect GitHub repo
2. Create Web Service for backend (Python)
3. Create Web Service for frontend (Python)
4. Same environment variables as above

## Alternative: Fly.io Deployment

1. Install Fly CLI
2. Run `fly launch` in backend and frontend directories
3. Configure environment variables
4. Deploy with `fly deploy`

## 🎯 Assignment Submission

After deployment, you'll have:
- ✅ Backend API: https://your-backend.railway.app
- ✅ Frontend App: https://your-frontend.railway.app  
- ✅ GitHub repo with full source code
- ✅ Working conversational AI booking agent

Perfect for TailorTalk internship submission! 🎉
