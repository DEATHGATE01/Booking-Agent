"""
Booking Agent using LangGraph for conversational workflow management
"""
import json
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
        
        if self.graph and LANGGRAPH_AVAILABLE:
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
        
        # Update session data
        if extracted_data:
            for key, value in extracted_data.items():
                if value is not None and hasattr(session.extracted_data, key):
                    setattr(session.extracted_data, key, value)
        
        # Determine conversation flow
        if session.current_step == "greeting":
            if intent_result.get("intent") == "booking":
                session.current_step = "collecting_info"
                response = "I'll help you book an appointment. Let me gather the details."
            else:
                response = "Hello! I'm your booking assistant. I can help you schedule appointments. What would you like to book?"
        
        elif session.current_step == "collecting_info":
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
                    response = f"Unfortunately, {session.extracted_data.date} at {session.extracted_data.time} is not available. {availability_result.get('message', '')} Would you like to try a different time?"
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
        
        else:
            response = self.ai_service.generate_response(message, {"step": session.current_step}, extracted_data)
        
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
