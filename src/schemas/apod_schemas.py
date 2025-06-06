"""Pydantic schemas for APOD data."""

from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime
from typing import Optional, List


class APODResponse(BaseModel):
    """Schema for APOD API response."""
    
    date: str
    title: str
    explanation: str
    url: HttpUrl
    hdurl: Optional[HttpUrl] = None
    media_type: str
    service_version: str
    copyright: Optional[str] = None
    
    @validator('date')
    def validate_date(cls, v):
        """Validate date format."""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    @validator('media_type')
    def validate_media_type(cls, v):
        """Validate media type."""
        if v not in ['image', 'video']:
            raise ValueError("Media type must be 'image' or 'video'")
        return v


class APODToolArgs(BaseModel):
    """Base class for APOD tool arguments."""
    pass


class APODByDateArgs(APODToolArgs):
    """Arguments for get_apod_by_date tool."""
    date: str
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class APODDateRangeArgs(APODToolArgs):
    """Arguments for get_apod_date_range tool."""
    start_date: str
    end_date: str
    
    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format")
