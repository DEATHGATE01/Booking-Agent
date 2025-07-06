# 🚀 Quick Deployment Guide for TailorTalk

## 🌟 Recommended: Render.com Deployment

Render.com is more reliable than Railway for Python apps with complex dependencies.

## Step 1: Prepare Environment Variables

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

### Service Account Options:
**Option A**: Upload file to `credentials/` folder in Render
**Option B**: Add as environment variable:
```
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project",...}
```

### Frontend Environment Variables:
```
API_BASE_URL=https://tailortalk-backend.onrender.com/api/v1
STREAMLIT_PORT=8501
```

## Step 2: Deploy on Render.com

### Quick Deploy (Recommended):
1. Go to https://render.com
2. Click "New +" → "Web Service"  
3. **If repos don't show up**: Use "Public Git repository" option
4. Enter: `https://github.com/DEATHGATE01/Booking-Agent.git`
5. Configure backend service manually (see below)
6. Repeat for frontend

### Backend Configuration:
- **Name**: `tailortalk-backend`
- **Language**: `Python 3` (or use Docker with existing Dockerfile)
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Configuration:
- **Name**: `tailortalk-frontend`
- **Language**: `Python 3`
- **Root Directory**: `frontend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

## Step 3: Test Deployment

Visit your frontend URL and test:
- "Book a meeting tomorrow at 2 PM"
- Should get proper AI responses via Gemini and calendar integration

## 🎯 TailorTalk Assignment Submission

After deployment, you'll have:
- ✅ **Backend API**: `https://tailortalk-backend.onrender.com`
- ✅ **Frontend App**: `https://tailortalk-frontend.onrender.com`  
- ✅ **GitHub Repository**: Complete source code
- ✅ **Live Demo**: Working conversational AI booking agent
- ✅ **AI Provider**: Google Gemini (no OpenAI needed)
- ✅ **Calendar Integration**: Google Calendar API

## 🚨 Troubleshooting

### If deployment fails:
1. Check build logs in Render dashboard
2. Ensure all environment variables are set
3. Verify `requirements.txt` files are complete
4. Check service account JSON format

### Common issues:
- **Module not found**: Update requirements.txt
- **Service account error**: Use environment variable approach
- **CORS errors**: Already handled in backend
- **App sleeping**: Normal on free tier (15 min timeout)
- **Gemini API errors**: Check API key is valid and has quota

## 📝 Alternative Platforms

### Railway:
- Similar process but may have Nixpacks build issues
- Use Docker configuration if Python build fails

### Fly.io:
1. Install Fly CLI
2. Run `fly launch` in backend/frontend directories
3. Configure environment variables
4. Deploy with `fly deploy`

Perfect for TailorTalk internship submission using Google Gemini AI! 🎉
