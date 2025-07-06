# 🚀 TailorTalk Assignment Deployment Guide

## 🎯 Assignment Requirement: "Host both backend and frontend using platforms like Railway, Render, Fly.io, etc."

This guide helps you deploy your TailorTalk Booking Agent to meet the submission requirements.

## 🌟 Recommended: Railway Deployment

Railway is the easiest option for the assignment submission.

### 📋 Pre-deployment Checklist
- ✅ Google Calendar Service Account JSON file ready
- ✅ OpenAI or Gemini API key ready
- ✅ GitHub repository created and pushed
- ✅ Calendar shared with service account email

### 🚀 Railway Deployment Steps

#### 1. Prepare Your Repository
```bash
# Ensure your code is pushed to GitHub
git add .
git commit -m "Ready for TailorTalk assignment submission"
git push origin main
```

#### 2. Deploy Backend (FastAPI)
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `booking-agent` repository
5. Choose "backend" folder as root directory
6. Set environment variables:
   ```
   GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/service-account-key.json
   GOOGLE_CALENDAR_ID=your-email@gmail.com
   OPENAI_API_KEY=sk-your-key-here
   API_HOST=0.0.0.0
   API_PORT=8000
   DEBUG=False
   ```
7. Upload your `service-account-key.json` file
8. Deploy and note the backend URL

#### 3. Deploy Frontend (Streamlit)
1. Create another Railway service
2. Same repository, choose "frontend" folder
3. Set environment variables:
   ```
   API_BASE_URL=https://your-backend-url.railway.app/api/v1
   ```
4. Deploy and note the frontend URL

#### 4. Update CORS Settings
- Edit backend environment to allow frontend domain
- Add frontend URL to CORS origins

## 🔧 Alternative: Render Deployment

### Backend Deployment
1. Go to [Render.com](https://render.com)
2. Connect GitHub repository
3. Create "Web Service"
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

### Frontend Deployment
1. Create another Web Service
2. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
   - **Root Directory**: `frontend`

## ⚡ Quick Deploy with Fly.io

### Install Fly CLI
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh
# or on Windows: iwr https://fly.io/install.ps1 -useb | iex
```

### Deploy Backend
```bash
cd backend
fly launch --name tailortalk-backend
fly secrets set OPENAI_API_KEY=your-key
fly secrets set GOOGLE_CALENDAR_ID=your-email@gmail.com
fly deploy
```

### Deploy Frontend
```bash
cd frontend
fly launch --name tailortalk-frontend
fly secrets set API_BASE_URL=https://tailortalk-backend.fly.dev/api/v1
fly deploy
```

## 📝 Environment Variables Reference

### Backend Environment Variables
```env
# Required for assignment
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/service-account-key.json
GOOGLE_CALENDAR_ID=your-calendar@gmail.com
OPENAI_API_KEY=sk-your-openai-key
# OR
GEMINI_API_KEY=your-gemini-key

# Production settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
TIMEZONE=UTC
```

### Frontend Environment Variables
```env
# Point to your deployed backend
API_BASE_URL=https://your-backend-url.railway.app/api/v1
```

## 🧪 Testing Your Deployment

### 1. Test Backend API
```bash
# Check health endpoint
curl https://your-backend-url/health

# Test chat endpoint
curl -X POST "https://your-backend-url/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I want to book a meeting"}'
```

### 2. Test Frontend
- Open your Streamlit URL
- Try a conversation: "Book a meeting tomorrow at 2 PM"
- Verify calendar integration works

### 3. Verify Calendar Integration
- Check your Google Calendar for test bookings
- Ensure service account has proper permissions

## 📋 Submission URLs Template

Once deployed, update your README.md with:

```markdown
## 🌐 TailorTalk Assignment Submission

### 🎯 Live Demo Links
- **Streamlit Frontend**: https://your-app.railway.app
- **FastAPI Backend**: https://your-api.railway.app
- **API Documentation**: https://your-api.railway.app/docs
- **GitHub Repository**: https://github.com/yourusername/tailortalk-booking-agent

### ✅ Assignment Requirements Met
- [x] Conversational AI agent with natural dialogue
- [x] Google Calendar integration via Service Account
- [x] Function calling for booking management
- [x] Hosted backend and frontend
- [x] Working Streamlit URL for live testing
- [x] GitHub repository with complete code
```

## 🏆 Assignment Success Tips

1. **Test Thoroughly**: Make sure booking actually creates calendar events
2. **Document Everything**: Clear README with setup instructions
3. **Handle Errors Gracefully**: Show fallback behavior when APIs fail
4. **Demo Video**: Consider recording a quick Loom video showing the booking flow
5. **Professional Presentation**: Clean UI, good error messages, loading states

## 🆘 Troubleshooting

### Common Deployment Issues
- **CORS Errors**: Make sure backend allows frontend domain
- **Environment Variables**: Double-check all API keys are set correctly
- **Calendar Permissions**: Verify service account email is shared with calendar
- **Port Configuration**: Use `$PORT` environment variable on most platforms

### Quick Fixes
```bash
# Test locally first
./start.ps1  # or ./start.sh

# Check logs on Railway
railway logs

# Check logs on Render
# Use the web dashboard logs section
```

---

**🎉 You're ready to submit an impressive, working AI booking agent!**

Remember: The assignment evaluators will test the live Streamlit URL, so make sure everything works end-to-end before submission.
