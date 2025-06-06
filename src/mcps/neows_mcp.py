"""NeoWs MCP implementation for Near Earth Objects."""

from typing import Dict, List, Any
import asyncio
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_mcp import BaseMCP
from nasa_api.neows_client import NeoWsClient
from schemas.neows_schemas import (
    NeoWsResponse, DateRangeArgs, AsteroidByIdArgs, 
    LargestAsteroidsArgs, AsteroidData
)


class NeoWsMCP(BaseMCP):
    """MCP for NASA Near Earth Object Web Service API."""
    
    def __init__(self):
        super().__init__(
            name="nasa-neows",
            description="Access NASA's Near Earth Object data for asteroids and their threat analysis"
        )
        self.client = NeoWsClient()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return available NeoWs tools."""
        return [
            {
                "name": "get_asteroids_today",
                "description": "Get asteroids approaching Earth today",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_asteroids_week",
                "description": "Get asteroids approaching Earth this week",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_asteroids_date_range",
                "description": "Get asteroids for a specific date range (max 7 days)",
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
            },
            {
                "name": "get_potentially_hazardous",
                "description": "Get only potentially hazardous asteroids for this week",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_largest_asteroids_week",
                "description": "Get the largest asteroids approaching this week",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "integer",
                            "description": "Number of asteroids to return (1-20)",
                            "minimum": 1,
                            "maximum": 20,
                            "default": 5
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "analyze_asteroid_danger",
                "description": "Analyze the danger level of a specific asteroid",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asteroid_id": {
                            "type": "string",
                            "description": "NASA asteroid ID (e.g., '2465633')"
                        }
                    },
                    "required": ["asteroid_id"]
                }
            }
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NeoWs tool."""
        try:
            if tool_name == "get_asteroids_today":
                return await self._get_asteroids_today()
            elif tool_name == "get_asteroids_week":
                return await self._get_asteroids_week()
            elif tool_name == "get_asteroids_date_range":
                args = DateRangeArgs(**arguments)
                return await self._get_asteroids_date_range(args.start_date, args.end_date)
            elif tool_name == "get_potentially_hazardous":
                return await self._get_potentially_hazardous()
            elif tool_name == "get_largest_asteroids_week":
                args = LargestAsteroidsArgs(**arguments)
                return await self._get_largest_asteroids_week(args.count)
            elif tool_name == "analyze_asteroid_danger":
                args = AsteroidByIdArgs(**arguments)
                return await self._analyze_asteroid_danger(args.asteroid_id)
            else:
                return self._format_error(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            self.logger.error(f"Error in {tool_name}: {str(e)}")
            return self._format_error(f"Tool execution failed: {str(e)}")
    
    async def _get_asteroids_today(self) -> Dict[str, Any]:
        """Get asteroids approaching today."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_asteroids_today)
            
            response = NeoWsResponse(**data)
            asteroids = response.get_all_asteroids()
            
            # Format summary
            hazardous_count = len(response.get_potentially_hazardous())
            
            return self._format_success(
                data={
                    "total_count": len(asteroids),
                    "hazardous_count": hazardous_count,
                    "asteroids": [self._format_asteroid_summary(ast) for ast in asteroids]
                },
                message=f"Found {len(asteroids)} asteroids today ({hazardous_count} potentially hazardous)"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get today's asteroids: {str(e)}")
    
    async def _get_asteroids_week(self) -> Dict[str, Any]:
        """Get asteroids approaching this week."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_asteroids_week)
            
            response = NeoWsResponse(**data)
            asteroids = response.get_all_asteroids()
            hazardous = response.get_potentially_hazardous()
            
            return self._format_success(
                data={
                    "total_count": len(asteroids),
                    "hazardous_count": len(hazardous),
                    "asteroids": [self._format_asteroid_summary(ast) for ast in asteroids],
                    "by_date": {
                        date: [self._format_asteroid_summary(ast) for ast in date_asteroids]
                        for date, date_asteroids in response.near_earth_objects.items()
                    }
                },
                message=f"Found {len(asteroids)} asteroids this week ({len(hazardous)} potentially hazardous)"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get this week's asteroids: {str(e)}")
    
    async def _get_asteroids_date_range(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get asteroids for date range."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self.client.get_asteroids_date_range, 
                start_date, 
                end_date
            )
            
            response = NeoWsResponse(**data)
            asteroids = response.get_all_asteroids()
            
            return self._format_success(
                data={
                    "total_count": len(asteroids),
                    "date_range": f"{start_date} to {end_date}",
                    "asteroids": [self._format_asteroid_summary(ast) for ast in asteroids]
                },
                message=f"Found {len(asteroids)} asteroids from {start_date} to {end_date}"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get asteroids for date range: {str(e)}")
    
    async def _get_potentially_hazardous(self) -> Dict[str, Any]:
        """Get only potentially hazardous asteroids."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_asteroids_week)
            
            response = NeoWsResponse(**data)
            hazardous = response.get_potentially_hazardous()
            
            return self._format_success(
                data={
                    "hazardous_count": len(hazardous),
                    "asteroids": [self._format_asteroid_detailed(ast) for ast in hazardous]
                },
                message=f"Found {len(hazardous)} potentially hazardous asteroids this week" if hazardous 
                        else "No potentially hazardous asteroids found this week"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get hazardous asteroids: {str(e)}")
    
    async def _get_largest_asteroids_week(self, count: int = 5) -> Dict[str, Any]:
        """Get largest asteroids this week."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_asteroids_week)
            
            response = NeoWsResponse(**data)
            largest = response.get_largest_asteroids(count)
            
            return self._format_success(
                data={
                    "count": len(largest),
                    "asteroids": [self._format_asteroid_detailed(ast) for ast in largest]
                },
                message=f"Top {len(largest)} largest asteroids this week"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to get largest asteroids: {str(e)}")
    
    async def _analyze_asteroid_danger(self, asteroid_id: str) -> Dict[str, Any]:
        """Analyze danger level of specific asteroid."""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self.client.get_asteroid_by_id, asteroid_id)
            
            asteroid = AsteroidData(**data)
            
            # Analyze danger
            analysis = self._perform_danger_analysis(asteroid)
            
            return self._format_success(
                data={
                    "asteroid": self._format_asteroid_detailed(asteroid),
                    "danger_analysis": analysis
                },
                message=f"Danger analysis for {asteroid.name}: {analysis['threat_level']}"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to analyze asteroid {asteroid_id}: {str(e)}")
    
    def _format_asteroid_summary(self, asteroid: AsteroidData) -> Dict[str, Any]:
        """Format asteroid for summary display."""
        closest_approach = min(asteroid.close_approach_data, 
                             key=lambda x: float(x.miss_distance.kilometers))
        
        return {
            "id": asteroid.id,
            "name": asteroid.name,
            "is_hazardous": asteroid.is_potentially_hazardous_asteroid,
            "diameter_km": {
                "min": asteroid.estimated_diameter.kilometers["estimated_diameter_min"],
                "max": asteroid.estimated_diameter.kilometers["estimated_diameter_max"]
            },
            "closest_approach": {
                "date": closest_approach.close_approach_date,
                "distance_km": float(closest_approach.miss_distance.kilometers),
                "velocity_kmh": float(closest_approach.relative_velocity.kilometers_per_hour)
            }
        }
    
    def _format_asteroid_detailed(self, asteroid: AsteroidData) -> Dict[str, Any]:
        """Format asteroid for detailed display."""
        summary = self._format_asteroid_summary(asteroid)
        
        # Add size comparisons
        max_diameter = asteroid.estimated_diameter.kilometers["estimated_diameter_max"]
        size_comparison = self._get_size_comparison(max_diameter)
        
        summary.update({
            "absolute_magnitude": asteroid.absolute_magnitude_h,
            "nasa_jpl_url": asteroid.nasa_jpl_url,
            "size_comparison": size_comparison,
            "all_approaches": [
                {
                    "date": approach.close_approach_date,
                    "distance_km": float(approach.miss_distance.kilometers),
                    "distance_lunar": float(approach.miss_distance.lunar),
                    "velocity_kmh": float(approach.relative_velocity.kilometers_per_hour)
                }
                for approach in asteroid.close_approach_data
            ]
        })
        
        return summary
    
    def _perform_danger_analysis(self, asteroid: AsteroidData) -> Dict[str, Any]:
        """Perform comprehensive danger analysis."""
        closest_approach = min(asteroid.close_approach_data, 
                             key=lambda x: float(x.miss_distance.kilometers))
        
        distance_km = float(closest_approach.miss_distance.kilometers)
        max_diameter = asteroid.estimated_diameter.kilometers["estimated_diameter_max"]
        
        # Determine threat level
        if asteroid.is_potentially_hazardous_asteroid:
            if distance_km < 1000000:  # Less than 1M km
                threat_level = "HIGH"
            elif distance_km < 5000000:  # Less than 5M km
                threat_level = "MODERATE"
            else:
                threat_level = "LOW"
        else:
            threat_level = "MINIMAL"
        
        # Size category
        if max_diameter > 1.0:
            size_category = "Very Large"
        elif max_diameter > 0.5:
            size_category = "Large"
        elif max_diameter > 0.1:
            size_category = "Medium"
        else:
            size_category = "Small"
        
        return {
            "threat_level": threat_level,
            "is_potentially_hazardous": asteroid.is_potentially_hazardous_asteroid,
            "size_category": size_category,
            "closest_distance_km": distance_km,
            "closest_distance_lunar": float(closest_approach.miss_distance.lunar),
            "impact_potential": "None - will miss Earth safely",
            "monitoring_priority": "High" if threat_level in ["HIGH", "MODERATE"] else "Standard"
        }
    
    def _get_size_comparison(self, diameter_km: float) -> str:
        """Get human-friendly size comparison."""
        diameter_m = diameter_km * 1000
        
        if diameter_m > 1000:
            return f"About {diameter_km:.1f} km - larger than most cities"
        elif diameter_m > 500:
            return f"About {diameter_m:.0f}m - size of a large skyscraper"
        elif diameter_m > 100:
            return f"About {diameter_m:.0f}m - size of a football field"
        elif diameter_m > 50:
            return f"About {diameter_m:.0f}m - size of a large building"
        elif diameter_m > 10:
            return f"About {diameter_m:.0f}m - size of a house"
        else:
            return f"About {diameter_m:.0f}m - size of a car"
