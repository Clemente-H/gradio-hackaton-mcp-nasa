"""NASA NeoWs API client for Near Earth Objects."""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time
from tenacity import retry, stop_after_attempt, wait_exponential

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, NASA_ENDPOINTS


class NeoWsClient:
    """Client for NASA Near Earth Object Web Service API."""
    
    def __init__(self):
        self.api_key = Config.NASA_API_KEY
        self.feed_url = NASA_ENDPOINTS.NEOWS_FEED
        self.lookup_url = NASA_ENDPOINTS.NEOWS_LOOKUP
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
    
    def get_asteroids_today(self) -> Dict[str, Any]:
        """Get asteroids approaching Earth today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_asteroids_date_range(today, today)
    
    def get_asteroids_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get asteroids for a date range."""
        try:
            # Validate dates
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                raise ValueError("Start date must be before end date")
            
            # NASA API limits range to 7 days
            if (end - start).days > 7:
                raise ValueError("Date range cannot exceed 7 days")
            
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "detailed": "true"  # Get detailed information
            }
            
            return self._make_request(self.feed_url, params)
        
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Failed to fetch asteroids for {start_date} to {end_date}: {str(e)}")
    
    def get_asteroid_by_id(self, asteroid_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific asteroid."""
        try:
            url = f"{self.lookup_url}/{asteroid_id}"
            return self._make_request(url, {})
        except Exception as e:
            raise Exception(f"Failed to fetch asteroid {asteroid_id}: {str(e)}")
    
    def get_asteroids_week(self) -> Dict[str, Any]:
        """Get asteroids for the current week."""
        today = datetime.now()
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=6)).strftime("%Y-%m-%d")
        return self.get_asteroids_date_range(start_date, end_date)
