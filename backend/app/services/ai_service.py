"""
AI Service for natural language processing and LLM integration
"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

try:
    from langchain_openai import ChatOpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available. AI features will be limited.")

from ..utils.config import get_settings
from ..models import ExtractedBookingData

logger = logging.getLogger(__name__)


class AIService:
    """AI service for natural language processing"""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available. Using fallback text processing.")
            return
        
        try:
            if self.settings.openai_api_key:
                self.llm = ChatOpenAI(
                    api_key=self.settings.openai_api_key,
                    model="gpt-3.5-turbo",
                    temperature=0.1
                )
                logger.info("OpenAI ChatGPT initialized")
            elif self.settings.gemini_api_key:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.settings.gemini_api_key,
                    temperature=0.1
                )
                logger.info("Google Gemini initialized")
            else:
                logger.warning("No API keys found. Using fallback text processing.")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.llm = None
    
    def extract_booking_intent(self, user_message: str) -> Dict[str, Any]:
        """Extract booking information from user message"""
        if self.llm and LANGCHAIN_AVAILABLE:
            return self._llm_extract_intent(user_message)
        else:
            return self._fallback_extract_intent(user_message)
    
    def _llm_extract_intent(self, user_message: str) -> Dict[str, Any]:
        """Extract intent using LLM"""
        system_prompt = """
        You are an AI assistant that extracts booking information from user messages.
        Extract the following information from the user's message:
        - title: What they want to book (meeting, appointment, etc.)
        - date: What date they want (in YYYY-MM-DD format if possible)
        - time: What time they want (in HH:MM format if possible)
        - duration: How long the meeting should be (in minutes)
        - description: Any additional details
        - location: Where the meeting should be
        - attendee_email: Email of other attendees
        
        Return the information as a JSON object. If information is not provided, use null.
        
        Example:
        User: "Book a meeting with John tomorrow at 3 PM for 1 hour"
        Response: {
            "title": "Meeting with John",
            "date": "tomorrow",
            "time": "15:00",
            "duration": 60,
            "description": null,
            "location": null,
            "attendee_email": null,
            "confidence": 0.8
        }
        """
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"User message: {user_message}")
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                return {
                    "intent": "booking",
                    "extracted_data": extracted_data,
                    "confidence": extracted_data.get("confidence", 0.5)
                }
            else:
                logger.warning("No JSON found in LLM response")
                return self._fallback_extract_intent(user_message)
                
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            return self._fallback_extract_intent(user_message)
    
    def _fallback_extract_intent(self, user_message: str) -> Dict[str, Any]:
        """Fallback intent extraction using regex patterns"""
        message_lower = user_message.lower()
        
        # Check for booking intent keywords
        booking_keywords = ['book', 'schedule', 'appointment', 'meeting', 'reserve']
        has_booking_intent = any(keyword in message_lower for keyword in booking_keywords)
        
        if not has_booking_intent:
            return {
                "intent": "general",
                "extracted_data": {},
                "confidence": 0.1
            }
        
        extracted_data = {}
        
        # Extract time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)',
            r'at\s+(\d{1,2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted_data['time'] = match.group(0)
                break
        
        # Extract date patterns
        date_patterns = [
            r'tomorrow',
            r'today',
            r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(\d{1,2})/(\d{1,2})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted_data['date'] = match.group(0)
                break
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*(hour|hours|minute|minutes|min)', message_lower)
        if duration_match:
            duration_value = int(duration_match.group(1))
            duration_unit = duration_match.group(2)
            if 'hour' in duration_unit:
                extracted_data['duration'] = duration_value * 60
            else:
                extracted_data['duration'] = duration_value
        
        # Extract title/subject
        if 'meeting' in message_lower:
            extracted_data['title'] = 'Meeting'
        elif 'appointment' in message_lower:
            extracted_data['title'] = 'Appointment'
        else:
            extracted_data['title'] = 'Event'
        
        return {
            "intent": "booking",
            "extracted_data": extracted_data,
            "confidence": 0.6 if extracted_data else 0.3
        }
    
    def generate_response(self, 
                         user_message: str, 
                         context: Dict[str, Any] = None,
                         extracted_data: Dict[str, Any] = None) -> str:
        """Generate conversational response"""
        if self.llm and LANGCHAIN_AVAILABLE:
            return self._llm_generate_response(user_message, context, extracted_data)
        else:
            return self._fallback_generate_response(user_message, context, extracted_data)
    
    def _llm_generate_response(self, 
                              user_message: str, 
                              context: Dict[str, Any] = None,
                              extracted_data: Dict[str, Any] = None) -> str:
        """Generate response using LLM"""
        system_prompt = """
        You are a helpful booking assistant for TailorTalk. Your job is to help users book appointments.
        Be conversational, friendly, and helpful. Ask for clarification when needed.
        
        Guidelines:
        - Keep responses concise and natural
        - Ask for missing information politely
        - Confirm details before booking
        - Suggest alternatives if time is not available
        """
        
        context_info = ""
        if context:
            context_info = f"Context: {json.dumps(context, default=str)}\n"
        
        extracted_info = ""
        if extracted_data:
            extracted_info = f"Extracted data: {json.dumps(extracted_data, default=str)}\n"
        
        prompt = f"{context_info}{extracted_info}User message: {user_message}"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._fallback_generate_response(user_message, context, extracted_data)
    
    def _fallback_generate_response(self, 
                                   user_message: str, 
                                   context: Dict[str, Any] = None,
                                   extracted_data: Dict[str, Any] = None) -> str:
        """Fallback response generation"""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your booking assistant. I can help you schedule appointments. What would you like to book?"
        
        # Booking responses
        if extracted_data and extracted_data.get('title'):
            missing_info = []
            if not extracted_data.get('date'):
                missing_info.append('date')
            if not extracted_data.get('time'):
                missing_info.append('time')
            
            if missing_info:
                return f"I'd be happy to help you book a {extracted_data['title']}. Could you please provide the {' and '.join(missing_info)}?"
            else:
                return f"I'll help you book a {extracted_data['title']} on {extracted_data.get('date')} at {extracted_data.get('time')}. Let me check availability."
        
        # Default responses
        booking_keywords = ['book', 'schedule', 'appointment', 'meeting']
        if any(keyword in message_lower for keyword in booking_keywords):
            return "I'd be happy to help you book an appointment. Could you please tell me what date and time you prefer?"
        
        return "I'm here to help you book appointments. Could you tell me what you'd like to schedule?"
    
    def parse_natural_datetime(self, date_str: str, time_str: str = None) -> Optional[datetime]:
        """Parse natural language date and time into datetime object"""
        try:
            now = datetime.now()
            
            # Handle date
            date_lower = date_str.lower()
            if date_lower == 'today':
                target_date = now.date()
            elif date_lower == 'tomorrow':
                target_date = (now + timedelta(days=1)).date()
            elif 'next' in date_lower:
                # Handle "next monday", etc.
                weekdays = {
                    'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                    'friday': 4, 'saturday': 5, 'sunday': 6
                }
                for day_name, day_num in weekdays.items():
                    if day_name in date_lower:
                        days_ahead = day_num - now.weekday()
                        if days_ahead <= 0:  # Target day already happened this week
                            days_ahead += 7
                        target_date = (now + timedelta(days=days_ahead)).date()
                        break
                else:
                    return None
            else:
                # Try to parse as actual date
                try:
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    target_date = parsed_date
                except ValueError:
                    return None
            
            # Handle time
            if time_str:
                time_lower = time_str.lower()
                # Parse time patterns
                time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', time_lower)
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    am_pm = time_match.group(3)
                    
                    if am_pm == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm == 'am' and hour == 12:
                        hour = 0
                    
                    target_datetime = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
                    return target_datetime
            
            # Default to 9 AM if no time specified
            return datetime.combine(target_date, datetime.min.time().replace(hour=9))
            
        except Exception as e:
            logger.error(f"Error parsing datetime: {e}")
            return None
    
    def call_functions_with_llm(self, user_message: str, available_functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use LLM with function calling to process user requests"""
        if not self.llm or not LANGCHAIN_AVAILABLE:
            return {"error": "LLM not available for function calling"}
        
        try:
            # Check if this is OpenAI (supports function calling)
            if hasattr(self.llm, 'model_name') and 'gpt' in self.llm.model_name:
                return self._openai_function_calling(user_message, available_functions)
            else:
                # Fallback to manual parsing for other LLMs
                return self._manual_function_calling(user_message, available_functions)
                
        except Exception as e:
            logger.error(f"Error in function calling: {e}")
            return {"error": f"Function calling failed: {str(e)}"}
    
    def _openai_function_calling(self, user_message: str, available_functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use OpenAI's native function calling"""
        try:
            import openai
            from openai import OpenAI
            
            client = OpenAI(api_key=self.settings.openai_api_key)
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful booking assistant. Use the available functions to help users book appointments, check availability, and manage their calendar."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                functions=available_functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            if message.function_call:
                return {
                    "function_call": {
                        "name": message.function_call.name,
                        "arguments": json.loads(message.function_call.arguments)
                    },
                    "message": message.content
                }
            else:
                return {
                    "response": message.content,
                    "function_call": None
                }
                
        except Exception as e:
            logger.error(f"OpenAI function calling error: {e}")
            return {"error": f"OpenAI function calling failed: {str(e)}"}
    
    def _manual_function_calling(self, user_message: str, available_functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Manual function calling for non-OpenAI LLMs"""
        # Analyze the message to determine if a function should be called
        message_lower = user_message.lower()
        
        # Intent detection for function calling
        if any(word in message_lower for word in ['book', 'schedule', 'create', 'make appointment']):
            # Extract booking details and prepare for create_calendar_event
            intent_result = self.extract_booking_intent(user_message)
            extracted_data = intent_result.get("extracted_data", {})
            
            if extracted_data.get('date') and extracted_data.get('time'):
                # Parse the datetime
                start_dt = self.parse_natural_datetime(extracted_data['date'], extracted_data['time'])
                if start_dt:
                    end_dt = start_dt + timedelta(minutes=extracted_data.get('duration', 60))
                    
                    return {
                        "function_call": {
                            "name": "create_calendar_event",
                            "arguments": {
                                "title": extracted_data.get('title', 'Meeting'),
                                "start_datetime": start_dt.isoformat(),
                                "end_datetime": end_dt.isoformat(),
                                "description": extracted_data.get('description'),
                                "location": extracted_data.get('location')
                            }
                        }
                    }
        
        elif any(word in message_lower for word in ['available', 'free', 'check']):
            # Check availability
            intent_result = self.extract_booking_intent(user_message)
            extracted_data = intent_result.get("extracted_data", {})
            
            if extracted_data.get('date') and extracted_data.get('time'):
                start_dt = self.parse_natural_datetime(extracted_data['date'], extracted_data['time'])
                if start_dt:
                    end_dt = start_dt + timedelta(minutes=extracted_data.get('duration', 60))
                    
                    return {
                        "function_call": {
                            "name": "check_calendar_availability",
                            "arguments": {
                                "start_datetime": start_dt.isoformat(),
                                "end_datetime": end_dt.isoformat()
                            }
                        }
                    }
        
        elif any(word in message_lower for word in ['upcoming', 'events', 'schedule']):
            # Get upcoming events
            return {
                "function_call": {
                    "name": "get_upcoming_events",
                    "arguments": {"days_ahead": 7}
                }
            }
        
        # No function call needed
        return {"function_call": None}
