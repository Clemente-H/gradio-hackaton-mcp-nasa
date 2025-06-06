"""APOD MCP implementation."""

from typing import Dict, List, Any
import asyncio
from datetime import datetime
import sys
import os

# Ajustar imports para estructura actual
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_mcp import BaseMCP
from nasa_api.apod_client import APODClient
from schemas.apod_schemas import APODResponse, APODByDateArgs, APODDateRangeArgs


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
