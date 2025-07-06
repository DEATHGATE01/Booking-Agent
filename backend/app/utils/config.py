"""
Configuration settings for the TailorTalk Booking Agent
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application settings
    app_name: str = "TailorTalk Booking Agent"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API settings
    api_host: str = "localhost"
    api_port: int = 8000
    
    # Google Calendar settings
    google_calendar_credentials_path: str = "credentials/service-account-key.json"
    google_calendar_id: str = ""
    
    # OpenAI settings
    openai_api_key: Optional[str] = None
    
    # Gemini settings
    gemini_api_key: Optional[str] = None
    
    # Timezone
    timezone: str = "UTC"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
