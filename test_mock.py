#!/usr/bin/env python3
"""
Test just the conversation logic without calendar API
"""
import sys
import os

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up the environment
os.environ['GOOGLE_CALENDAR_CREDENTIALS_PATH'] = 'credentials/service-account-key.json'
os.environ['GOOGLE_CALENDAR_ID'] = 'imdeathgate@gmail.com'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCbZ0sh8YwnLDS9AOp-ggjyoPs9QeAvSEE'

def test_simple_flow():
    """Test conversation flow with mock calendar service"""
    from backend.app.services.booking_agent import BookingAgent
    from backend.app.models import AgentState, ExtractedBookingData
    
    agent = BookingAgent()
    
    # Mock the calendar service to avoid API issues
    def mock_check_availability(data):
        return {"available": False, "message": "Time slot is busy"}
    
    def mock_get_alternatives(data):
        from datetime import datetime, timedelta
        import pytz
        
        # Return some mock alternatives
        now = datetime.now(pytz.UTC)
        tomorrow = now + timedelta(days=1)
        
        return [
            {"start": tomorrow.replace(hour=10, minute=0), "end": tomorrow.replace(hour=11, minute=0)},
            {"start": tomorrow.replace(hour=14, minute=0), "end": tomorrow.replace(hour=15, minute=0)},
            {"start": tomorrow.replace(hour=16, minute=0), "end": tomorrow.replace(hour=17, minute=0)}
        ]
    
    # Replace the methods temporarily
    agent._check_time_availability = mock_check_availability
    agent._get_alternative_suggestions = mock_get_alternatives
    
    # Test the conversation
    message = "Book a meeting tomorrow at 2 PM"
    session_id = "test-mock"
    
    print(f"Testing: {message}")
    result = agent.process_message(message, session_id)
    
    print(f"\nResponse: {result['response']}")
    print(f"Current step: {result['current_step']}")
    print(f"Extracted data: {result['extracted_data']}")

if __name__ == "__main__":
    test_simple_flow()
