"""LlamaIndex chat agent using direct MCP integration."""

import asyncio
import os
from typing import List, Dict, Any, AsyncGenerator
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.mistralai import MistralAI
from llama_index.core.tools import FunctionTool
from pydantic import BaseModel

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from mcp_server import NASAMCPServer


class NASAChatAgent:
    """NASA Space Explorer chat agent using LlamaIndex with direct MCP integration."""
    
    def __init__(self, mcp_server: NASAMCPServer = None):
        self.mcp_server = mcp_server
        self.agent = None
        self.tools = []
        
        # Configure Mistral LLM
        self.llm = MistralAI(
            api_key=Config.MISTRAL_API_KEY,
            model=Config.MISTRAL_MODEL,
            temperature=0.7,
            max_tokens=2000
        )
        
        self.system_prompt = """You are NASA Space Explorer Assistant, an expert on space data and astronomy.

You have access to NASA's APIs through specialized tools:
- APOD tools (apod_*): For Astronomy Picture of the Day data
- NeoWs tools (neows_*): For asteroid and Near Earth Object information  
- Mars Rover tools (marsrover_*): For Mars rover photos and mission data

Your capabilities include:
1. **Single queries**: Answer questions about space images, asteroids, or Mars missions
2. **Cross-correlations**: Connect data across different NASA sources
3. **Analysis**: Provide insights about asteroid dangers, rover discoveries, space events
4. **Education**: Explain space concepts in an engaging, accessible way

When users ask questions:
- Use the most appropriate tools for their query
- Combine multiple tools when it adds value
- Provide rich, detailed responses with context
- Be enthusiastic about space exploration!"""
    
    async def initialize(self) -> bool:
        """Initialize the agent with MCP tools through direct integration."""
        try:
            print("🔄 Initializing chat agent with direct MCP integration...")
            
            # Initialize MCP server if not provided
            if not self.mcp_server:
                self.mcp_server = NASAMCPServer()
                await self.mcp_server.initialize()
            
            # Get tools from MCP server
            tools_response = await self.mcp_server.list_tools()
            mcp_tools = tools_response.get("tools", [])
            
            print(f"📋 Found {len(mcp_tools)} MCP tools")
            
            # Convert MCP tools to LlamaIndex FunctionTools
            self.tools = []
            for tool_def in mcp_tools:
                function_tool = self._create_function_tool(tool_def)
                if function_tool:
                    self.tools.append(function_tool)
            
            print(f"✅ Converted {len(self.tools)} tools for LlamaIndex")
            
            # Debug: Print tool names
            if Config.DEBUG:
                print("Available tools:")
                for tool in self.tools:
                    print(f"  - {tool.metadata.name}")
            
            # Create the agent
            self.agent = FunctionAgent(
                name="NASA Space Explorer",
                description="Expert assistant for NASA space data and astronomy",
                llm=self.llm,
                tools=self.tools,
                system_prompt=self.system_prompt,
                verbose=Config.DEBUG
            )
            
            print("✅ Agent initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return False
    
    def _create_function_tool(self, tool_def: Dict[str, Any]) -> FunctionTool:
        """Convert MCP tool definition to LlamaIndex FunctionTool."""
        try:
            tool_name = tool_def["name"]
            tool_description = tool_def["description"]
            tool_parameters = tool_def.get("parameters", {})
            
            # Create a wrapper function that calls the MCP tool
            async def tool_wrapper(**kwargs):
                """Wrapper function for MCP tool execution."""
                result = await self.mcp_server.call_tool(tool_name, kwargs)
                
                # Format the response for LLM consumption
                if result.get("success"):
                    data = result.get("data", {})
                    message = result.get("message", "")
                    
                    # Convert data to string format for LLM
                    if isinstance(data, dict):
                        # Format key information
                        if "asteroids" in data:
                            return self._format_asteroid_response(data, message)
                        elif "photos" in data:
                            return self._format_photos_response(data, message)
                        elif "title" in data and "explanation" in data:
                            return self._format_apod_response(data, message)
                        else:
                            return f"{message}\n\nData: {data}"
                    elif isinstance(data, list):
                        return f"{message}\n\nFound {len(data)} items"
                    else:
                        return f"{message}\n\n{data}"
                else:
                    error = result.get("error", "Unknown error")
                    return f"Error: {error}"
            
            # Create function tool
            return FunctionTool.from_defaults(
                fn=tool_wrapper,
                name=tool_name,
                description=tool_description,
                fn_schema=self._create_tool_schema(tool_parameters)
            )
            
        except Exception as e:
            print(f"Error creating tool {tool_def.get('name', 'unknown')}: {str(e)}")
            return None
    
    def _create_tool_schema(self, parameters: Dict[str, Any]) -> type[BaseModel]:
        """Create Pydantic schema from MCP tool parameters."""
        # Extract properties and required fields
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])
        
        # Create field definitions using annotations
        annotations = {}
        defaults = {}
        
        for field_name, field_def in properties.items():
            # Map JSON schema types to Python types
            json_type = field_def.get("type", "string")
            if json_type == "integer":
                field_type = int
            elif json_type == "number":
                field_type = float
            elif json_type == "boolean":
                field_type = bool
            elif json_type == "array":
                field_type = List[str]
            else:
                field_type = str
            
            # Make optional if not required
            if field_name not in required:
                from typing import Optional
                field_type = Optional[field_type]
                # Set default value for optional fields
                defaults[field_name] = None
            
            # Add to annotations
            annotations[field_name] = field_type
        
        # Create namespace for the dynamic class
        from pydantic import Field
        namespace = {
            "__annotations__": annotations,
            **defaults  # Add default values
        }
        
        # Create dynamic Pydantic model
        return type("ToolSchema", (BaseModel,), namespace)
    
    def _format_asteroid_response(self, data: Dict, message: str) -> str:
        """Format asteroid data for LLM consumption."""
        parts = [message]
        
        if "total_count" in data:
            parts.append(f"\nTotal asteroids: {data['total_count']}")
        if "hazardous_count" in data:
            parts.append(f"Potentially hazardous: {data['hazardous_count']}")
        
        if "asteroids" in data and data["asteroids"]:
            parts.append("\nTop asteroids:")
            for i, ast in enumerate(data["asteroids"][:5]):
                name = ast.get("name", "Unknown")
                hazardous = "⚠️ HAZARDOUS" if ast.get("is_hazardous") else "✅ Safe"
                parts.append(f"{i+1}. {name} - {hazardous}")
                
                if "diameter_km" in ast:
                    size = ast["diameter_km"].get("max", 0)
                    parts.append(f"   Size: ~{size:.3f} km")
                
                if "closest_approach" in ast:
                    approach = ast["closest_approach"]
                    date = approach.get("date", "Unknown")
                    distance = approach.get("distance_km", 0)
                    parts.append(f"   Closest approach: {date} at {distance:,.0f} km")
        
        return "\n".join(parts)
    
    def _format_photos_response(self, data: Dict, message: str) -> str:
        """Format Mars rover photos for LLM consumption."""
        parts = [message]
        
        if "rover" in data:
            parts.append(f"\nRover: {data['rover']}")
        if "count" in data:
            parts.append(f"Photos found: {data['count']}")
        if "latest_sol" in data:
            parts.append(f"Latest Martian day (sol): {data['latest_sol']}")
        if "latest_earth_date" in data:
            parts.append(f"Latest Earth date: {data['latest_earth_date']}")
        
        if "photos" in data and data["photos"]:
            parts.append("\nSample photos:")
            for i, photo in enumerate(data["photos"][:3]):
                camera = photo.get("camera", {}).get("full_name", "Unknown camera")
                earth_date = photo.get("earth_date", "Unknown date")
                parts.append(f"{i+1}. {camera} - {earth_date}")
                parts.append(f"   URL: {photo.get('img_src', 'N/A')}")
        
        return "\n".join(parts)
    
    def _format_apod_response(self, data: Dict, message: str) -> str:
        """Format APOD data for LLM consumption."""
        parts = [message]
        
        parts.append(f"\nTitle: {data.get('title', 'Unknown')}")
        parts.append(f"Date: {data.get('date', 'Unknown')}")
        parts.append(f"Media type: {data.get('media_type', 'Unknown')}")
        
        if "copyright" in data:
            parts.append(f"Copyright: {data['copyright']}")
        
        parts.append(f"\nExplanation: {data.get('explanation', 'No explanation available')}")
        parts.append(f"\nURL: {data.get('url', 'N/A')}")
        
        if "hdurl" in data:
            parts.append(f"HD URL: {data['hdurl']}")
        
        return "\n".join(parts)
    
    async def chat(self, message: str) -> str:
        """Chat with the agent."""
        if not self.agent:
            return "❌ Agent not initialized. Please check configuration."
        
        try:
            # FunctionAgent uses run() method, not arun()
            response = await self.agent.run(message)
            return str(response)
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            if Config.DEBUG:
                import traceback
                traceback.print_exc()
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    def get_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available tools."""
        if not self.tools:
            return []
        
        return [
            {
                "name": tool.metadata.name,
                "description": tool.metadata.description
            }
            for tool in self.tools
        ]