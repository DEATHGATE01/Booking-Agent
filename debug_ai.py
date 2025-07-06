#!/usr/bin/env python3
"""
Debug script to test AI service intent extraction
"""
import sys
import os

# Add the backend to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.ai_service import AIService

def test_intent_extraction():
    """Test intent extraction with various messages"""
    ai_service = AIService()
    
    test_messages = [
        "hello",
        "hi",
        "book meeting",
        "Book a meeting tomorrow at 2 PM",
        "schedule appointment",
        "I want to book something"
    ]
    
    for message in test_messages:
        print(f"\nMessage: '{message}'")
        result = ai_service.extract_booking_intent(message)
        print(f"Intent: {result.get('intent')}")
        print(f"Extracted data: {result.get('extracted_data')}")
        print(f"Confidence: {result.get('confidence')}")
        print("-" * 50)

if __name__ == "__main__":
    test_intent_extraction()
