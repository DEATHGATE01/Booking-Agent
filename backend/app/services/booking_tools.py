"""
Function calling tools for the booking agent
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class BookingTools:
    """Collection of tools/functions for the booking agent to call"""
    
    def __init__(self, calendar_service, ai_service):
        self.calendar_service = calendar_service
        self.ai_service = ai_service
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get OpenAI-compatible function definitions for tool calling"""
        return [
            {
                "name": "check_calendar_availability",
                "description": "Check if a specific time slot is available on the calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_datetime": {
                            "type": "string",
                            "description": "Start datetime in ISO format (e.g., '2024-01-15T14:00:00')"
                        },
                        "end_datetime": {
                            "type": "string",
                            "description": "End datetime in ISO format (e.g., '2024-01-15T15:00:00')"
                        }
                    },
                    "required": ["start_datetime", "end_datetime"]
                }
            },
            {
                "name": "create_calendar_event",
                "description": "Create a new event on the calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Event title/subject"
                        },
                        "start_datetime": {
                            "type": "string",
                            "description": "Start datetime in ISO format"
                        },
                        "end_datetime": {
                            "type": "string",
                            "description": "End datetime in ISO format"
                        },
                        "description": {
                            "type": "string",
                            "description": "Event description (optional)"
                        },
                        "location": {
                            "type": "string",
                            "description": "Event location (optional)"
                        },
                        "attendee_email": {
                            "type": "string",
                            "description": "Attendee email address (optional)"
                        }
                    },
                    "required": ["title", "start_datetime", "end_datetime"]
                }
            },
            {
                "name": "suggest_alternative_times",
                "description": "Suggest alternative time slots if the requested time is not available",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "preferred_start": {
                            "type": "string",
                            "description": "Preferred start datetime in ISO format"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Duration of the meeting in minutes",
                            "default": 60
                        },
                        "suggestions_count": {
                            "type": "integer",
                            "description": "Number of alternative suggestions to provide",
                            "default": 3
                        }
                    },
                    "required": ["preferred_start"]
                }
            },
            {
                "name": "parse_natural_datetime",
                "description": "Parse natural language date/time into structured datetime",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date_text": {
                            "type": "string",
                            "description": "Natural language date (e.g., 'tomorrow', 'next Monday')"
                        },
                        "time_text": {
                            "type": "string",
                            "description": "Natural language time (e.g., '2 PM', '14:30')"
                        }
                    },
                    "required": ["date_text"]
                }
            },
            {
                "name": "get_upcoming_events",
                "description": "Get upcoming events from the calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days ahead to look for events",
                            "default": 7
                        }
                    }
                }
            }
        ]
    
    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call and return the result"""
        try:
            if function_name == "check_calendar_availability":
                return self._check_calendar_availability(**arguments)
            elif function_name == "create_calendar_event":
                return self._create_calendar_event(**arguments)
            elif function_name == "suggest_alternative_times":
                return self._suggest_alternative_times(**arguments)
            elif function_name == "parse_natural_datetime":
                return self._parse_natural_datetime(**arguments)
            elif function_name == "get_upcoming_events":
                return self._get_upcoming_events(**arguments)
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            logger.error(f"Error executing function {function_name}: {e}")
            return {"error": f"Function execution failed: {str(e)}"}
    
    def _check_calendar_availability(self, start_datetime: str, end_datetime: str) -> Dict[str, Any]:
        """Check calendar availability"""
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            result = self.calendar_service.check_availability(start_dt, end_dt)
            return {
                "available": result.get("available", False),
                "message": result.get("message", ""),
                "conflicts": result.get("conflicts", []),
                "start_time": start_datetime,
                "end_time": end_datetime
            }
        except Exception as e:
            return {"error": f"Failed to check availability: {str(e)}"}
    
    def _create_calendar_event(self, title: str, start_datetime: str, end_datetime: str, 
                              description: str = None, location: str = None, 
                              attendee_email: str = None) -> Dict[str, Any]:
        """Create a calendar event"""
        try:
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
            
            event_data = {
                "title": title,
                "description": description or "Booked via TailorTalk AI Assistant",
                "start_datetime": start_dt,
                "end_datetime": end_dt,
                "location": location,
                "attendee_email": attendee_email
            }
            
            result = self.calendar_service.create_event(event_data)
            return {
                "success": result.get("success", False),
                "event_id": result.get("event_id"),
                "message": result.get("message", ""),
                "event_details": result.get("event_details", {}),
                "event_link": result.get("event_link")
            }
        except Exception as e:
            return {"error": f"Failed to create event: {str(e)}"}
    
    def _suggest_alternative_times(self, preferred_start: str, duration_minutes: int = 60, 
                                  suggestions_count: int = 3) -> Dict[str, Any]:
        """Suggest alternative time slots"""
        try:
            preferred_dt = datetime.fromisoformat(preferred_start.replace('Z', '+00:00'))
            
            alternatives = self.calendar_service.suggest_alternative_times(
                preferred_dt, duration_minutes, suggestions_count
            )
            
            formatted_alternatives = []
            for alt in alternatives:
                formatted_alternatives.append({
                    "start": alt["start"].isoformat(),
                    "end": alt["end"].isoformat(),
                    "human_readable": alt["start"].strftime("%A, %B %d at %I:%M %p"),
                    "duration_minutes": duration_minutes
                })
            
            return {
                "alternatives": formatted_alternatives,
                "count": len(formatted_alternatives),
                "original_request": preferred_start,
                "message": f"Found {len(formatted_alternatives)} alternative time slots"
            }
        except Exception as e:
            return {"error": f"Failed to suggest alternatives: {str(e)}"}
    
    def _parse_natural_datetime(self, date_text: str, time_text: str = None) -> Dict[str, Any]:
        """Parse natural language datetime"""
        try:
            parsed_dt = self.ai_service.parse_natural_datetime(date_text, time_text)
            
            if parsed_dt:
                return {
                    "success": True,
                    "datetime": parsed_dt.isoformat(),
                    "human_readable": parsed_dt.strftime("%A, %B %d, %Y at %I:%M %p"),
                    "date": parsed_dt.date().isoformat(),
                    "time": parsed_dt.time().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Could not parse the date/time"
                }
        except Exception as e:
            return {"error": f"Failed to parse datetime: {str(e)}"}
    
    def _get_upcoming_events(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Get upcoming events"""
        try:
            if not self.calendar_service.service:
                return {"error": "Calendar service not available"}
            
            now = datetime.now()
            end_time = now + timedelta(days=days_ahead)
            
            events_result = self.calendar_service.service.events().list(
                calendarId=self.calendar_service.calendar_id,
                timeMin=now.isoformat(),
                timeMax=end_time.isoformat(),
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    "id": event.get('id'),
                    "summary": event.get('summary', 'No title'),
                    "start": start,
                    "end": end,
                    "description": event.get('description', ''),
                    "location": event.get('location', '')
                })
            
            return {
                "events": formatted_events,
                "count": len(formatted_events),
                "date_range": {
                    "start": now.isoformat(),
                    "end": end_time.isoformat()
                }
            }
        except Exception as e:
            return {"error": f"Failed to get events: {str(e)}"}


# LangChain-compatible tools
def create_langchain_tools(calendar_service, ai_service):
    """Create LangChain-compatible tools"""
    booking_tools = BookingTools(calendar_service, ai_service)
    
    try:
        from langchain.tools import Tool
        
        tools = [
            Tool(
                name="check_calendar_availability",
                description="Check if a specific time slot is available on the calendar. Input should be JSON with start_datetime and end_datetime in ISO format.",
                func=lambda args: booking_tools.execute_function("check_calendar_availability", json.loads(args))
            ),
            Tool(
                name="create_calendar_event",
                description="Create a new event on the calendar. Input should be JSON with title, start_datetime, end_datetime, and optional description, location, attendee_email.",
                func=lambda args: booking_tools.execute_function("create_calendar_event", json.loads(args))
            ),
            Tool(
                name="suggest_alternative_times",
                description="Suggest alternative time slots if requested time is not available. Input should be JSON with preferred_start and optional duration_minutes.",
                func=lambda args: booking_tools.execute_function("suggest_alternative_times", json.loads(args))
            ),
            Tool(
                name="parse_natural_datetime",
                description="Parse natural language date/time into structured datetime. Input should be JSON with date_text and optional time_text.",
                func=lambda args: booking_tools.execute_function("parse_natural_datetime", json.loads(args))
            ),
            Tool(
                name="get_upcoming_events",
                description="Get upcoming events from the calendar. Input should be JSON with optional days_ahead.",
                func=lambda args: booking_tools.execute_function("get_upcoming_events", json.loads(args))
            )
        ]
        
        return tools
        
    except ImportError:
        logger.warning("LangChain not available. Tools created without LangChain integration.")
        return []
