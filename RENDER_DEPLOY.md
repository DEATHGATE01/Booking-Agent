# 🚀 Alternative Deployment: Render.com

## Why Render.com?
- More reliable than Railway for Python apps
- Better handling of dependencies
- Free tier available
- Good for TailorTalk assignment submission

## Render Deployment Steps:

### 1. Deploy Backend on Render

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `tailortalk-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

6. Add Environment Variables:
   ```
   GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/service-account-key.json
   GOOGLE_CALENDAR_ID=imdeathgate@gmail.com
   GEMINI_API_KEY=AIzaSyCbZ0sh8YwnLDS9AOp-ggjyoPs9QeAvSEE
   API_HOST=0.0.0.0
   DEBUG=False
   TIMEZONE=UTC
   ```

7. Upload your `service-account-key.json` file to the credentials folder
8. Deploy and save the backend URL

### 2. Deploy Frontend on Render

1. Create another Web Service
2. Same repository, configure:
   - **Name**: `tailortalk-frontend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
   - **Root Directory**: `frontend`

3. Add Environment Variables:
   ```
   API_BASE_URL=https://tailortalk-backend.onrender.com/api/v1
   ```

### 3. Alternative: Streamlit Cloud (Frontend Only)

For the frontend, you can also use Streamlit Cloud:
1. Go to https://share.streamlit.io
2. Connect GitHub repository
3. Deploy from `frontend/streamlit_app.py`
4. Set API_BASE_URL to your Render backend

## 🎯 Result:
- ✅ Backend: `https://tailortalk-backend.onrender.com`
- ✅ Frontend: `https://tailortalk-frontend.onrender.com`
- ✅ Working conversational AI booking agent

Perfect for TailorTalk submission! 🎉
