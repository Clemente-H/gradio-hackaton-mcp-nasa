"""Configuration settings for NASA Space Explorer."""

import os
from typing import Optional

class Config:
    """Application configuration."""
    
    # NASA API Configuration
    NASA_API_KEY: str = os.getenv("NASA_API_KEY", "DEMO_KEY")
    NASA_BASE_URL: str = "https://api.nasa.gov"
    
    # Rate limiting
    MAX_REQUESTS_PER_HOUR: int = 950  # Leave buffer under NASA's 1000/hour limit
    REQUEST_TIMEOUT: int = 30  # seconds
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        if cls.NASA_API_KEY == "DEMO_KEY":
            print("⚠️  Using DEMO_KEY - consider using your personal NASA API key")
        
        return cls.NASA_API_KEY is not None

# API Endpoints
class NASA_ENDPOINTS:
    """NASA API endpoints."""
    
    APOD = f"{Config.NASA_BASE_URL}/planetary/apod"
    NEOWS_FEED = f"{Config.NASA_BASE_URL}/neo/rest/v1/feed"
    NEOWS_LOOKUP = f"{Config.NASA_BASE_URL}/neo/rest/v1/neo"
    MARS_ROVER = f"{Config.NASA_BASE_URL}/mars-photos/api/v1/rovers"
