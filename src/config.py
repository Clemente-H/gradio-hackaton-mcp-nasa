"""Configuration settings for NASA Space Explorer."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # NASA API Configuration
    NASA_API_KEY: str = os.getenv("NASA_API_KEY", "DEMO_KEY")
    NASA_BASE_URL: str = "https://api.nasa.gov"
    
    # LLM Configuration
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = "mistral-large-latest"
    MISTRAL_BASE_URL: str = "https://api.mistral.ai/v1"
    
    # Rate limiting
    MAX_REQUESTS_PER_HOUR: int = 950
    REQUEST_TIMEOUT: int = 30
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        if cls.NASA_API_KEY == "DEMO_KEY":
            print("⚠️  Using DEMO_KEY - consider using your personal NASA API key")
        
        if not cls.MISTRAL_API_KEY:
            print("⚠️  MISTRAL_API_KEY not set - chat features will be disabled")
            return False
        
        return cls.NASA_API_KEY is not None
# API Endpoints
class NASA_ENDPOINTS:
    """NASA API endpoints."""
    
    APOD = f"{Config.NASA_BASE_URL}/planetary/apod"
    NEOWS_FEED = f"{Config.NASA_BASE_URL}/neo/rest/v1/feed"
    NEOWS_LOOKUP = f"{Config.NASA_BASE_URL}/neo/rest/v1/neo"
    MARS_ROVER = f"{Config.NASA_BASE_URL}/mars-photos/api/v1/rovers"
