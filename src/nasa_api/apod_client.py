"""NASA APOD API client with rate limiting and error handling."""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Ajustar imports para la estructura actual
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, NASA_ENDPOINTS


class APODClient:
    """Client for NASA Astronomy Picture of the Day API."""
    
    def __init__(self):
        self.api_key = Config.NASA_API_KEY
        self.base_url = NASA_ENDPOINTS.APOD
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 3.6  # seconds (to stay under 1000/hour)
    
    def _rate_limit(self):
        """Simple rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        self._rate_limit()
        
        # Add API key to params
        params["api_key"] = self.api_key
        
        response = self.session.get(
            self.base_url,
            params=params,
            timeout=Config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    def get_apod_today(self) -> Dict[str, Any]:
        """Get today's Astronomy Picture of the Day."""
        try:
            return self._make_request({})
        except Exception as e:
            raise Exception(f"Failed to fetch today's APOD: {str(e)}")
    
    def get_apod_by_date(self, date: str) -> Dict[str, Any]:
        """Get APOD for a specific date (YYYY-MM-DD format)."""
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
            
            return self._make_request({"date": date})
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        except Exception as e:
            raise Exception(f"Failed to fetch APOD for {date}: {str(e)}")
    
    def get_apod_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get APOD for a date range."""
        try:
            # Validate dates
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                raise ValueError("Start date must be before end date")
            
            # NASA API limits range to 100 days
            if (end - start).days > 100:
                raise ValueError("Date range cannot exceed 100 days")
            
            return self._make_request({
                "start_date": start_date,
                "end_date": end_date
            })
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Failed to fetch APOD range {start_date} to {end_date}: {str(e)}")
