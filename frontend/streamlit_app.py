"""
TailorTalk Booking Agent - Streamlit Frontend
A modern, conversational interface for booking calendar appointments
"""

import streamlit as st
import requests
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Support both local and deployed environments
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
CHAT_ENDPOINT = f"{API_BASE_URL}/chat/message"
AVAILABILITY_ENDPOINT = f"{API_BASE_URL}/booking/check-availability"

# Page configuration
st.set_page_config(
    page_title="TailorTalk Booking Agent",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.8rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .assistant-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.8rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    
    .status-info {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-info {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .quick-action-btn {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        margin: 0.25rem;
        cursor: pointer;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'conversation_step' not in st.session_state:
        st.session_state.conversation_step = "greeting"
    
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = {}
    
    if 'booking_confirmed' not in st.session_state:
        st.session_state.booking_confirmed = False


def send_message_to_api(message: str) -> Dict[str, Any]:
    """Send message to the backend API"""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(
            CHAT_ENDPOINT,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def display_chat_history():
    """Display the conversation history"""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")
        
        if role == "user":
            st.markdown(
                f'<div class="user-message">{content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="assistant-message">{content}</div>',
                unsafe_allow_html=True
            )


def add_message(role: str, content: str):
    """Add a message to the conversation history"""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.messages.append(message)


def display_extracted_data():
    """Display extracted booking data in sidebar"""
    if st.session_state.extracted_data:
        st.sidebar.markdown("### 📋 Booking Information")
        
        data = st.session_state.extracted_data
        
        if data.get('title'):
            st.sidebar.markdown(f"**Type:** {data['title']}")
        
        if data.get('date'):
            st.sidebar.markdown(f"**Date:** {data['date']}")
        
        if data.get('time'):
            st.sidebar.markdown(f"**Time:** {data['time']}")
        
        if data.get('duration'):
            st.sidebar.markdown(f"**Duration:** {data['duration']} minutes")
        
        if data.get('description'):
            st.sidebar.markdown(f"**Description:** {data['description']}")
        
        if data.get('location'):
            st.sidebar.markdown(f"**Location:** {data['location']}")


def display_quick_actions():
    """Display quick action buttons"""
    st.sidebar.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📅 Book Meeting", key="quick_meeting"):
            user_input = "I want to book a meeting"
            add_message("user", user_input)
            process_user_input(user_input)
    
    with col2:
        if st.button("🏥 Doctor Appointment", key="quick_doctor"):
            user_input = "I need to schedule a doctor appointment"
            add_message("user", user_input)
            process_user_input(user_input)
    
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button("☕ Coffee Chat", key="quick_coffee"):
            user_input = "Schedule a coffee meeting"
            add_message("user", user_input)
            process_user_input(user_input)
    
    with col4:
        if st.button("📞 Call", key="quick_call"):
            user_input = "Book a phone call"
            add_message("user", user_input)
            process_user_input(user_input)


def display_conversation_status():
    """Display current conversation status"""
    step = st.session_state.conversation_step
    
    status_messages = {
        "greeting": "👋 Ready to help you book appointments",
        "collecting_info": "📝 Gathering booking details",
        "checking_availability": "🔍 Checking calendar availability",
        "confirming": "✅ Ready to confirm your booking",
        "completed": "🎉 Booking completed successfully!"
    }
    
    status_msg = status_messages.get(step, f"Current step: {step}")
    
    st.sidebar.markdown("### 📊 Status")
    st.sidebar.markdown(
        f'<div class="status-info">{status_msg}</div>',
        unsafe_allow_html=True
    )


def process_user_input(user_input: str):
    """Process user input and get AI response"""
    with st.spinner("🤔 Thinking..."):
        response = send_message_to_api(user_input)
        
        if response:
            # Update session state
            st.session_state.conversation_step = response.get("intent", st.session_state.conversation_step)
            st.session_state.extracted_data = response.get("extracted_data", {})
            
            # Add assistant response
            add_message("assistant", response["response"])
            
            # Rerun to update the display
            st.rerun()


def display_help_section():
    """Display help and examples"""
    st.sidebar.markdown("### 💡 Example Phrases")
    
    examples = [
        "Book a meeting tomorrow at 2 PM",
        "Schedule a doctor appointment next Monday",
        "I need a 30-minute call with John at 3 PM",
        "Book lunch meeting for Friday at noon",
        "Schedule a 2-hour workshop next week"
    ]
    
    for example in examples:
        if st.sidebar.button(f"💬 '{example}'", key=f"example_{hash(example)}"):
            add_message("user", example)
            process_user_input(example)


def display_calendar_status():
    """Display calendar service status"""
    try:
        response = requests.get(f"{API_BASE_URL}/booking/calendar-status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            st.sidebar.markdown("### 📅 Calendar Status")
            
            if status.get("connection_test", {}).get("connected", False):
                st.sidebar.markdown("🟢 **Connected**")
            else:
                st.sidebar.markdown("🔴 **Disconnected**")
                if status.get("connection_test", {}).get("error"):
                    st.sidebar.markdown(f"Error: {status['connection_test']['error']}")
        else:
            st.sidebar.markdown("### 📅 Calendar Status")
            st.sidebar.markdown("⚠️ **Status Unknown**")
    except:
        st.sidebar.markdown("### 📅 Calendar Status")
        st.sidebar.markdown("❌ **Service Unavailable**")


def main():
    """Main application function"""
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">📅 TailorTalk Booking Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Your AI-powered appointment scheduling assistant</p>', unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.markdown("### 💬 Conversation")
        
        # Chat container
        chat_container = st.container()
        with chat_container:
            display_chat_history()
        
        # Input area
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Type your message here...",
                placeholder="e.g., 'Book a meeting tomorrow at 2 PM'",
                key="user_input"
            )
            
            col_send, col_clear = st.columns([1, 4])
            
            with col_send:
                submit_button = st.form_submit_button("Send 📤")
            
            if submit_button and user_input.strip():
                add_message("user", user_input)
                process_user_input(user_input)
    
    with col2:
        # Sidebar content
        display_conversation_status()
        display_extracted_data()
        display_quick_actions()
        display_help_section()
        display_calendar_status()
        
        # Clear conversation button
        st.markdown("---")
        if st.button("🗑️ Clear Conversation", type="secondary"):
            st.session_state.messages = []
            st.session_state.extracted_data = {}
            st.session_state.conversation_step = "greeting"
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #888; font-size: 0.9rem;">'
        'Built with ❤️ for TailorTalk Internship Assignment | '
        f'Session ID: {st.session_state.session_id[:8]}...'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
