"""Real MCP Server implementation for NASA Space Explorer."""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcps.apod_mcp import APODMCP
from mcps.neows_mcp import NeoWsMCP
from mcps.marsrover_mcp import MarsRoverMCP
from config import Config


class NASAMCPServer:
    """NASA Space Explorer MCP Server implementing the MCP protocol."""
    
    def __init__(self):
        self.logger = logging.getLogger("nasa_mcp_server")
        self.setup_logging()
        
        # Initialize MCPs
        self.apod_mcp = APODMCP()
        self.neows_mcp = NeoWsMCP()
        self.marsrover_mcp = MarsRoverMCP()
        
        # MCP registry
        self.mcps = {
            "apod": self.apod_mcp,
            "neows": self.neows_mcp, 
            "marsrover": self.marsrover_mcp
        }
        
        self.logger.info("NASA MCP Server initialized with 3 MCPs")
    
    def setup_logging(self):
        """Setup logging for the server."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def initialize(self) -> Dict[str, Any]:
        """MCP Server initialization handshake."""
        tools = []
        
        # Collect all tools from all MCPs
        for mcp_name, mcp in self.mcps.items():
            mcp_tools = mcp.get_tools()
            # Prefix tool names with MCP name to avoid conflicts
            for tool in mcp_tools:
                tool["name"] = f"{mcp_name}_{tool['name']}"
                tool["mcp_source"] = mcp_name
                tools.append(tool)
        
        self.logger.info(f"Server initialized with {len(tools)} total tools")
        
        return {
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "server_info": {
                "name": "nasa-space-explorer",
                "version": "1.0.0",
                "description": "NASA Space Explorer MCP Server providing access to APOD, NeoWs, and Mars Rover data"
            },
            "tools": tools
        }
    
    async def list_tools(self) -> Dict[str, Any]:
        """List all available tools across MCPs."""
        tools = []
        
        for mcp_name, mcp in self.mcps.items():
            mcp_tools = mcp.get_tools()
            for tool in mcp_tools:
                tool["name"] = f"{mcp_name}_{tool['name']}"
                tool["mcp_source"] = mcp_name
                tools.append(tool)
        
        return {
            "tools": tools
        }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call, routing to the appropriate MCP."""
        try:
            # Parse MCP name from tool name
            if "_" not in tool_name:
                return self._format_error(f"Invalid tool name format: {tool_name}")
            
            mcp_name, actual_tool_name = tool_name.split("_", 1)
            
            if mcp_name not in self.mcps:
                return self._format_error(f"Unknown MCP: {mcp_name}")
            
            mcp = self.mcps[mcp_name]
            
            self.logger.info(f"Calling {mcp_name}.{actual_tool_name} with args: {arguments}")
            
            # Call the MCP tool
            result = await mcp.call_tool(actual_tool_name, arguments)
            
            # Add metadata
            result["_metadata"] = {
                "mcp_source": mcp_name,
                "tool_name": actual_tool_name,
                "timestamp": datetime.now().isoformat(),
                "server": "nasa-space-explorer"
            }
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return self._format_error(f"Tool execution failed: {str(e)}")
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get server status and statistics."""
        try:
            # Test each MCP
            mcp_status = {}
            total_tools = 0
            
            for mcp_name, mcp in self.mcps.items():
                try:
                    tools = mcp.get_tools()
                    mcp_status[mcp_name] = {
                        "status": "healthy",
                        "tools_count": len(tools),
                        "description": mcp.description
                    }
                    total_tools += len(tools)
                except Exception as e:
                    mcp_status[mcp_name] = {
                        "status": "error",
                        "error": str(e),
                        "tools_count": 0
                    }
            
            return {
                "server_status": "running",
                "total_mcps": len(self.mcps),
                "total_tools": total_tools,
                "nasa_api_key": "configured" if Config.NASA_API_KEY != "DEMO_KEY" else "demo",
                "mcps": mcp_status,
                "uptime": "N/A",  # Would implement with server start time
                "last_check": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "server_status": "error", 
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    async def handle_cross_mcp_query(self, query_type: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complex queries that span multiple MCPs."""
        try:
            if query_type == "space_summary":
                return await self._space_summary(arguments)
            elif query_type == "correlate_date":
                return await self._correlate_by_date(arguments)
            elif query_type == "size_comparison":
                return await self._size_comparison(arguments)
            else:
                return self._format_error(f"Unknown cross-MCP query: {query_type}")
        
        except Exception as e:
            return self._format_error(f"Cross-MCP query failed: {str(e)}")
    
    async def _space_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive space summary."""
        try:
            date = arguments.get("date", datetime.now().strftime("%Y-%m-%d"))
            
            # Get APOD for the date
            apod_result = await self.apod_mcp.call_tool("get_apod_by_date", {"date": date})
            
            # Get asteroids for the week
            asteroids_result = await self.neows_mcp.call_tool("get_asteroids_week", {})
            
            # Get latest Mars photos
            mars_result = await self.marsrover_mcp.call_tool("get_latest_photos", {
                "rover": "curiosity", 
                "count": 5
            })
            
            summary = {
                "date": date,
                "astronomy_highlight": apod_result.get("data", {}) if apod_result.get("success") else None,
                "asteroid_activity": {
                    "total_this_week": asteroids_result.get("data", {}).get("total_count", 0),
                    "hazardous_count": asteroids_result.get("data", {}).get("hazardous_count", 0)
                } if asteroids_result.get("success") else None,
                "mars_exploration": {
                    "latest_photos": len(mars_result.get("data", {}).get("photos", [])),
                    "latest_sol": mars_result.get("data", {}).get("latest_sol"),
                    "rover_status": "active"
                } if mars_result.get("success") else None
            }
            
            return self._format_success(
                summary,
                f"Space summary for {date} compiled from APOD, NeoWs, and Mars Rover data"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to generate space summary: {str(e)}")
    
    async def _correlate_by_date(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate space events by date."""
        try:
            date = arguments.get("date")
            if not date:
                return self._format_error("Date parameter required")
            
            # Get APOD for that date
            apod_result = await self.apod_mcp.call_tool("get_apod_by_date", {"date": date})
            
            # Get asteroids for that date
            asteroids_result = await self.neows_mcp.call_tool("get_asteroids_date_range", {
                "start_date": date,
                "end_date": date
            })
            
            # Get Mars photos for that date
            mars_result = await self.marsrover_mcp.call_tool("get_photos_by_earth_date", {
                "rover": "curiosity",
                "earth_date": date
            })
            
            correlation = {
                "date": date,
                "apod": apod_result.get("data") if apod_result.get("success") else None,
                "asteroids": asteroids_result.get("data") if asteroids_result.get("success") else None,
                "mars_photos": mars_result.get("data") if mars_result.get("success") else None,
                "correlation_insights": self._generate_insights(apod_result, asteroids_result, mars_result)
            }
            
            return self._format_success(
                correlation,
                f"Correlated space data for {date}"
            )
        
        except Exception as e:
            return self._format_error(f"Failed to correlate data: {str(e)}")
    
    def _generate_insights(self, apod_result, asteroids_result, mars_result) -> List[str]:
        """Generate insights from correlated data."""
        insights = []
        
        if apod_result.get("success") and asteroids_result.get("success"):
            apod_title = apod_result.get("data", {}).get("title", "")
            asteroid_count = asteroids_result.get("data", {}).get("total_count", 0)
            
            if asteroid_count > 0:
                insights.append(f"On this date, {asteroid_count} asteroids approached Earth while the astronomy picture featured: {apod_title}")
        
        if mars_result.get("success"):
            mars_photos = len(mars_result.get("data", {}).get("photos", []))
            if mars_photos > 0:
                insights.append(f"Curiosity rover captured {mars_photos} photos on this Earth date")
        
        return insights
    
    def _format_error(self, error: str) -> Dict[str, Any]:
        """Format error response."""
        return {
            "success": False,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_success(self, data: Any, message: str = None) -> Dict[str, Any]:
        """Format success response."""
        response = {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        if message:
            response["message"] = message
        return response