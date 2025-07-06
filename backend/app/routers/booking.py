"""
Booking endpoints for calendar management
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from ..models import BookingRequest, BookingResponse, AvailabilityRequest, AvailabilityResponse
from ..services.calendar_service import GoogleCalendarService
from ..utils.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Global calendar service instance
calendar_service = GoogleCalendarService()


@router.post("/create", response_model=BookingResponse)
async def create_booking(booking: BookingRequest) -> BookingResponse:
    """
    Create a new calendar booking
    """
    try:
        logger.info(f"Creating booking: {booking.title} at {booking.start_datetime}")
        
        # First check availability
        availability = calendar_service.check_availability(
            booking.start_datetime,
            booking.end_datetime
        )
        
        if not availability.get("available", False):
            return BookingResponse(
                success=False,
                message=f"Time slot is not available: {availability.get('message', 'Unknown conflict')}",
                event_details={"conflicts": availability.get("conflicts", [])}
            )
        
        # Create the event
        event_data = {
            "title": booking.title,
            "description": booking.description,
            "start_datetime": booking.start_datetime,
            "end_datetime": booking.end_datetime,
            "location": booking.location,
            "attendee_email": booking.attendee_email
        }
        
        result = calendar_service.create_event(event_data)
        
        if result.get("success", False):
            return BookingResponse(
                success=True,
                event_id=result.get("event_id"),
                message="Booking created successfully!",
                event_details=result.get("event_details")
            )
        else:
            return BookingResponse(
                success=False,
                message=f"Failed to create booking: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"Error creating booking: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")


@router.post("/check-availability", response_model=Dict[str, Any])
async def check_availability(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check availability for a specific time slot
    """
    try:
        start_time = datetime.fromisoformat(request["start_datetime"].replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(request["end_datetime"].replace("Z", "+00:00"))
        
        logger.info(f"Checking availability from {start_time} to {end_time}")
        
        result = calendar_service.check_availability(start_time, end_time)
        
        return {
            "available": result.get("available", False),
            "message": result.get("message", ""),
            "conflicts": result.get("conflicts", []),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")


@router.get("/available-slots")
async def get_available_slots(
    start_date: str,
    end_date: str,
    duration_minutes: int = 60
) -> Dict[str, Any]:
    """
    Get available time slots within a date range
    """
    try:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
        
        logger.info(f"Getting available slots from {start_datetime} to {end_datetime}")
        
        slots = calendar_service.get_available_slots(
            start_datetime,
            end_datetime,
            duration_minutes
        )
        
        # Format slots for response
        formatted_slots = []
        for slot in slots:
            formatted_slots.append({
                "start": slot["start"].isoformat(),
                "end": slot["end"].isoformat(),
                "duration_minutes": duration_minutes
            })
        
        return {
            "available_slots": formatted_slots,
            "count": len(formatted_slots),
            "duration_minutes": duration_minutes,
            "search_range": {
                "start": start_datetime.isoformat(),
                "end": end_datetime.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting available slots: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting available slots: {str(e)}")


@router.post("/suggest-alternatives")
async def suggest_alternative_times(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest alternative times if preferred slot is not available
    """
    try:
        preferred_start = datetime.fromisoformat(request["preferred_start"].replace("Z", "+00:00"))
        duration_minutes = request.get("duration_minutes", 60)
        
        logger.info(f"Suggesting alternatives for {preferred_start}")
        
        alternatives = calendar_service.suggest_alternative_times(
            preferred_start,
            duration_minutes
        )
        
        # Format alternatives
        formatted_alternatives = []
        for alt in alternatives:
            formatted_alternatives.append({
                "start": alt["start"].isoformat(),
                "end": alt["end"].isoformat(),
                "human_readable": alt["start"].strftime("%A, %B %d at %I:%M %p")
            })
        
        return {
            "alternatives": formatted_alternatives,
            "count": len(formatted_alternatives),
            "original_request": preferred_start.isoformat(),
            "message": f"Found {len(formatted_alternatives)} alternative time slots"
        }
        
    except Exception as e:
        logger.error(f"Error suggesting alternatives: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error suggesting alternatives: {str(e)}")


@router.get("/calendar-status")
async def get_calendar_status() -> Dict[str, Any]:
    """
    Get calendar service status and configuration
    """
    try:
        settings = get_settings()
        
        # Test calendar connection
        test_result = {"connected": False, "error": None}
        if calendar_service.service:
            try:
                # Try to list calendars to test connection
                calendars = calendar_service.service.calendarList().list().execute()
                test_result["connected"] = True
                test_result["calendar_count"] = len(calendars.get('items', []))
            except Exception as e:
                test_result["error"] = str(e)
        
        return {
            "service_initialized": calendar_service.service is not None,
            "calendar_id": settings.google_calendar_id,
            "credentials_path": settings.google_calendar_credentials_path,
            "connection_test": test_result,
            "timezone": settings.timezone
        }
        
    except Exception as e:
        logger.error(f"Error getting calendar status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting calendar status: {str(e)}")


@router.get("/upcoming-events")
async def get_upcoming_events(days_ahead: int = 7) -> Dict[str, Any]:
    """
    Get upcoming events from the calendar
    """
    try:
        if not calendar_service.service:
            raise HTTPException(status_code=503, detail="Calendar service not available")
        
        # Calculate time range
        now = datetime.now()
        end_time = now + timedelta(days=days_ahead)
        
        # Get events
        events_result = calendar_service.service.events().list(
            calendarId=calendar_service.calendar_id,
            timeMin=now.isoformat(),
            timeMax=end_time.isoformat(),
            maxResults=50,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events
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
                "location": event.get('location', ''),
                "attendees": [attendee.get('email') for attendee in event.get('attendees', [])]
            })
        
        return {
            "events": formatted_events,
            "count": len(formatted_events),
            "date_range": {
                "start": now.isoformat(),
                "end": end_time.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting upcoming events: {str(e)}")
