"""
NASA Space Explorer Assistant - MCP Server
Updated with real MCP protocol implementation
"""

import os
import asyncio
import gradio as gr
from dotenv import load_dotenv
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp_server import NASAMCPServer

# Load environment variables
load_dotenv()

# Global MCP server instance
mcp_server = None

async def init_mcp_server():
    """Initialize the MCP server."""
    global mcp_server
    mcp_server = NASAMCPServer()
    await mcp_server.initialize()
    return mcp_server

def create_app():
    """Create and configure the Gradio app with MCP servers."""
    
    # Create Gradio interface
    with gr.Blocks(
        title="NASA Space Explorer Assistant",
        theme=gr.themes.Soft()  # Fixed theme
    ) as app:
        
        gr.Markdown("""
        # 🚀 NASA Space Explorer Assistant
        
        **MCP-powered space data access for LLMs**
        
        This app provides three specialized MCP servers for NASA data:
        - 🌌 **APOD**: Astronomy Picture of the Day (3 tools)
        - 🌍 **NeoWs**: Near Earth Objects - Asteroids (6 tools)
        - 🔴 **Mars Rover**: Photos from Mars rovers (6 tools)
        
        **Total: 15 MCP tools ready for LLM clients!**
        """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🛠️ MCP Server Status")
                
                # Server status component
                status_button = gr.Button("🔄 Check Server Status", variant="secondary")
                status_output = gr.JSON(label="Server Status")
                
                async def check_status():
                    if mcp_server:
                        return await mcp_server.get_server_status()
                    else:
                        return {"error": "MCP server not initialized"}
                
                status_button.click(
                    lambda: asyncio.run(check_status()),
                    outputs=[status_output]
                )
            
            with gr.Column():
                gr.Markdown("### 📡 MCP Connection Info")
                gr.Markdown("""
                **For LLM Clients:**
                
                Connect to this MCP server using:
                - **Protocol**: MCP 2024-11-05
                - **Tools**: 15 available across 3 MCPs
                - **Capabilities**: tools, cross-mcp queries
                
                **Available Tool Prefixes:**
                - `apod_*` - Astronomy Picture tools
                - `neows_*` - Asteroid tools  
                - `marsrover_*` - Mars Rover tools
                """)
        
        with gr.Row():
            gr.Markdown("### 🎮 Interactive Testing")
            
            with gr.Column():
                # Tool testing interface
                tool_dropdown = gr.Dropdown(
                    choices=[
                        "apod_get_apod_today",
                        "neows_get_asteroids_today", 
                        "marsrover_get_latest_photos"
                    ],
                    label="Select Tool to Test",
                    value="apod_get_apod_today"
                )
                
                args_input = gr.JSON(
                    label="Tool Arguments (JSON)",
                    value={}
                )
                
                test_button = gr.Button("🧪 Test Tool", variant="primary")
                test_output = gr.JSON(label="Tool Response")
                
                async def test_tool(tool_name, arguments):
                    if mcp_server:
                        return await mcp_server.call_tool(tool_name, arguments)
                    else:
                        return {"error": "MCP server not initialized"}
                
                test_button.click(
                    lambda tool, args: asyncio.run(test_tool(tool, args)),
                    inputs=[tool_dropdown, args_input],
                    outputs=[test_output]
                )
        
        with gr.Row():
            gr.Markdown("### 🌟 Cross-MCP Queries")
            
            with gr.Column():
                cross_query_type = gr.Dropdown(
                    choices=["space_summary", "correlate_date"],
                    label="Cross-MCP Query Type",
                    value="space_summary"
                )
                
                cross_args = gr.JSON(
                    label="Query Arguments",
                    value={"date": "2024-01-01"}
                )
                
                cross_button = gr.Button("🚀 Execute Cross-MCP Query", variant="primary")
                cross_output = gr.JSON(label="Cross-MCP Response")
                
                async def test_cross_query(query_type, arguments):
                    if mcp_server:
                        return await mcp_server.handle_cross_mcp_query(query_type, arguments)
                    else:
                        return {"error": "MCP server not initialized"}
                
                cross_button.click(
                    lambda query, args: asyncio.run(test_cross_query(query, args)),
                    inputs=[cross_query_type, cross_args],
                    outputs=[cross_output]
                )
        
        gr.Markdown("""
        ### 🎥 Demo Examples for LLM Clients
        
        Try these natural language queries with your MCP client:
        
        1. **Single MCP**: "What's today's astronomy picture?"
        2. **Cross-MCP**: "Give me a space summary for today"
        3. **Complex**: "What asteroids were near Earth when the astronomy picture was taken on January 1st, 2024?"
        4. **Mars Focus**: "Show me recent photos from Curiosity's MAST camera"
        5. **Analysis**: "Compare the sizes of this week's largest asteroids"
        """)
    
    return app

async def main():
    """Main application entry point."""
    # Validate NASA API key
    api_key = os.getenv("NASA_API_KEY")
    if not api_key:
        print("⚠️  Warning: NASA_API_KEY not found in .env file")
        print("Using DEMO_KEY (limited to 30 requests/hour)")
    
    # Initialize MCP server
    print("🚀 Initializing NASA MCP Server...")
    await init_mcp_server()
    print("✅ MCP Server initialized with 3 MCPs")
    
    # Create and launch Gradio app
    app = create_app()
    
    # Launch app
    print("🌐 Launching Gradio interface...")
    app.launch(
        server_name="0.0.0.0",
        server_port=8000,
        share=True,  # For Hugging Face Spaces
        show_error=True
    )

if __name__ == "__main__":
    asyncio.run(main())