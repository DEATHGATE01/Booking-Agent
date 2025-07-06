"""
Chat endpoints for conversational interaction
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from ..models import ChatMessage, ChatResponse
from ..services.booking_agent import BookingAgent
from ..utils.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Global booking agent instance
booking_agent = BookingAgent()


@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage) -> ChatResponse:
    """
    Process a chat message and return AI response
    """
    try:
        logger.info(f"Received message: {message.message[:100]}...")
        
        # Process the message through the booking agent
        result = booking_agent.process_message(
            message=message.message,
            session_id=message.session_id
        )
        
        response = ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            intent=result.get("current_step"),
            extracted_data=result.get("extracted_data"),
            suggested_actions=[result.get("next_action")] if result.get("next_action") else None
        )
        
        logger.info(f"Sending response: {response.response[:100]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@router.get("/session/{session_id}/history")
async def get_conversation_history(session_id: str) -> Dict[str, Any]:
    """
    Get conversation history for a session
    """
    try:
        if session_id not in booking_agent.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = booking_agent.sessions[session_id]
        
        return {
            "session_id": session_id,
            "current_step": session.current_step,
            "conversation_history": session.conversation_history,
            "extracted_data": session.extracted_data.dict(),
            "confirmed_booking": session.confirmed_booking
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.delete("/session/{session_id}")
async def clear_session(session_id: str) -> Dict[str, str]:
    """
    Clear a conversation session
    """
    try:
        if session_id in booking_agent.sessions:
            del booking_agent.sessions[session_id]
            return {"message": f"Session {session_id} cleared successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")


@router.get("/sessions")
async def list_active_sessions() -> Dict[str, Any]:
    """
    List all active chat sessions
    """
    try:
        sessions_info = {}
        for session_id, session in booking_agent.sessions.items():
            sessions_info[session_id] = {
                "current_step": session.current_step,
                "message_count": len(session.conversation_history),
                "confirmed_booking": session.confirmed_booking,
                "last_activity": session.conversation_history[-1]["timestamp"] if session.conversation_history else None
            }
        
        return {
            "active_sessions": sessions_info,
            "total_sessions": len(sessions_info)
        }
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.post("/quick-actions/suggest-times")
async def suggest_alternative_times(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest alternative times for booking
    """
    try:
        # This would integrate with the calendar service to suggest alternatives
        # For now, return a placeholder response
        return {
            "suggested_times": [
                "Tomorrow at 2:00 PM",
                "Day after tomorrow at 10:00 AM",
                "Next Monday at 3:00 PM"
            ],
            "message": "Here are some alternative times that might work for you:"
        }
        
    except Exception as e:
        logger.error(f"Error suggesting times: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error suggesting times: {str(e)}")
