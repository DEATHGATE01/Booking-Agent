#!/usr/bin/env python3
"""
Minimal test to debug the exact issue
"""
import sys
import os

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set up the environment
os.environ['GOOGLE_CALENDAR_CREDENTIALS_PATH'] = 'credentials/service-account-key.json'
os.environ['GOOGLE_CALENDAR_ID'] = 'imdeathgate@gmail.com'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCbZ0sh8YwnLDS9AOp-ggjyoPs9QeAvSEE'

from backend.app.services.booking_agent import BookingAgent
from backend.app.services.ai_service import AIService

def debug_flow():
    """Debug the exact flow issue"""
    # Test AI service directly
    ai_service = AIService()
    message = "Book a meeting tomorrow at 2 PM"
    
    print("=== AI Service Test ===")
    intent_result = ai_service.extract_booking_intent(message)
    print(f"Intent result: {intent_result}")
    
    print("\n=== Booking Agent Test ===")
    agent = BookingAgent()
    session_id = "debug-simple"
    
    # Manually check the conditions
    session = agent.sessions.get(session_id)
    if not session:
        from backend.app.models import AgentState, ExtractedBookingData
        session = AgentState(
            session_id=session_id,
            current_step="greeting",
            extracted_data=ExtractedBookingData(),
            conversation_history=[],
            confirmed_booking=False
        )
        agent.sessions[session_id] = session
    
    print(f"Initial current_step: {session.current_step}")
    
    # Update extracted data
    extracted_data = intent_result.get("extracted_data", {})
    if extracted_data:
        for key, value in extracted_data.items():
            if value is not None and hasattr(session.extracted_data, key):
                setattr(session.extracted_data, key, value)
    
    print(f"After data extraction: {session.extracted_data}")
    
    # Check the conditions manually
    print(f"Intent: {intent_result.get('intent')}")
    print(f"Current step is greeting: {session.current_step == 'greeting'}")
    print(f"Intent is booking: {intent_result.get('intent') == 'booking'}")
    
    has_booking_data = (session.extracted_data.title and 
                      (session.extracted_data.date or session.extracted_data.time))
    print(f"Has booking data: {has_booking_data}")
    print(f"Title: {session.extracted_data.title}")
    print(f"Date: {session.extracted_data.date}")
    print(f"Time: {session.extracted_data.time}")
    
    # Check missing info
    missing_info = agent._get_missing_info(session.extracted_data)
    print(f"Missing info: {missing_info}")

if __name__ == "__main__":
    debug_flow()
