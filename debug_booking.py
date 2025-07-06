#!/usr/bin/env python3
"""
Simple test to debug the booking agent flow
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

def test_booking_flow():
    """Test the booking agent flow step by step"""
    agent = BookingAgent()
    
    # Test message
    message = "Book a meeting tomorrow at 2 PM"
    session_id = "test-debug"
    
    print(f"Testing message: '{message}'")
    print(f"Session ID: {session_id}")
    
    result = agent.process_message(message, session_id)
    
    print(f"\nResult:")
    print(f"Response: {result['response']}")
    print(f"Current step: {result['current_step']}")
    print(f"Extracted data: {result['extracted_data']}")
    
    # Check the session state
    session = agent.sessions[session_id]
    print(f"\nSession state:")
    print(f"Current step: {session.current_step}")
    print(f"Extracted data: {session.extracted_data}")

if __name__ == "__main__":
    test_booking_flow()
