"""Pydantic schemas for Mars Rover data."""

from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime
from typing import Optional, List, Dict, Any


class Camera(BaseModel):
    """Camera information."""
    id: int
    name: str
    rover_id: int
    full_name: str


class Rover(BaseModel):
    """Rover information."""
    id: int
    name: str
    landing_date: str
    launch_date: str
    status: str
    max_sol: Optional[int] = None
    max_date: Optional[str] = None
    total_photos: Optional[int] = None


class RoverPhoto(BaseModel):
    """Individual rover photo."""
    id: int
    sol: int
    camera: Camera
    img_src: HttpUrl
    earth_date: str
    rover: Rover


class MarsRoverResponse(BaseModel):
    """Schema for Mars Rover API response."""
    photos: List[RoverPhoto]


class LatestPhotosResponse(BaseModel):
    """Schema for latest photos response."""
    latest_photos: List[RoverPhoto]


class RoverInfoResponse(BaseModel):
    """Schema for rover info response."""
    rover: Rover
    

class MarsRoverToolArgs(BaseModel):
    """Base class for Mars Rover tool arguments."""
    pass


class RoverArgs(MarsRoverToolArgs):
    """Arguments requiring only rover name."""
    rover: str
    
    @validator('rover')
    def validate_rover(cls, v):
        valid_rovers = ["curiosity", "opportunity", "spirit"]
        if v.lower() not in valid_rovers:
            raise ValueError(f"Invalid rover. Must be one of: {valid_rovers}")
        return v.lower()


class RoverPhotosArgs(RoverArgs):
    """Arguments for getting rover photos with optional count."""
    count: Optional[int] = 25
    
    @validator('count')
    def validate_count(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError("Count must be between 1 and 100")
        return v


class RoverDateArgs(RoverArgs):
    """Arguments for date-based photo queries."""
    earth_date: str
    camera: Optional[str] = None
    
    @validator('earth_date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class RoverSolArgs(RoverArgs):
    """Arguments for sol-based photo queries."""
    sol: int
    camera: Optional[str] = None
    
    @validator('sol')
    def validate_sol(cls, v):
        if v < 0:
            raise ValueError("Sol must be non-negative")
        return v


class RoverCameraArgs(RoverArgs):
    """Arguments for camera-specific queries."""
    camera: str
    count: Optional[int] = 20
    
    @validator('count')
    def validate_count(cls, v):
        if v is not None and (v < 1 or v > 50):
            raise ValueError("Count must be between 1 and 50")
        return v