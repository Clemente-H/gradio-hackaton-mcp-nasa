"""Base MCP class with common functionality."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import json
import logging

class BaseMCP(ABC):
    """Base class for all MCP implementations."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"mcp.{name}")
        
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools for this MCP."""
        pass
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        pass
    
    def initialize(self) -> Dict[str, Any]:
        """MCP initialization handshake."""
        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0",
            "tools": self.get_tools()
        }
    
    def _format_error(self, error: str, details: str = None) -> Dict[str, Any]:
        """Format error response."""
        response = {
            "error": error,
            "success": False
        }
        if details:
            response["details"] = details
        return response
    
    def _format_success(self, data: Any, message: str = None) -> Dict[str, Any]:
        """Format success response."""
        response = {
            "success": True,
            "data": data
        }
        if message:
            response["message"] = message
        return response