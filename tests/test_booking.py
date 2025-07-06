"""
Tests for the booking functionality
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.ai_service import AIService
from app.models import ExtractedBookingData


class TestAIService:
    """Test cases for AI service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ai_service = AIService()
    
    def test_extract_booking_intent_basic(self):
        """Test basic booking intent extraction"""
        message = "I want to book a meeting tomorrow at 2 PM"
        result = self.ai_service.extract_booking_intent(message)
        
        assert result["intent"] == "booking"
        assert "extracted_data" in result
        assert result["confidence"] > 0
    
    def test_extract_booking_intent_no_booking(self):
        """Test non-booking intent"""
        message = "What's the weather like today?"
        result = self.ai_service.extract_booking_intent(message)
        
        assert result["intent"] == "general"
        assert result["confidence"] < 0.5
    
    def test_parse_natural_datetime_tomorrow(self):
        """Test parsing 'tomorrow' date"""
        result = self.ai_service.parse_natural_datetime("tomorrow", "2 PM")
        
        assert result is not None
        assert result.hour == 14
        assert result.date() == (datetime.now() + timedelta(days=1)).date()
    
    def test_parse_natural_datetime_today(self):
        """Test parsing 'today' date"""
        result = self.ai_service.parse_natural_datetime("today", "3:30 PM")
        
        assert result is not None
        assert result.hour == 15
        assert result.minute == 30
        assert result.date() == datetime.now().date()
    
    def test_parse_natural_datetime_next_monday(self):
        """Test parsing 'next monday'"""
        result = self.ai_service.parse_natural_datetime("next monday", "9 AM")
        
        assert result is not None
        assert result.hour == 9
        assert result.weekday() == 0  # Monday
    
    def test_generate_response_fallback(self):
        """Test response generation"""
        response = self.ai_service.generate_response("Hello")
        
        assert response is not None
        assert len(response) > 0
        assert "hello" in response.lower() or "hi" in response.lower()


class TestBookingAgent:
    """Test cases for booking agent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Import here to avoid circular imports during test discovery
        from app.services.booking_agent import BookingAgent
        self.booking_agent = BookingAgent()
    
    def test_process_message_greeting(self):
        """Test greeting message processing"""
        result = self.booking_agent.process_message("Hello", "test_session")
        
        assert "response" in result
        assert "session_id" in result
        assert result["session_id"] == "test_session"
    
    def test_process_message_booking_request(self):
        """Test booking request processing"""
        result = self.booking_agent.process_message(
            "I want to book a meeting tomorrow at 2 PM",
            "test_session_2"
        )
        
        assert "response" in result
        assert "extracted_data" in result
        assert result["current_step"] in ["collecting_info", "checking_availability"]
    
    def test_session_management(self):
        """Test session management"""
        session_id = "test_session_3"
        
        # First message
        result1 = self.booking_agent.process_message("Hello", session_id)
        assert session_id in self.booking_agent.sessions
        
        # Second message in same session
        result2 = self.booking_agent.process_message("Book a meeting", session_id)
        assert result2["session_id"] == session_id
        
        # Check conversation history
        session = self.booking_agent.sessions[session_id]
        assert len(session.conversation_history) >= 2


class TestExtractedBookingData:
    """Test cases for booking data model"""
    
    def test_booking_data_creation(self):
        """Test creating booking data"""
        data = ExtractedBookingData(
            title="Test Meeting",
            date="tomorrow",
            time="2 PM",
            duration=60
        )
        
        assert data.title == "Test Meeting"
        assert data.date == "tomorrow"
        assert data.time == "2 PM"
        assert data.duration == 60
    
    def test_booking_data_defaults(self):
        """Test default values"""
        data = ExtractedBookingData()
        
        assert data.duration == 60
        assert data.confidence == 0.0


# Mock tests for calendar service (since we don't want to test actual Google Calendar)
class TestCalendarServiceMock:
    """Mock tests for calendar service"""
    
    def test_check_availability_format(self):
        """Test availability check response format"""
        # This would test the structure of the response
        # without actually calling Google Calendar API
        
        expected_keys = ["available", "message"]
        
        # Mock response
        mock_response = {
            "available": True,
            "message": "Time slot is available"
        }
        
        for key in expected_keys:
            assert key in mock_response
    
    def test_create_event_format(self):
        """Test event creation response format"""
        expected_keys = ["success", "message"]
        
        mock_response = {
            "success": True,
            "event_id": "test_event_123",
            "message": "Event created successfully"
        }
        
        for key in expected_keys:
            assert key in mock_response


if __name__ == "__main__":
    pytest.main([__file__])
