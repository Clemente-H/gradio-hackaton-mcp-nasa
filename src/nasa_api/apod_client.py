# src/nasa_api/apod_client.py
"""NASA APOD API client with rate limiting and error handling."""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import time
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import Config, NASA_ENDPOINTS


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


# src/schemas/apod_schemas.py
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


# src/mcps/apod_mcp.py
"""APOD MCP implementation."""

from typing import Dict, List, Any
import asyncio
from datetime import datetime

from .base_mcp import BaseMCP
from ..nasa_api.apod_client import APODClient
from ..schemas.apod_schemas import APODResponse, APODByDateArgs, APODDateRangeArgs


class APODMCP(BaseMCP):
    """MCP for NASA Astronomy Picture of the Day API."""
    
    def __init__(self):
        super().__init__(
            name="nasa-apod",
            description="Access NASA's Astronomy Picture of the Day data"
        )
        self.client = APODClient()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return available APOD tools."""
        return [
            {
                "name": "get_apod_today",
                "description": "Get today's Astronomy Picture of the Day",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_apod_by_date",
                "description": "Get APOD for a specific date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["date"]
                }
            },
            {
                "name": "get_apod_date_range",
                "description": "Get APOD for a date range (max 100 days)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute APOD tool."""
        try:
            if tool_name == "get_apod_today":
                return await self._get_apod_today()
            elif tool_name == "get_apod_by_date":
                args = APODByDateArgs(**arguments)
                return await self._get_apod_by_date(args.date)
            elif tool_name == "get_apod_date_range":
                args = APODDateRangeArgs(**arguments)
                return await self._get_apod_date_range(args.start_date, args.end_date)
            else:
                return self._format_error(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            self.logger.error(f"Error in {tool_name}: {str(e)}")
            return self._format_error(f"Tool execution failed: {str(e)}")
    
    async def _get_apod_today(self) -> Dict[str, Any]:
        """Get today's APOD."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_apod_today)
            
            # Validate and format response
            apod = APODResponse(**data)
            
            return self._format_success(
                data=apod.dict(),
                message=f"Today's astronomy picture: {apod.title}"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get today's APOD: {str(e)}")
    
    async def _get_apod_by_date(self, date: str) -> Dict[str, Any]:
        """Get APOD for specific date."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_apod_by_date, date)
            
            apod = APODResponse(**data)
            
            return self._format_success(
                data=apod.dict(),
                message=f"APOD for {date}: {apod.title}"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get APOD for {date}: {str(e)}")
    
    async def _get_apod_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get APOD for date range."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self.client.get_apod_date_range, 
                start_date, 
                end_date
            )
            
            # Handle both single item and list responses
            if isinstance(data, list):
                apods = [APODResponse(**item) for item in data]
                apod_dicts = [apod.dict() for apod in apods]
                message = f"Found {len(apods)} APODs from {start_date} to {end_date}"
            else:
                apod = APODResponse(**data)
                apod_dicts = [apod.dict()]
                message = f"Found 1 APOD from {start_date} to {end_date}"
            
            return self._format_success(
                data=apod_dicts,
                message=message
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get APOD range: {str(e)}")


# tests/test_apod_mcp.py
"""Basic tests for APOD MCP."""

import pytest
import asyncio
from src.mcps.apod_mcp import APODMCP


class TestAPODMCP:
    """Test APOD MCP functionality."""
    
    @pytest.fixture
    def apod_mcp(self):
        """Create APOD MCP instance."""
        return APODMCP()
    
    def test_initialization(self, apod_mcp):
        """Test MCP initialization."""
        assert apod_mcp.name == "nasa-apod"
        assert "Astronomy Picture of the Day" in apod_mcp.description
    
    def test_get_tools(self, apod_mcp):
        """Test tools discovery."""
        tools = apod_mcp.get_tools()
        assert len(tools) == 3
        
        tool_names = [tool["name"] for tool in tools]
        assert "get_apod_today" in tool_names
        assert "get_apod_by_date" in tool_names
        assert "get_apod_date_range" in tool_names
    
    @pytest.mark.asyncio
    async def test_get_apod_today(self, apod_mcp):
        """Test getting today's APOD."""
        result = await apod_mcp.call_tool("get_apod_today", {})
        
        assert result["success"] is True
        assert "data" in result
        assert "title" in result["data"]
        assert "explanation" in result["data"]
    
    @pytest.mark.asyncio
    async def test_get_apod_by_date(self, apod_mcp):
        """Test getting APOD by date."""
        result = await apod_mcp.call_tool("get_apod_by_date", {"date": "2023-01-01"})
        
        assert result["success"] is True
        assert result["data"]["date"] == "2023-01-01"
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(self, apod_mcp):
        """Test error handling for invalid date format."""
        result = await apod_mcp.call_tool("get_apod_by_date", {"date": "invalid-date"})
        
        assert result["success"] is False
        assert "error" in result


if __name__ == "__main__":
    # Quick test run
    async def quick_test():
        apod = APODMCP()
        print("APOD MCP Tools:", apod.get_tools())
        
        # Test today's APOD
        result = await apod.call_tool("get_apod_today", {})
        print("Today's APOD:", result.get("message", "Error"))
    
    asyncio.run(quick_test())