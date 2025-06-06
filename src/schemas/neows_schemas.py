"""Pydantic schemas for NeoWs data."""

from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class EstimatedDiameter(BaseModel):
    """Estimated diameter in different units."""
    kilometers: Dict[str, float]
    meters: Dict[str, float]
    miles: Dict[str, float]
    feet: Dict[str, float]


class RelativeVelocity(BaseModel):
    """Relative velocity in different units."""
    kilometers_per_second: str
    kilometers_per_hour: str
    miles_per_hour: str


class MissDistance(BaseModel):
    """Miss distance in different units."""
    astronomical: str
    lunar: str
    kilometers: str
    miles: str


class CloseApproachData(BaseModel):
    """Close approach data for an asteroid."""
    close_approach_date: str
    close_approach_date_full: str
    epoch_date_close_approach: int
    relative_velocity: RelativeVelocity
    miss_distance: MissDistance
    orbiting_body: str


class AsteroidData(BaseModel):
    """Individual asteroid data."""
    id: str
    neo_reference_id: str
    name: str
    nasa_jpl_url: str
    absolute_magnitude_h: float
    estimated_diameter: EstimatedDiameter
    is_potentially_hazardous_asteroid: bool
    close_approach_data: List[CloseApproachData]
    is_sentry_object: bool


class NeoWsResponse(BaseModel):
    """Schema for NeoWs API response."""
    element_count: int
    near_earth_objects: Dict[str, List[AsteroidData]]
    
    def get_all_asteroids(self) -> List[AsteroidData]:
        """Get all asteroids from all dates."""
        all_asteroids = []
        for date_asteroids in self.near_earth_objects.values():
            all_asteroids.extend(date_asteroids)
        return all_asteroids
    
    def get_potentially_hazardous(self) -> List[AsteroidData]:
        """Get only potentially hazardous asteroids."""
        return [ast for ast in self.get_all_asteroids() if ast.is_potentially_hazardous_asteroid]
    
    def get_largest_asteroids(self, count: int = 5) -> List[AsteroidData]:
        """Get the largest asteroids by diameter."""
        asteroids = self.get_all_asteroids()
        return sorted(
            asteroids,
            key=lambda x: x.estimated_diameter.kilometers["estimated_diameter_max"],
            reverse=True
        )[:count]


class NeoWsToolArgs(BaseModel):
    """Base class for NeoWs tool arguments."""
    pass


class DateRangeArgs(NeoWsToolArgs):
    """Arguments for date range queries."""
    start_date: str
    end_date: str
    
    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Dates must be in YYYY-MM-DD format")


class AsteroidByIdArgs(NeoWsToolArgs):
    """Arguments for asteroid lookup by ID."""
    asteroid_id: str
    
    @validator('asteroid_id')
    def validate_id(cls, v):
        if not v.strip():
            raise ValueError("Asteroid ID cannot be empty")
        return v.strip()


class LargestAsteroidsArgs(NeoWsToolArgs):
    """Arguments for getting largest asteroids."""
    count: Optional[int] = Field(default=5, ge=1, le=20)
