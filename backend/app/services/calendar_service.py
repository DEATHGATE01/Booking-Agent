"""
Google Calendar service integration
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

from ..utils.config import get_settings

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Google Calendar API service"""
    
    def __init__(self):
        self.settings = get_settings()
        self.service = None
        self.calendar_id = self.settings.google_calendar_id
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service"""
        try:
            # Load service account credentials
            credentials_path = self.settings.google_calendar_credentials_path
            if not os.path.exists(credentials_path):
                logger.error(f"Credentials file not found: {credentials_path}")
                return
            
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Google Calendar service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            self.service = None
    
    def check_availability(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Check calendar availability for a given time range"""
        if not self.service:
            return {"available": False, "error": "Calendar service not initialized"}
        
        try:
            # Convert to RFC3339 format
            start_time_rfc = start_time.isoformat()
            end_time_rfc = end_time.isoformat()
            
            # Query for events in the time range
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_time_rfc,
                timeMax=end_time_rfc,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if events:
                # Time slot is busy
                busy_events = []
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))
                    summary = event.get('summary', 'Busy')
                    
                    busy_events.append({
                        'start': start,
                        'end': end,
                        'summary': summary
                    })
                
                return {
                    "available": False,
                    "conflicts": busy_events,
                    "message": f"Time slot is busy with {len(events)} event(s)"
                }
            else:
                return {
                    "available": True,
                    "message": "Time slot is available"
                }
                
        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            return {"available": False, "error": f"Calendar API error: {error}"}
        except Exception as e:
            logger.error(f"Unexpected error checking availability: {e}")
            return {"available": False, "error": f"Unexpected error: {e}"}
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        if not self.service:
            return {"success": False, "error": "Calendar service not initialized"}
        
        try:
            # Prepare event object
            event = {
                'summary': event_data.get('title', 'New Appointment'),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data['start_datetime'].isoformat(),
                    'timeZone': self.settings.timezone,
                },
                'end': {
                    'dateTime': event_data['end_datetime'].isoformat(),
                    'timeZone': self.settings.timezone,
                },
            }
            
            # Add location if provided
            if event_data.get('location'):
                event['location'] = event_data['location']
            
            # Add attendees if provided
            if event_data.get('attendee_email'):
                event['attendees'] = [
                    {'email': event_data['attendee_email']}
                ]
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            logger.info(f"Event created successfully: {created_event['id']}")
            
            return {
                "success": True,
                "event_id": created_event['id'],
                "event_link": created_event.get('htmlLink'),
                "message": "Event created successfully",
                "event_details": {
                    "id": created_event['id'],
                    "summary": created_event.get('summary'),
                    "start": created_event['start'],
                    "end": created_event['end'],
                    "html_link": created_event.get('htmlLink')
                }
            }
            
        except HttpError as error:
            logger.error(f"Calendar API error creating event: {error}")
            return {"success": False, "error": f"Calendar API error: {error}"}
        except Exception as e:
            logger.error(f"Unexpected error creating event: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}
    
    def get_available_slots(self, 
                           start_date: datetime, 
                           end_date: datetime, 
                           duration_minutes: int = 60,
                           business_hours_start: int = 9,
                           business_hours_end: int = 17) -> List[Dict[str, datetime]]:
        """Get available time slots within business hours"""
        if not self.service:
            return []
        
        try:
            available_slots = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                # Skip weekends (optional)
                if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                    # Generate time slots for the day
                    day_start = datetime.combine(current_date, datetime.min.time().replace(hour=business_hours_start))
                    day_end = datetime.combine(current_date, datetime.min.time().replace(hour=business_hours_end))
                    
                    # Check each hour slot
                    current_time = day_start
                    while current_time + timedelta(minutes=duration_minutes) <= day_end:
                        slot_end = current_time + timedelta(minutes=duration_minutes)
                        
                        # Check if this slot is available
                        availability = self.check_availability(current_time, slot_end)
                        if availability.get("available", False):
                            available_slots.append({
                                "start": current_time,
                                "end": slot_end
                            })
                        
                        current_time += timedelta(hours=1)  # Check hourly slots
                
                current_date += timedelta(days=1)
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []
    
    def suggest_alternative_times(self, 
                                 preferred_start: datetime, 
                                 duration_minutes: int = 60,
                                 suggestions_count: int = 3) -> List[Dict[str, datetime]]:
        """Suggest alternative times if preferred time is not available"""
        # Look for alternatives within the next 7 days
        search_end = preferred_start + timedelta(days=7)
        
        available_slots = self.get_available_slots(
            preferred_start, 
            search_end, 
            duration_minutes
        )
        
        # Return up to suggestions_count alternatives
        return available_slots[:suggestions_count]
