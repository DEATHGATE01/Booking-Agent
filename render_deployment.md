# 🚀 Render.com Deployment Guide for TailorTalk

Render.com is more reliable than Railway for Python apps with complex dependencies like LangChain.

## Step 1: Prepare Your Repository

Ensure your GitHub repository is up to date:
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin master
```

## Step 2: Deploy Backend (FastAPI)

### 2.1 Create Backend Service
1. Go to https://render.com
2. Sign up/login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure the backend service:

**Service Details:**
- **Name**: `tailortalk-backend`
- **Environment**: `Python 3`
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.2 Backend Environment Variables
Add these in Render dashboard:
```
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/service-account-key.json
GOOGLE_CALENDAR_ID=imdeathgate@gmail.com
GEMINI_API_KEY=AIzaSyCbZ0sh8YwnLDS9AOp-ggjyoPs9QeAvSEE
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
TIMEZONE=UTC
PYTHONPATH=/opt/render/project/src
```

### 2.3 Upload Service Account File
1. In your service dashboard, go to "Files"
2. Upload `service-account-key.json` to `credentials/` folder
3. Or add the JSON content as an environment variable:
   - Variable: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Value: Copy entire contents of your service-account-key.json

### 2.4 Deploy Backend
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. **Save the backend URL**: `https://tailortalk-backend.onrender.com`

## Step 3: Deploy Frontend (Streamlit)

### 3.1 Create Frontend Service
1. Click "New +" → "Web Service" again
2. Same GitHub repository
3. Configure the frontend service:

**Service Details:**
- **Name**: `tailortalk-frontend`
- **Environment**: `Python 3`
- **Root Directory**: `frontend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

### 3.2 Frontend Environment Variables
```
API_BASE_URL=https://tailortalk-backend.onrender.com/api/v1
STREAMLIT_PORT=8501
```

### 3.3 Deploy Frontend
1. Click "Create Web Service"
2. Wait for deployment
3. **Save the frontend URL**: `https://tailortalk-frontend.onrender.com`

## Step 4: Test Your Deployment

1. Visit your frontend URL: `https://tailortalk-frontend.onrender.com`
2. Test the booking conversation:
   - "Book a meeting tomorrow at 2 PM"
   - Should get proper AI responses
   - Calendar integration should work

## Step 5: Verify API Endpoints

Test backend directly:
- Health check: `https://tailortalk-backend.onrender.com/health`
- API docs: `https://tailortalk-backend.onrender.com/docs`

## 🎯 TailorTalk Assignment Submission

You now have:
- ✅ **Backend API**: `https://tailortalk-backend.onrender.com`
- ✅ **Frontend App**: `https://tailortalk-frontend.onrender.com`
- ✅ **GitHub Repository**: Complete source code
- ✅ **Live Demo**: Working conversational AI booking agent

## 🚨 Common Issues & Solutions

### Issue: "Module not found" errors
**Solution**: Ensure `requirements.txt` includes all dependencies

### Issue: Service account file not found
**Solution**: Either upload file to `credentials/` folder or use environment variable approach

### Issue: CORS errors between frontend/backend
**Solution**: Backend already configured with CORS middleware for all origins

### Issue: App sleeping (free tier)
**Solution**: 
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- This is normal for free tier

## 🔧 Troubleshooting Commands

If deployment fails, check logs in Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Look for error messages

## 💡 Pro Tips

1. **Free Tier Limitations**: 
   - Services sleep after 15 minutes
   - 750 hours/month limit
   - Consider upgrading for production

2. **Custom Domains**: 
   - You can add custom domains in service settings
   - Useful for professional submission

3. **Environment Variables**: 
   - Can be updated anytime without redeployment
   - Use for sensitive information

Perfect for TailorTalk internship submission! 🎉
