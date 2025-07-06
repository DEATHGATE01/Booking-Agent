#!/usr/bin/env python3
"""
Test to trace exactly where the flow breaks
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
from backend.app.models import AgentState, ExtractedBookingData

def trace_flow():
    """Trace the flow step by step"""
    agent = BookingAgent()
    message = "Book a meeting tomorrow at 2 PM"
    session_id = "trace-test"
    
    print("=== Tracing the booking flow ===")
    
    # Initialize session manually
    session = AgentState(
        session_id=session_id,
        current_step="greeting",
        extracted_data=ExtractedBookingData(),
        conversation_history=[],
        confirmed_booking=False
    )
    agent.sessions[session_id] = session
    
    # Step 1: Extract intent
    print("Step 1: Extracting intent...")
    intent_result = agent.ai_service.extract_booking_intent(message)
    print(f"Intent result: {intent_result}")
    
    # Step 2: Update extracted data
    print("\nStep 2: Updating extracted data...")
    extracted_data = intent_result.get("extracted_data", {})
    if extracted_data:
        for key, value in extracted_data.items():
            if value is not None and hasattr(session.extracted_data, key):
                setattr(session.extracted_data, key, value)
    print(f"Extracted data: {session.extracted_data}")
    
    # Step 3: Check conditions
    print("\nStep 3: Checking conditions...")
    print(f"Current step: {session.current_step}")
    print(f"Intent: {intent_result.get('intent')}")
    
    has_booking_data = (session.extracted_data.title and 
                      (session.extracted_data.date or session.extracted_data.time))
    print(f"Has booking data: {has_booking_data}")
    
    booking_condition = intent_result.get("intent") == "booking" or has_booking_data
    print(f"Booking condition met: {booking_condition}")
    
    if session.current_step == "greeting" and booking_condition:
        print("\nStep 4: Processing booking...")
        session.current_step = "collecting_info"
        
        missing_info = agent._get_missing_info(session.extracted_data)
        print(f"Missing info: {missing_info}")
        
        if not missing_info:
            print("Step 5: No missing info, checking availability...")
            session.current_step = "checking_availability"
            
            try:
                availability_result = agent._check_time_availability(session.extracted_data)
                print(f"Availability result: {availability_result}")
                
                if availability_result["available"]:
                    print("✅ Time is available!")
                    session.current_step = "confirming"
                    response = f"Great! I found that {session.extracted_data.date} at {session.extracted_data.time} is available. Shall I book this {session.extracted_data.title} for you?"
                else:
                    print("❌ Time not available, getting alternatives...")
                    alternatives = agent._get_alternative_suggestions(session.extracted_data)
                    print(f"Alternatives: {alternatives}")
                    
                    if alternatives:
                        alternatives_text = agent._format_alternatives(alternatives)
                        response = f"Unfortunately, {session.extracted_data.date} at {session.extracted_data.time} is not available. Here are some alternative times I found:\n\n{alternatives_text}\n\nWhich time would you prefer, or would you like to suggest a different time?"
                    else:
                        response = f"Unfortunately, {session.extracted_data.date} at {session.extracted_data.time} is not available. Could you please suggest a different date and time?"
                    session.current_step = "collecting_info"
                
                print(f"Final response: {response}")
                print(f"Final step: {session.current_step}")
                
            except Exception as e:
                print(f"❌ Error in availability check: {e}")
                import traceback
                traceback.print_exc()
        
        else:
            print("Step 5: Missing info found, asking for details...")
            response = "I'll help you book an appointment. Let me gather the details."
    else:
        print("❌ Conditions not met!")
        print(f"Current step == greeting: {session.current_step == 'greeting'}")
        print(f"Booking condition: {booking_condition}")

if __name__ == "__main__":
    trace_flow()
