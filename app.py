"""
NASA Space Explorer Assistant - MCP Server
Gradio Agents & MCP Hackathon 2025
"""

import os
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Gradio app with MCP servers."""
    
    # Create Gradio interface
    with gr.Blocks(
        title="NASA Space Explorer Assistant",
        theme=gr.themes.Soft()
    ) as app:
        
        gr.Markdown("""
        # 🚀 NASA Space Explorer Assistant
        
        **MCP-powered space data access for LLMs**
        
        This app provides three specialized MCP servers for NASA data:
        - 🌌 **APOD**: Astronomy Picture of the Day
        - 🌍 **NeoWs**: Near Earth Objects (Asteroids)
        - 🔴 **Mars Rover**: Photos from Mars rovers
        
        Connect your LLM client to these MCP servers to explore space data!
        """)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🛠️ Available MCP Servers")
                gr.Markdown("""
                - **APOD MCP**: Ready for testing
                - **NeoWs MCP**: Coming next  
                - **Mars Rover MCP**: Coming soon
                """)
            
            with gr.Column():
                gr.Markdown("### 📡 Server Status")
                # API key validation
                api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
                if api_key == "DEMO_KEY":
                    status = "🟡 Using DEMO_KEY (limited requests)"
                else:
                    status = "🟢 Personal API key configured"
                gr.Markdown(status)
        
        gr.Markdown("""
        ### 🎥 Demo Examples
        
        Try these queries with your MCP client:
        
        1. **Single MCP**: "What's today's astronomy picture?"
        2. **Cross-MCP**: "Are there dangerous asteroids this week, and show me recent Mars photos?"
        3. **Complex**: "Give me a space summary: today's astronomy highlight, asteroid activity, and latest Mars discoveries"
        """)
    
    return app

if __name__ == "__main__":
    # Validate NASA API key
    api_key = os.getenv("NASA_API_KEY")
    if not api_key:
        print("⚠️  Warning: NASA_API_KEY not found in .env file")
        print("Using DEMO_KEY (limited to 30 requests/hour)")
    
    # Create and launch app
    app = create_app()
    
    # Launch with MCP server support
    app.launch(
        server_name="0.0.0.0",
        server_port=8000,
        share=True,  # For Hugging Face Spaces
        # mcp_server=True  # Uncomment when MCP support is ready
    )