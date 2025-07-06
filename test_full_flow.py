#!/usr/bin/env python3
"""
Test the full conversation flow
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

def test_full_flow():
    """Test the complete booking flow"""
    agent = BookingAgent()
    session_id = "test-full-flow"
    
    print("=== FULL BOOKING FLOW TEST ===\n")
    
    # Step 1: Initial booking request
    print("User: Book a meeting tomorrow at 2 PM")
    result1 = agent.process_message("Book a meeting tomorrow at 2 PM", session_id)
    print(f"Agent: {result1['response']}")
    print(f"Step: {result1['current_step']}\n")
    
    # Step 2: User confirmation
    print("User: Yes, please book it")
    result2 = agent.process_message("Yes, please book it", session_id)
    print(f"Agent: {result2['response']}")
    print(f"Step: {result2['current_step']}\n")
    
    print("=== ALTERNATIVE FLOW TEST ===\n")
    
    # Test alternative suggestions flow
    session_id2 = "test-alternatives"
    print("User: Book a meeting today at 3 PM")
    result3 = agent.process_message("Book a meeting today at 3 PM", session_id2)
    print(f"Agent: {result3['response']}")
    print(f"Step: {result3['current_step']}\n")

if __name__ == "__main__":
    test_full_flow()
