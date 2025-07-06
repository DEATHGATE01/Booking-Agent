"""
Booking Agent using LangGraph for conversational workflow management
"""
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    from typing_extensions import TypedDict, Annotated
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available. Using simplified conversation flow.")

from ..models import AgentState, ExtractedBookingData
from ..services.ai_service import AIService
from ..services.calendar_service import GoogleCalendarService

logger = logging.getLogger(__name__)


class BookingAgent:
    """Conversational booking agent using LangGraph"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.calendar_service = GoogleCalendarService()
        self.sessions: Dict[str, AgentState] = {}
        
        if LANGGRAPH_AVAILABLE:
            self.graph = self._build_graph()
        else:
            self.graph = None
            logger.warning("Using simplified conversation flow without LangGraph")
    
    def _build_graph(self):
        """Build the conversation flow graph"""
        # Define the conversation state
        class ConversationState(TypedDict):
            messages: Annotated[List[dict], add_messages]
            session_id: str
            current_step: str
            extracted_data: dict
            confirmed: bool
        
        # Create the graph
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("greeting", self._greeting_node)
        workflow.add_node("extract_info", self._extract_info_node)
        workflow.add_node("check_availability", self._check_availability_node)
        workflow.add_node("confirm_booking", self._confirm_booking_node)
        workflow.add_node("create_booking", self._create_booking_node)
        
        # Define the flow
        workflow.set_entry_point("greeting")
        
        workflow.add_edge("greeting", "extract_info")
        workflow.add_conditional_edges(
            "extract_info",
            self._route_after_extraction,
            {
                "need_more_info": "extract_info",
                "check_availability": "check_availability",
            }
        )
        workflow.add_conditional_edges(
            "check_availability",
            self._route_after_availability,
            {
                "confirm": "confirm_booking",
                "suggest_alternatives": "extract_info",
                "unavailable": "extract_info"
            }
        )
        workflow.add_conditional_edges(
            "confirm_booking",
            self._route_after_confirmation,
            {
                "create": "create_booking",
                "modify": "extract_info",
                "cancel": END
            }
        )
        workflow.add_edge("create_booking", END)
        
        return workflow.compile()
    
    def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Process a user message and return response"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize session if needed
        if session_id not in self.sessions:
            self.sessions[session_id] = AgentState(
                session_id=session_id,
                current_step="greeting",
                extracted_data=ExtractedBookingData(),
                conversation_history=[],
                confirmed_booking=False
            )
        
        session = self.sessions[session_id]
        
        # Add message to history
        session.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if self.graph and LANGGRAPH_AVAILABLE and False:  # Temporarily disable LangGraph
            return self._process_with_graph(message, session)
        else:
            return self._process_simple(message, session)
    
    def _process_with_graph(self, message: str, session: AgentState) -> Dict[str, Any]:
        """Process message using LangGraph"""
        try:
            state = {
                "messages": [{"role": "user", "content": message}],
                "session_id": session.session_id,
                "current_step": session.current_step,
                "extracted_data": session.extracted_data.dict(),
                "confirmed": session.confirmed_booking
            }
            
            result = self.graph.invoke(state)
            
            # Update session
            session.current_step = result.get("current_step", session.current_step)
            session.confirmed_booking = result.get("confirmed", session.confirmed_booking)
            
            response_message = result["messages"][-1]["content"]
            session.last_response = response_message
            
            # Add response to history
            session.conversation_history.append({
                "role": "assistant",
                "content": response_message,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "response": response_message,
                "session_id": session.session_id,
                "current_step": session.current_step,
                "extracted_data": result.get("extracted_data", {}),
                "next_action": self._get_next_action(session.current_step)
            }
            
        except Exception as e:
            logger.error(f"Error processing with graph: {e}")
            return self._process_simple(message, session)
    
    def _process_simple(self, message: str, session: AgentState) -> Dict[str, Any]:
        """Simple conversation flow without LangGraph"""
        
        # Extract intent and information
        intent_result = self.ai_service.extract_booking_intent(message)
        extracted_data = intent_result.get("extracted_data", {})
        
        logger.info(f"Intent result: {intent_result}")
        logger.info(f"Current step: {session.current_step}")
        
        # Update session data
        if extracted_data:
            for key, value in extracted_data.items():
                if value is not None and hasattr(session.extracted_data, key):
                    setattr(session.extracted_data, key, value)
        
        # Determine conversation flow
        response = None  # Initialize response variable
        
        logger.info(f"Processing step: {session.current_step}")
        logger.info(f"Intent detected: {intent_result.get('intent')}")
        
        if session.current_step == "greeting":
            logger.info("In greeting block")
            # Check if we have booking data regardless of intent classification
            has_booking_data = (session.extracted_data.title and 
                              (session.extracted_data.date or session.extracted_data.time))
            
            if intent_result.get("intent") == "booking" or has_booking_data:
                logger.info("Booking intent detected, switching to collecting_info")
                session.current_step = "collecting_info"
                # Check if we have enough info to proceed immediately
                missing_info = self._get_missing_info(session.extracted_data)
                logger.info(f"Missing info: {missing_info}")
                if not missing_info:
                    logger.info("No missing info, checking availability")
                    # We have all the info, check availability immediately
                    session.current_step = "checking_availability"
                    availability_result = self._check_time_availability(session.extracted_data)
                    
                    if availability_result["available"]:
                        session.current_step = "confirming"
                        response = f"Great! I found that {session.extracted_data.date} at {session.extracted_data.time} is available. Shall I book this {session.extracted_data.title} for you?"
                    else:
                        # Get alternative suggestions
                        alternatives = self._get_alternative_suggestions(session.extracted_data)
                        if alternatives:
                            alternatives_text = self._format_alternatives(alternatives)
                            response = f"Unfortunately, {session.extracted_data.date} at {session.extracted_data.time} is not available. Here are some alternative times I found:\n\n{alternatives_text}\n\nWhich time would you prefer, or would you like to suggest a different time?"
                        else:
                            response = f"Unfortunately, {session.extracted_data.date} at {session.extracted_data.time} is not available. Could you please suggest a different date and time?"
                        session.current_step = "collecting_info"  # Go back to collect new time
                else:
                    logger.info("Missing info found, asking for more details")
                    response = "I'll help you book an appointment. Let me gather the details."
            else:
                logger.info("No booking intent, showing greeting")
                response = "Hello! I'm your booking assistant. I can help you schedule appointments. What would you like to book?"
        
        elif session.current_step == "collecting_info":
            # Check if user is selecting from suggested alternatives
            if self._is_alternative_selection(message):
                alternative_data = self._parse_alternative_selection(message, session)
                if alternative_data:
                    session.extracted_data.date = alternative_data["date"]
                    session.extracted_data.time = alternative_data["time"]
                    
                    # Recheck availability for the selected time
                    session.current_step = "checking_availability"
                    availability_result = self._check_time_availability(session.extracted_data)
                    
                    if availability_result["available"]:
                        session.current_step = "confirming"
                        response = f"Perfect! I can book your {session.extracted_data.title} on {session.extracted_data.date} at {session.extracted_data.time}. Shall I confirm this booking?"
                    else:
                        response = "I'm sorry, that time slot is no longer available. Let me find other options for you."
                        alternatives = self._get_alternative_suggestions(session.extracted_data)
                        if alternatives:
                            alternatives_text = self._format_alternatives(alternatives)
                            response += f"\n\nHere are some other available times:\n\n{alternatives_text}\n\nWhich would you prefer?"
                        session.current_step = "collecting_info"
                else:
                    response = "I didn't understand which time you selected. Could you please specify the date and time you'd like?"
            else:
                missing_info = self._get_missing_info(session.extracted_data)
                
                if missing_info:
                    response = f"I need a bit more information. Could you please provide: {', '.join(missing_info)}?"
                else:
                    # Check availability
                    session.current_step = "checking_availability"
                    availability_result = self._check_time_availability(session.extracted_data)
                    
                    if availability_result["available"]:
                        session.current_step = "confirming"
                        response = f"Great! I found that {session.extracted_data.date} at {session.extracted_data.time} is available. Shall I book this {session.extracted_data.title} for you?"
                    else:
                        # Get alternative suggestions
                        alternatives = self._get_alternative_suggestions(session.extracted_data)
                        if alternatives:
                            alternatives_text = self._format_alternatives(alternatives)
                            response = f"Unfortunately, {session.extracted_data.date} at {session.extracted_data.time} is not available. Here are some alternative times I found:\n\n{alternatives_text}\n\nWhich time would you prefer, or would you like to suggest a different time?"
                        else:
                            response = f"Unfortunately, {session.extracted_data.date} at {session.extracted_data.time} is not available. Could you please suggest a different date and time?"
                        session.current_step = "collecting_info"  # Go back to collect new time
        
        elif session.current_step == "confirming":
            if any(word in message.lower() for word in ['yes', 'confirm', 'book', 'ok']):
                booking_result = self._create_calendar_event(session.extracted_data)
                if booking_result["success"]:
                    session.current_step = "completed"
                    session.confirmed_booking = True
                    response = f"Perfect! I've booked your {session.extracted_data.title} for {session.extracted_data.date} at {session.extracted_data.time}. You should receive a calendar invitation shortly."
                else:
                    response = f"I'm sorry, there was an issue creating your booking: {booking_result.get('error', 'Unknown error')}. Would you like to try again?"
                    session.current_step = "collecting_info"
            else:
                response = "No problem! Would you like to choose a different time or make changes to your booking?"
                session.current_step = "collecting_info"
        
        # Default fallback for unhandled messages
        if response is None:
            response = "I'm here to help you book appointments. Could you tell me what you'd like to schedule?"
            session.current_step = "greeting"
        
        # Add response to history
        session.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        session.last_response = response
        
        return {
            "response": response,
            "session_id": session.session_id,
            "current_step": session.current_step,
            "extracted_data": session.extracted_data.dict(),
            "next_action": self._get_next_action(session.current_step)
        }
    
    def _get_alternative_suggestions(self, data: ExtractedBookingData) -> List[Dict[str, Any]]:
        """Get alternative time suggestions when requested time is not available"""
        try:
            # Parse the original requested time
            start_datetime = self.ai_service.parse_natural_datetime(data.date, data.time)
            if not start_datetime:
                return []
            
            duration = data.duration or 60
            
            # Get suggestions from calendar service
            suggestions = self.calendar_service.suggest_alternative_times(
                preferred_start=start_datetime,
                duration_minutes=duration,
                suggestions_count=3
            )
            
            # If calendar service fails, provide fallback suggestions
            if not suggestions:
                logger.info("Calendar service failed, providing fallback suggestions")
                return self._get_fallback_suggestions(start_datetime, duration)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting alternative suggestions: {e}")
            # Provide fallback suggestions when calendar service fails
            try:
                start_datetime = self.ai_service.parse_natural_datetime(data.date, data.time)
                if start_datetime:
                    return self._get_fallback_suggestions(start_datetime, data.duration or 60)
            except:
                pass
            return []
    
    def _get_fallback_suggestions(self, requested_time: datetime, duration: int) -> List[Dict[str, Any]]:
        """Provide fallback time suggestions when calendar service is unavailable"""
        suggestions = []
        
        # Suggest same day at different times
        same_day_times = [9, 11, 14, 16]  # 9 AM, 11 AM, 2 PM, 4 PM
        requested_hour = requested_time.hour
        
        for hour in same_day_times:
            if hour != requested_hour:
                suggestion_time = requested_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                suggestions.append({
                    "start": suggestion_time,
                    "end": suggestion_time + timedelta(minutes=duration)
                })
                if len(suggestions) >= 2:
                    break
        
        # Add next day suggestion if we need more
        if len(suggestions) < 3:
            next_day = requested_time + timedelta(days=1)
            next_day_suggestion = next_day.replace(hour=10, minute=0, second=0, microsecond=0)
            suggestions.append({
                "start": next_day_suggestion,
                "end": next_day_suggestion + timedelta(minutes=duration)
            })
        
        return suggestions[:3]
    
    def _is_alternative_selection(self, message: str) -> bool:
        """Check if the message is selecting from provided alternatives"""
        message_lower = message.lower().strip()
        
        # Check for numbered selection (1, 2, 3, etc.)
        if re.match(r'^[123]\.?\s*$', message_lower):
            return True
        
        # Check for selection keywords
        selection_patterns = [
            r'i?\'?ll take (the )?(first|second|third|1st|2nd|3rd)',
            r'option [123]',
            r'choice [123]',
            r'number [123]',
            r'^(first|second|third|1st|2nd|3rd)$'
        ]
        
        for pattern in selection_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _parse_alternative_selection(self, message: str, session: AgentState) -> Optional[Dict[str, str]]:
        """Parse which alternative the user selected"""
        message_lower = message.lower().strip()
        
        # Get the last alternatives that were shown (we'd need to store these in session)
        # For now, let's regenerate them
        try:
            original_data = session.extracted_data
            start_datetime = self.ai_service.parse_natural_datetime(original_data.date, original_data.time)
            if not start_datetime:
                return None
            
            duration = original_data.duration or 60
            alternatives = self.calendar_service.suggest_alternative_times(
                preferred_start=start_datetime,
                duration_minutes=duration,
                suggestions_count=3
            )
            
            if not alternatives:
                return None
            
            # Parse selection number
            selection_num = None
            
            # Check for direct number
            if re.match(r'^[123]\.?\s*$', message_lower):
                selection_num = int(message_lower.replace('.', '').strip())
            
            # Check for ordinal words
            elif 'first' in message_lower or '1st' in message_lower:
                selection_num = 1
            elif 'second' in message_lower or '2nd' in message_lower:
                selection_num = 2
            elif 'third' in message_lower or '3rd' in message_lower:
                selection_num = 3
            
            # Check for "option/choice/number X"
            else:
                number_match = re.search(r'(option|choice|number)\s+([123])', message_lower)
                if number_match:
                    selection_num = int(number_match.group(2))
            
            if selection_num and 1 <= selection_num <= len(alternatives):
                selected_slot = alternatives[selection_num - 1]
                selected_datetime = selected_slot["start"]
                
                return {
                    "date": selected_datetime.strftime("%Y-%m-%d"),
                    "time": selected_datetime.strftime("%H:%M")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing alternative selection: {e}")
            return None

    def _format_alternatives(self, alternatives: List[Dict[str, Any]]) -> str:
        """Format alternative time suggestions into readable text"""
        if not alternatives:
            return "No alternative times found."
        
        formatted_alternatives = []
        for i, slot in enumerate(alternatives, 1):
            start_time = slot["start"]
            # Format as "Monday, Jan 15 at 2:00 PM"
            formatted_time = start_time.strftime("%A, %b %d at %I:%M %p")
            formatted_alternatives.append(f"{i}. {formatted_time}")
        
        return "\n".join(formatted_alternatives)

    def _get_missing_info(self, data: ExtractedBookingData) -> List[str]:
        """Get list of missing required information"""
        missing = []
        
        if not data.title:
            missing.append("what type of appointment")
        if not data.date:
            missing.append("the date")
        if not data.time:
            missing.append("the time")
        
        return missing
    
    def _check_time_availability(self, data: ExtractedBookingData) -> Dict[str, Any]:
        """Check if the requested time is available"""
        try:
            # Parse the natural language date/time
            start_datetime = self.ai_service.parse_natural_datetime(data.date, data.time)
            if not start_datetime:
                return {"available": False, "message": "Could not parse the date/time"}
            
            # Calculate end time
            duration = data.duration or 60
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Check calendar availability
            return self.calendar_service.check_availability(start_datetime, end_datetime)
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {"available": False, "error": str(e)}
    
    def _create_calendar_event(self, data: ExtractedBookingData) -> Dict[str, Any]:
        """Create the calendar event"""
        try:
            # Parse datetime
            start_datetime = self.ai_service.parse_natural_datetime(data.date, data.time)
            if not start_datetime:
                return {"success": False, "error": "Could not parse date/time"}
            
            duration = data.duration or 60
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            event_data = {
                "title": data.title or "Appointment",
                "description": data.description or "Booked via TailorTalk Assistant",
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "location": data.location,
                "attendee_email": data.attendee_email
            }
            
            return self.calendar_service.create_event(event_data)
            
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_next_action(self, current_step: str) -> str:
        """Get suggested next action based on current step"""
        actions = {
            "greeting": "Tell me what you'd like to book",
            "collecting_info": "Provide the missing information",
            "checking_availability": "Waiting for availability check",
            "confirming": "Confirm or modify the booking",
            "completed": "Booking completed"
        }
        return actions.get(current_step, "Continue the conversation")
    
    # LangGraph node functions (only used if LangGraph is available)
    def _greeting_node(self, state):
        """Greeting node for LangGraph"""
        return {"current_step": "extract_info"}
    
    def _extract_info_node(self, state):
        """Extract information node"""
        return {"current_step": "check_availability"}
    
    def _check_availability_node(self, state):
        """Check availability node"""
        return {"current_step": "confirm_booking"}
    
    def _confirm_booking_node(self, state):
        """Confirm booking node"""
        return {"current_step": "create_booking"}
    
    def _create_booking_node(self, state):
        """Create booking node"""
        return {"confirmed": True}
    
    def _route_after_extraction(self, state):
        """Route after information extraction"""
        return "check_availability"
    
    def _route_after_availability(self, state):
        """Route after availability check"""
        return "confirm"
    
    def _route_after_confirmation(self, state):
        """Route after confirmation"""
        return "create"
