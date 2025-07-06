"""
Pydantic models for the TailorTalk Booking Agent
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="Agent response")
    session_id: str = Field(..., description="Session identifier")
    intent: Optional[str] = Field(None, description="Detected intent")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Extracted booking data")
    suggested_actions: Optional[List[str]] = Field(None, description="Suggested next actions")


class BookingRequest(BaseModel):
    """Booking request model"""
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    start_datetime: datetime = Field(..., description="Event start time")
    end_datetime: datetime = Field(..., description="Event end time")
    attendee_email: Optional[str] = Field(None, description="Attendee email")
    location: Optional[str] = Field(None, description="Event location")
    session_id: Optional[str] = Field(None, description="Session identifier")


class BookingResponse(BaseModel):
    """Booking response model"""
    success: bool = Field(..., description="Booking success status")
    event_id: Optional[str] = Field(None, description="Google Calendar event ID")
    message: str = Field(..., description="Booking result message")
    event_details: Optional[Dict[str, Any]] = Field(None, description="Created event details")


class AvailabilityRequest(BaseModel):
    """Availability check request"""
    start_date: datetime = Field(..., description="Start date for availability check")
    end_date: datetime = Field(..., description="End date for availability check")
    duration_minutes: int = Field(60, description="Duration of the meeting in minutes")


class AvailabilityResponse(BaseModel):
    """Availability response model"""
    available_slots: List[Dict[str, datetime]] = Field(..., description="Available time slots")
    busy_periods: List[Dict[str, datetime]] = Field(..., description="Busy time periods")


class ExtractedBookingData(BaseModel):
    """Extracted booking data from natural language"""
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    duration: Optional[int] = 60  # Default 1 hour
    description: Optional[str] = None
    location: Optional[str] = None
    attendee_email: Optional[str] = None
    confidence: float = 0.0


class AgentState(BaseModel):
    """Agent conversation state"""
    session_id: str
    current_step: str = "greeting"
    extracted_data: ExtractedBookingData = Field(default_factory=ExtractedBookingData)
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    last_response: Optional[str] = None
    confirmed_booking: bool = False
