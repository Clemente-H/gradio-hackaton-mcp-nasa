"""NASA Mars Rover Photos API client."""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
from tenacity import retry, stop_after_attempt, wait_exponential

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, NASA_ENDPOINTS


class MarsRoverClient:
    """Client for NASA Mars Rover Photos API."""
    
    # Available rovers and their details
    ROVERS = {
        "curiosity": {
            "name": "Curiosity",
            "landing_date": "2012-08-06",
            "launch_date": "2011-11-26",
            "status": "active",
            "max_sol": 4000,  # Approximate - will be updated from API
            "cameras": ["FHAZ", "RHAZ", "MAST", "CHEMCAM", "MAHLI", "MARDI", "NAVCAM"]
        },
        "opportunity": {
            "name": "Opportunity", 
            "landing_date": "2004-01-25",
            "launch_date": "2003-07-07",
            "status": "complete",
            "max_sol": 5111,
            "cameras": ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"]
        },
        "spirit": {
            "name": "Spirit",
            "landing_date": "2004-01-04", 
            "launch_date": "2003-06-10",
            "status": "complete",
            "max_sol": 2208,
            "cameras": ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"]
        }
    }
    
    def __init__(self):
        self.api_key = Config.NASA_API_KEY
        self.base_url = NASA_ENDPOINTS.MARS_ROVER
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 3.6  # seconds
    
    def _rate_limit(self):
        """Simple rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        self._rate_limit()
        
        # Add API key to params
        params["api_key"] = self.api_key
        
        response = self.session.get(
            url,
            params=params,
            timeout=Config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def get_rover_info(self, rover: str) -> Dict[str, Any]:
        """Get rover information and status."""
        rover = rover.lower()
        if rover not in self.ROVERS:
            raise ValueError(f"Unknown rover: {rover}. Available: {list(self.ROVERS.keys())}")
        
        try:
            url = f"{self.base_url}/{rover}"
            data = self._make_request(url, {})
            return data
        except Exception as e:
            raise Exception(f"Failed to get rover info for {rover}: {str(e)}")
    
    def get_latest_photos(self, rover: str, count: int = 25) -> Dict[str, Any]:
        """Get latest photos from a rover."""
        rover = rover.lower()
        if rover not in self.ROVERS:
            raise ValueError(f"Unknown rover: {rover}")
        
        try:
            url = f"{self.base_url}/{rover}/latest_photos"
            params = {"page": 1}
            data = self._make_request(url, params)
            
            # Limit to requested count
            if "latest_photos" in data and len(data["latest_photos"]) > count:
                data["latest_photos"] = data["latest_photos"][:count]
            
            return data
        except Exception as e:
            raise Exception(f"Failed to get latest photos for {rover}: {str(e)}")
    
    def get_photos_by_earth_date(self, rover: str, earth_date: str, camera: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
        """Get photos by Earth date."""
        rover = rover.lower()
        if rover not in self.ROVERS:
            raise ValueError(f"Unknown rover: {rover}")
        
        try:
            # Validate date
            datetime.strptime(earth_date, "%Y-%m-%d")
            
            url = f"{self.base_url}/{rover}/photos"
            params = {
                "earth_date": earth_date,
                "page": page
            }
            
            if camera:
                camera = camera.upper()
                if camera not in self.ROVERS[rover]["cameras"]:
                    raise ValueError(f"Invalid camera {camera} for {rover}")
                params["camera"] = camera
            
            return self._make_request(url, params)
        
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Failed to get photos for {rover} on {earth_date}: {str(e)}")
    
    def get_photos_by_sol(self, rover: str, sol: int, camera: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
        """Get photos by Martian sol (day)."""
        rover = rover.lower()
        if rover not in self.ROVERS:
            raise ValueError(f"Unknown rover: {rover}")
        
        if sol < 0 or sol > self.ROVERS[rover]["max_sol"]:
            raise ValueError(f"Sol {sol} out of range for {rover} (0-{self.ROVERS[rover]['max_sol']})")
        
        try:
            url = f"{self.base_url}/{rover}/photos"
            params = {
                "sol": sol,
                "page": page
            }
            
            if camera:
                camera = camera.upper()
                if camera not in self.ROVERS[rover]["cameras"]:
                    raise ValueError(f"Invalid camera {camera} for {rover}")
                params["camera"] = camera
            
            return self._make_request(url, params)
        
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Failed to get photos for {rover} on sol {sol}: {str(e)}")
    
    def get_photos_by_camera(self, rover: str, camera: str, limit: int = 20) -> Dict[str, Any]:
        """Get recent photos from a specific camera."""
        rover = rover.lower()
        camera = camera.upper()
        
        if rover not in self.ROVERS:
            raise ValueError(f"Unknown rover: {rover}")
        
        if camera not in self.ROVERS[rover]["cameras"]:
            raise ValueError(f"Invalid camera {camera} for {rover}")
        
        try:
            # Get latest photos and filter by camera
            latest_data = self.get_latest_photos(rover, count=100)  # Get more to filter
            
            if "latest_photos" in latest_data:
                camera_photos = [
                    photo for photo in latest_data["latest_photos"] 
                    if photo["camera"]["name"] == camera
                ][:limit]
                
                return {
                    "photos": camera_photos,
                    "rover": latest_data.get("latest_photos", [{}])[0].get("rover", {}),
                    "camera_filter": camera,
                    "total_found": len(camera_photos)
                }
            else:
                return {"photos": [], "camera_filter": camera, "total_found": 0}
        
        except Exception as e:
            raise Exception(f"Failed to get {camera} photos for {rover}: {str(e)}")
