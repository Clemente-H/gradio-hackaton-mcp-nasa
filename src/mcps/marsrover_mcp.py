"""Mars Rover MCP implementation."""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_mcp import BaseMCP
from nasa_api.marsrover_client import MarsRoverClient
from schemas.marsrover_schemas import (
    MarsRoverResponse, LatestPhotosResponse, RoverInfoResponse,
    RoverArgs, RoverPhotosArgs, RoverDateArgs, RoverSolArgs, RoverCameraArgs,
    RoverPhoto
)


class MarsRoverMCP(BaseMCP):
    """MCP for NASA Mars Rover Photos API."""
    
    def __init__(self):
        super().__init__(
            name="nasa-marsrover",
            description="Access NASA Mars Rover photos and mission data from Curiosity, Opportunity, and Spirit"
        )
        self.client = MarsRoverClient()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return available Mars Rover tools."""
        return [
            {
                "name": "get_rover_status",
                "description": "Get rover information and mission status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rover": {
                            "type": "string",
                            "description": "Rover name: curiosity, opportunity, or spirit",
                            "enum": ["curiosity", "opportunity", "spirit"]
                        }
                    },
                    "required": ["rover"]
                }
            },
            {
                "name": "get_latest_photos",
                "description": "Get the most recent photos from a rover",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rover": {
                            "type": "string",
                            "description": "Rover name",
                            "enum": ["curiosity", "opportunity", "spirit"]
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of photos to return (1-100)",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 25
                        }
                    },
                    "required": ["rover"]
                }
            },
            {
                "name": "get_photos_by_earth_date",
                "description": "Get photos taken on a specific Earth date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rover": {
                            "type": "string",
                            "description": "Rover name",
                            "enum": ["curiosity", "opportunity", "spirit"]
                        },
                        "earth_date": {
                            "type": "string",
                            "description": "Earth date in YYYY-MM-DD format",
                            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "camera": {
                            "type": "string",
                            "description": "Optional camera filter (FHAZ, RHAZ, MAST, NAVCAM, etc.)"
                        }
                    },
                    "required": ["rover", "earth_date"]
                }
            },
            {
                "name": "get_photos_by_sol",
                "description": "Get photos taken on a specific Martian sol (day)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rover": {
                            "type": "string",
                            "description": "Rover name",
                            "enum": ["curiosity", "opportunity", "spirit"]
                        },
                        "sol": {
                            "type": "integer",
                            "description": "Martian sol (day) number",
                            "minimum": 0
                        },
                        "camera": {
                            "type": "string",
                            "description": "Optional camera filter"
                        }
                    },
                    "required": ["rover", "sol"]
                }
            },
            {
                "name": "get_photos_by_camera",
                "description": "Get recent photos from a specific camera",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rover": {
                            "type": "string",
                            "description": "Rover name",
                            "enum": ["curiosity", "opportunity", "spirit"]
                        },
                        "camera": {
                            "type": "string",
                            "description": "Camera name (FHAZ, RHAZ, MAST, NAVCAM, etc.)"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of photos to return (1-50)",
                            "minimum": 1,
                            "maximum": 50,
                            "default": 20
                        }
                    },
                    "required": ["rover", "camera"]
                }
            },
            {
                "name": "compare_rovers",
                "description": "Compare mission stats across all rovers",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Mars Rover tool."""
        try:
            if tool_name == "get_rover_status":
                args = RoverArgs(**arguments)
                return await self._get_rover_status(args.rover)
            elif tool_name == "get_latest_photos":
                args = RoverPhotosArgs(**arguments)
                return await self._get_latest_photos(args.rover, args.count)
            elif tool_name == "get_photos_by_earth_date":
                args = RoverDateArgs(**arguments)
                return await self._get_photos_by_earth_date(args.rover, args.earth_date, args.camera)
            elif tool_name == "get_photos_by_sol":
                args = RoverSolArgs(**arguments)
                return await self._get_photos_by_sol(args.rover, args.sol, args.camera)
            elif tool_name == "get_photos_by_camera":
                args = RoverCameraArgs(**arguments)
                return await self._get_photos_by_camera(args.rover, args.camera, args.count)
            elif tool_name == "compare_rovers":
                return await self._compare_rovers()
            else:
                return self._format_error(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            self.logger.error(f"Error in {tool_name}: {str(e)}")
            return self._format_error(f"Tool execution failed: {str(e)}")
    
    async def _get_rover_status(self, rover: str) -> Dict[str, Any]:
        """Get rover status and information."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_rover_info, rover)
            
            rover_info = RoverInfoResponse(**data)
            rover_data = rover_info.rover
            
            # Calculate mission duration
            landing = datetime.strptime(rover_data.landing_date, "%Y-%m-%d")
            if rover_data.status == "active":
                duration_days = (datetime.now() - landing).days
            else:
                max_date = datetime.strptime(rover_data.max_date, "%Y-%m-%d") if rover_data.max_date else landing
                duration_days = (max_date - landing).days
            
            return self._format_success(
                data={
                    "name": rover_data.name,
                    "status": rover_data.status,
                    "landing_date": rover_data.landing_date,
                    "launch_date": rover_data.launch_date,
                    "mission_duration_days": duration_days,
                    "mission_duration_years": round(duration_days / 365.25, 1),
                    "max_sol": rover_data.max_sol,
                    "max_date": rover_data.max_date,
                    "total_photos": rover_data.total_photos,
                    "available_cameras": self.client.ROVERS[rover]["cameras"]
                },
                message=f"{rover_data.name} status: {rover_data.status} - {duration_days} days on Mars"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get status for {rover}: {str(e)}")
    
    async def _get_latest_photos(self, rover: str, count: int = 25) -> Dict[str, Any]:
        """Get latest photos from rover."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_latest_photos, rover, count)
            
            response = LatestPhotosResponse(**data)
            photos = response.latest_photos
            
            if not photos:
                return self._format_success(
                    data={"photos": [], "count": 0},
                    message=f"No recent photos found for {rover}"
                )
            
            # Group by camera
            cameras = {}
            for photo in photos:
                camera_name = photo.camera.name
                if camera_name not in cameras:
                    cameras[camera_name] = []
                cameras[camera_name].append(self._format_photo(photo))
            
            return self._format_success(
                data={
                    "rover": rover,
                    "count": len(photos),
                    "latest_sol": photos[0].sol if photos else None,
                    "latest_earth_date": photos[0].earth_date if photos else None,
                    "photos": [self._format_photo(photo) for photo in photos],
                    "by_camera": cameras
                },
                message=f"Found {len(photos)} latest photos from {rover}"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get latest photos for {rover}: {str(e)}")
    
    async def _get_photos_by_earth_date(self, rover: str, earth_date: str, camera: Optional[str] = None) -> Dict[str, Any]:
        """Get photos by Earth date."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self.client.get_photos_by_earth_date, 
                rover, 
                earth_date, 
                camera
            )
            
            response = MarsRoverResponse(**data)
            photos = response.photos
            
            return self._format_success(
                data={
                    "rover": rover,
                    "earth_date": earth_date,
                    "camera_filter": camera,
                    "count": len(photos),
                    "photos": [self._format_photo(photo) for photo in photos]
                },
                message=f"Found {len(photos)} photos from {rover} on {earth_date}" + 
                        (f" ({camera} camera)" if camera else "")
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get photos for {rover} on {earth_date}: {str(e)}")
    
    async def _get_photos_by_sol(self, rover: str, sol: int, camera: Optional[str] = None) -> Dict[str, Any]:
        """Get photos by Martian sol."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self.client.get_photos_by_sol, 
                rover, 
                sol, 
                camera
            )
            
            response = MarsRoverResponse(**data)
            photos = response.photos
            
            return self._format_success(
                data={
                    "rover": rover,
                    "sol": sol,
                    "camera_filter": camera,
                    "count": len(photos),
                    "photos": [self._format_photo(photo) for photo in photos]
                },
                message=f"Found {len(photos)} photos from {rover} on sol {sol}" + 
                        (f" ({camera} camera)" if camera else "")
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get photos for {rover} on sol {sol}: {str(e)}")
    
    async def _get_photos_by_camera(self, rover: str, camera: str, count: int = 20) -> Dict[str, Any]:
        """Get photos by camera."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self.client.get_photos_by_camera, 
                rover, 
                camera, 
                count
            )
            
            photos = [RoverPhoto(**photo) for photo in data.get("photos", [])]
            
            return self._format_success(
                data={
                    "rover": rover,
                    "camera": camera,
                    "camera_full_name": photos[0].camera.full_name if photos else camera,
                    "count": len(photos),
                    "photos": [self._format_photo(photo) for photo in photos]
                },
                message=f"Found {len(photos)} recent {camera} photos from {rover}"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get {camera} photos for {rover}: {str(e)}")
    
    async def _compare_rovers(self) -> Dict[str, Any]:
        """Compare all rovers."""
        try:
            rover_comparisons = {}
            
            for rover_name in ["curiosity", "opportunity", "spirit"]:
                try:
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, self.client.get_rover_info, rover_name)
                    
                    rover_info = RoverInfoResponse(**data)
                    rover_data = rover_info.rover
                    
                    landing = datetime.strptime(rover_data.landing_date, "%Y-%m-%d")
                    if rover_data.status == "active":
                        duration_days = (datetime.now() - landing).days
                    else:
                        max_date = datetime.strptime(rover_data.max_date, "%Y-%m-%d") if rover_data.max_date else landing
                        duration_days = (max_date - landing).days
                    
                    rover_comparisons[rover_name] = {
                        "name": rover_data.name,
                        "status": rover_data.status,
                        "landing_date": rover_data.landing_date,
                        "mission_duration_days": duration_days,
                        "mission_duration_years": round(duration_days / 365.25, 1),
                        "max_sol": rover_data.max_sol,
                        "total_photos": rover_data.total_photos,
                        "cameras": self.client.ROVERS[rover_name]["cameras"]
                    }
                except Exception as e:
                    rover_comparisons[rover_name] = {"error": str(e)}
            
            # Calculate totals
            total_photos = sum(r.get("total_photos", 0) for r in rover_comparisons.values() if "total_photos" in r)
            active_rovers = [r["name"] for r in rover_comparisons.values() if r.get("status") == "active"]
            
            return self._format_success(
                data={
                    "rovers": rover_comparisons,
                    "summary": {
                        "total_rovers": len(rover_comparisons),
                        "active_rovers": active_rovers,
                        "total_photos_all_rovers": total_photos,
                        "longest_mission": max(
                            (r.get("mission_duration_days", 0) for r in rover_comparisons.values() if "mission_duration_days" in r),
                            default=0
                        )
                    }
                },
                message=f"Mars rover comparison: {len(active_rovers)} active, {total_photos:,} total photos"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to compare rovers: {str(e)}")
    
    def _format_photo(self, photo: RoverPhoto) -> Dict[str, Any]:
        """Format photo for display."""
        return {
            "id": photo.id,
            "sol": photo.sol,
            "earth_date": photo.earth_date,
            "camera": {
                "name": photo.camera.name,
                "full_name": photo.camera.full_name
            },
            "img_src": str(photo.img_src),
            "rover": photo.rover.name
        }