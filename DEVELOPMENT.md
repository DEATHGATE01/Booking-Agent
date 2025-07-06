# 📚 Development Guide - TailorTalk Booking Agent

## 🎯 Project Overview

This project implements a conversational AI booking agent that integrates with Google Calendar to help users schedule appointments through natural language conversation.

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI Application**: RESTful API for handling chat and booking requests
- **AI Service**: Natural language processing using LangChain and LLMs
- **Calendar Service**: Google Calendar API integration
- **Booking Agent**: LangGraph-powered conversational workflow

### Frontend (Streamlit)
- **Chat Interface**: Modern, responsive UI for user interaction
- **Real-time Updates**: Live conversation flow with status indicators
- **Quick Actions**: Pre-built buttons for common booking scenarios

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Google Cloud Project with Calendar API enabled
- OpenAI API key or Google Gemini API key
- Git

### Initial Setup

1. **Clone and Setup**
   ```bash
   git clone <your-repo>
   cd booking-agent
   
   # On Windows
   .\setup.ps1
   
   # On Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure Environment**
   ```bash
   # Edit .env file
   cp .env.example .env
   # Add your API keys and configuration
   ```

3. **Google Calendar Setup**
   - Create Google Cloud Project
   - Enable Calendar API
   - Create Service Account
   - Download JSON credentials
   - Place in `credentials/service-account-key.json`
   - Share your calendar with service account email

4. **Run Application**
   ```bash
   # On Windows
   .\start.ps1
   
   # On Linux/Mac
   ./start.sh
   ```

## 🧪 Testing

### Running Tests
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run tests
cd tests
python -m pytest test_booking.py -v
```

### Test Coverage
- AI Service: Intent extraction, datetime parsing, response generation
- Booking Agent: Conversation flow, session management
- API Endpoints: Chat, booking, availability checking
- Models: Data validation and serialization

## 🚀 Deployment

### Local Development
```bash
# Backend only
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend only
cd frontend
streamlit run streamlit_app.py --server.port 8501
```

### Production Deployment

#### Option 1: Railway (Recommended)
1. Connect GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy backend and frontend as separate services

#### Option 2: Render
1. Create new web services for backend and frontend
2. Configure build and start commands
3. Set environment variables

#### Option 3: Fly.io
1. Install flyctl CLI
2. Create Dockerfile for each service
3. Deploy using `fly deploy`

### Environment Variables for Production
```env
# Required
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials/service-account-key.json
GOOGLE_CALENDAR_ID=your-calendar@gmail.com
OPENAI_API_KEY=sk-...  # or GEMINI_API_KEY

# Optional
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000
TIMEZONE=UTC
```

## 🔀 Development Workflow

### Adding New Features

1. **Backend Changes**
   ```
   backend/app/
   ├── models.py          # Add new data models
   ├── routers/           # Add new API endpoints
   ├── services/          # Add new business logic
   └── utils/             # Add utilities
   ```

2. **Frontend Changes**
   ```
   frontend/
   ├── streamlit_app.py   # Main UI components
   └── components/        # Reusable UI components (if added)
   ```

3. **Testing**
   ```
   tests/
   ├── test_booking.py    # Main test file
   ├── test_api.py        # API endpoint tests (if added)
   └── test_ui.py         # UI tests (if added)
   ```

### Code Style
- Use Black for Python formatting
- Follow FastAPI and Streamlit best practices
- Add type hints for all functions
- Document complex logic with comments

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create PR
git push origin feature/new-feature
```

## 🐛 Debugging

### Common Issues

1. **Google Calendar API Errors**
   - Check service account permissions
   - Verify calendar sharing with service account
   - Ensure credentials file is valid JSON

2. **LLM Integration Issues**
   - Verify API keys are set correctly
   - Check API quotas and limits
   - Test with fallback extraction if LLM fails

3. **Streamlit Connection Errors**
   - Ensure backend is running on correct port
   - Check CORS configuration in FastAPI
   - Verify API endpoints are accessible

### Logging
- Backend logs: Check console output or `app.log`
- Frontend logs: Check Streamlit console
- Enable debug mode with `DEBUG=True` in .env

## 📊 Monitoring and Analytics

### Health Checks
- Backend: `GET /health`
- Calendar Status: `GET /api/v1/booking/calendar-status`

### Session Management
- Active Sessions: `GET /api/v1/chat/sessions`
- Session History: `GET /api/v1/chat/session/{id}/history`

## 🎨 Customization

### UI Customization
- Modify CSS in `streamlit_app.py`
- Add new quick action buttons
- Customize color scheme and layout

### AI Behavior
- Adjust prompts in `ai_service.py`
- Modify conversation flow in `booking_agent.py`
- Add new intent recognition patterns

### Calendar Integration
- Add recurring event support
- Implement meeting rooms booking
- Add email notifications

## 📚 API Documentation

### Auto-generated Docs
- FastAPI Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Manual Testing
```bash
# Test chat endpoint
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Book a meeting tomorrow at 2 PM"}'

# Test availability
curl -X POST "http://localhost:8000/api/v1/booking/check-availability" \
  -H "Content-Type: application/json" \
  -d '{"start_datetime": "2024-01-15T14:00:00", "end_datetime": "2024-01-15T15:00:00"}'
```

## 🚀 Performance Optimization

### Backend Optimization
- Use async/await for I/O operations
- Implement caching for calendar data
- Add connection pooling for external APIs

### Frontend Optimization
- Use session state efficiently
- Implement message pagination for long conversations
- Add loading states for better UX

## 🔒 Security Considerations

### API Security
- Add authentication middleware
- Implement rate limiting
- Validate all input data

### Credential Security
- Never commit API keys or credentials
- Use environment variables
- Rotate keys regularly

### Data Privacy
- Don't log sensitive information
- Implement session cleanup
- Follow GDPR guidelines if applicable

---

**Happy Coding! 🎉**

For questions or issues, create an issue in the GitHub repository or check the troubleshooting section in the README.
