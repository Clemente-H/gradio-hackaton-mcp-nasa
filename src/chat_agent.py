"""LlamaIndex chat agent using our MCP server."""

import asyncio
import os
from typing import List, Dict, Any, AsyncGenerator
from llama_index.tools.mcp import get_tools_from_mcp_url
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class NASAChatAgent:
    """NASA Space Explorer chat agent using LlamaIndex + MCP."""
    
    def __init__(self, mcp_server_url: str = "http://127.0.0.1:8000/sse"):
        self.mcp_server_url = mcp_server_url
        self.agent = None
        self.tools = []
        
        # Configure Mistral LLM with OpenAI-compatible API
        self.llm = OpenAI(
            api_key=Config.MISTRAL_API_KEY,
            api_base=Config.MISTRAL_BASE_URL,
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
2. **Cross-correlations**: Connect data across different NASA sources (e.g., "What asteroids were near Earth when this astronomy picture was taken?")
3. **Analysis**: Provide insights about asteroid dangers, rover discoveries, space events
4. **Education**: Explain space concepts in an engaging, accessible way

When users ask questions:
- Use the most appropriate tools for their query
- Combine multiple tools when it adds value
- Provide rich, detailed responses with context
- Include relevant details like dates, sizes, distances
- Be enthusiastic about space exploration!

Remember: You can access real NASA data, so your responses should be current and accurate."""
    
    async def initialize(self) -> bool:
        """Initialize the agent with MCP tools."""
        try:
            print("🔄 Connecting to MCP server...")
            
            # Get tools from our MCP server
            self.tools = await get_tools_from_mcp_url(self.mcp_server_url)
            
            print(f"✅ Connected! Found {len(self.tools)} MCP tools")
            
            # Create the agent
            self.agent = FunctionAgent(
                name="NASA Space Explorer",
                description="Expert assistant for NASA space data and astronomy",
                llm=self.llm,
                tools=self.tools,
                system_prompt=self.system_prompt,
                verbose=Config.DEBUG
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {str(e)}")
            return False
    
    async def chat(self, message: str) -> str:
        """Chat with the agent."""
        if not self.agent:
            return "❌ Agent not initialized. Please check MCP server connection."
        
        try:
            response = await self.agent.arun(message)
            return str(response)
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return f"❌ Sorry, I encountered an error: {str(e)}"
    
    async def stream_chat(self, message: str) -> AsyncGenerator[str, None]:
        """Stream chat response (if supported)."""
        if not self.agent:
            yield "❌ Agent not initialized. Please check MCP server connection."
            return
        
        try:
            # For now, return the full response (streaming would require more setup)
            response = await self.chat(message)
            yield response
        except Exception as e:
            yield f"❌ Sorry, I encountered an error: {str(e)}"
    
    def get_tools_info(self) -> List[Dict[str, Any]]:
        """Get information about available tools."""
        if not self.tools:
            return []
        
        return [
            {
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "parameters": getattr(tool.metadata, 'fn_schema', {})
            }
            for tool in self.tools
        ]
