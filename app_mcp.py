"""
NASA Space Explorer Assistant - Complete MCP Server + Chat Interface
Gradio Agents & MCP Hackathon 2025

Features:
- 3 MCP servers (APOD, NeoWs, Mars Rover) with 15 total tools
- LlamaIndex chat agent with Mistral LLM
- Interactive testing interface
- Cross-MCP query capabilities
"""

import os
import asyncio
import gradio as gr
from dotenv import load_dotenv
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp_server import NASAMCPServer
from src.chat_agent import NASAChatAgent
from src.config import Config

# Load environment variables
load_dotenv()

# Global instances
mcp_server = None
chat_agent = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_servers():
    """Initialize both MCP server and chat agent."""
    global mcp_server, chat_agent
    
    try:
        # Initialize MCP server
        print("🚀 Initializing MCP Server...")
        mcp_server = NASAMCPServer()
        await mcp_server.initialize()
        print("✅ MCP Server initialized with 3 MCPs")
        
        # Initialize chat agent (if Mistral API key available)
        if Config.MISTRAL_API_KEY:
            print("🤖 Initializing Chat Agent...")
            # Pass the MCP server instance directly
            chat_agent = NASAChatAgent(mcp_server=mcp_server)
            success = await chat_agent.initialize()
            if success:
                print("✅ Chat Agent initialized with LlamaIndex + Mistral")
            else:
                print("⚠️ Chat Agent failed to initialize")
                chat_agent = None
        else:
            print("⚠️ MISTRAL_API_KEY not set - chat features disabled")
            chat_agent = None
        
        return mcp_server, chat_agent
    
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        return None, None

def create_app():
    """Create and configure the complete Gradio application."""
    
    with gr.Blocks(
        title="NASA Space Explorer Assistant",
        theme=gr.themes.Soft(),
        css="""
        .chat-container { 
            max-height: 600px; 
            overflow-y: auto; 
        }
        .space-themed { 
            background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%); 
        }
        .example-btn {
            margin: 2px;
        }
        """
    ) as app:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0;">🚀 NASA Space Explorer Assistant</h1>
            <p style="color: #cccccc; margin: 10px 0 0 0;">MCP-powered space data access + AI Chat Assistant</p>
        </div>
        """)
        
        # Status indicator
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📡 System Status")
                api_status = "🟢 NASA API" if Config.NASA_API_KEY != "DEMO_KEY" else "🟡 NASA Demo Key"
                chat_status = "🟢 Chat Ready" if Config.MISTRAL_API_KEY else "🔴 Chat Disabled"
                gr.Markdown(f"**{api_status}** | **{chat_status}**")
            
            with gr.Column(scale=2):
                gr.Markdown("### 🛠️ Available Services")
                gr.Markdown("🌌 **APOD** (3 tools) | 🌍 **NeoWs** (6 tools) | 🔴 **Mars Rover** (6 tools) | **Total: 15 MCP tools**")
        
        with gr.Tabs():
            # =================================
            # TAB 1: CHAT INTERFACE (NEW!)
            # =================================
            with gr.Tab("🤖 Chat with NASA Assistant") as chat_tab:
                if Config.MISTRAL_API_KEY:
                    gr.Markdown("""
                    ### 🌟 Your Personal NASA Space Expert
                    
                    I can access **live NASA data** to answer your questions about space! Try asking me about:
                    """)
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("""
                            **🌌 Astronomy**
                            - Today's space picture
                            - Historical astronomy images
                            - Space phenomena explanations
                            """)
                        with gr.Column():
                            gr.Markdown("""
                            **🌍 Asteroids & NEOs**
                            - Dangerous space rocks
                            - Asteroid size comparisons
                            - Threat analysis
                            """)
                        with gr.Column():
                            gr.Markdown("""
                            **🔴 Mars Exploration**
                            - Rover photos and missions
                            - Mars surface discoveries
                            - Mission statistics
                            """)
                    
                    # Main chat interface
                    chatbot = gr.Chatbot(
                        value=[],
                        elem_classes=["chat-container"],
                        height=500,
                        show_label=False,
                        type="messages"  # Fix the warning
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Ask me anything about space... 🚀",
                            show_label=False,
                            scale=4,
                            container=False
                        )
                        send_btn = gr.Button("Send 🚀", variant="primary", scale=1)
                        clear_btn = gr.Button("Clear 🗑️", variant="secondary", scale=1)
                    
                    # Quick example buttons
                    gr.Markdown("### 🎯 Quick Examples")
                    with gr.Row():
                        example_btn1 = gr.Button("🌌 What's today's astronomy picture?", elem_classes=["example-btn"])
                        example_btn2 = gr.Button("🌍 Any dangerous asteroids this week?", elem_classes=["example-btn"])
                    
                    with gr.Row():
                        example_btn3 = gr.Button("🔴 Show me latest Mars rover photos", elem_classes=["example-btn"])
                        example_btn4 = gr.Button("🌟 Give me today's space summary", elem_classes=["example-btn"])
                    
                    with gr.Row():
                        example_btn5 = gr.Button("📅 What space events happened on January 1, 2024?", elem_classes=["example-btn"])
                        example_btn6 = gr.Button("📏 Compare sizes of this week's largest asteroids", elem_classes=["example-btn"])
                    
                    # Chat functions
                    async def respond(message, history):
                        """Handle chat response."""
                        if not message.strip():
                            return history, ""
                        
                        if not chat_agent:
                            error_msg = "❌ Chat agent not available. Please check Mistral API key configuration."
                            # For messages format: list of dicts with 'role' and 'content'
                            return history + [
                                {"role": "user", "content": message},
                                {"role": "assistant", "content": error_msg}
                            ], ""
                        
                        # Add user message to history
                        history = history + [{"role": "user", "content": message}]
                        
                        # Get AI response
                        try:
                            print(f"🤖 Processing: {message}")
                            response = await chat_agent.chat(message)
                            # Add assistant response
                            history.append({"role": "assistant", "content": response})
                            print(f"✅ Response generated ({len(response)} chars)")
                        except Exception as e:
                            error_response = f"❌ Sorry, I encountered an error: {str(e)}"
                            history.append({"role": "assistant", "content": error_response})
                            print(f"❌ Chat error: {str(e)}")
                        
                        return history, ""
                    
                    def clear_chat():
                        """Clear chat history."""
                        return [], ""
                    
                    def set_example_text(text):
                        """Set example text in input."""
                        return text
                    
                    # Event handlers
                    msg.submit(
                        lambda msg, hist: asyncio.run(respond(msg, hist)),
                        inputs=[msg, chatbot],
                        outputs=[chatbot, msg]
                    )
                    
                    send_btn.click(
                        lambda msg, hist: asyncio.run(respond(msg, hist)),
                        inputs=[msg, chatbot],
                        outputs=[chatbot, msg]
                    )
                    
                    clear_btn.click(clear_chat, outputs=[chatbot, msg])
                    
                    # Example button handlers
                    example_btn1.click(
                        lambda: "What's today's astronomy picture?",
                        outputs=[msg]
                    )
                    example_btn2.click(
                        lambda: "Are there any potentially dangerous asteroids approaching Earth this week?",
                        outputs=[msg]
                    )
                    example_btn3.click(
                        lambda: "Show me the latest photos from Curiosity rover on Mars",
                        outputs=[msg]
                    )
                    example_btn4.click(
                        lambda: "Give me a comprehensive space summary for today",
                        outputs=[msg]
                    )
                    example_btn5.click(
                        lambda: "What space events happened on January 1st, 2024? Show me the astronomy picture, any asteroids, and Mars rover activity for that date.",
                        outputs=[msg]
                    )
                    example_btn6.click(
                        lambda: "What are the largest asteroids approaching Earth this week? Compare their sizes to familiar objects.",
                        outputs=[msg]
                    )
                
                else:
                    # Chat disabled - show setup instructions
                    gr.Markdown("""
                    ### 🔐 Chat Feature Disabled
                    
                    To enable the AI chat assistant, you need to add your Mistral API key:
                    
                    1. **Get API Key**: Visit [console.mistral.ai](https://console.mistral.ai/api-keys)
                    2. **Add to .env file**:
                       ```
                       MISTRAL_API_KEY=your_api_key_here
                       ```
                    3. **Restart the application**
                    
                    The chat assistant will then be able to:
                    - Answer questions about space in natural language
                    - Access all 15 NASA MCP tools automatically
                    - Provide cross-correlations and insights
                    - Generate comprehensive space summaries
                    """)
                    
                    gr.HTML("""
                    <div style="text-align: center; padding: 20px; background: #000000; border-radius: 10px; margin-top: 20px;">
                        <h3>🌟 Preview: What the chat can do</h3>
                        <p><strong>User:</strong> "What's today's astronomy picture?"</p>
                        <p><strong>Assistant:</strong> "Today's Astronomy Picture of the Day is..." <em>[Uses APOD MCP]</em></p>
                        <br>
                        <p><strong>User:</strong> "Are there dangerous asteroids this week?"</p>
                        <p><strong>Assistant:</strong> "Let me check current asteroid data..." <em>[Uses NeoWs MCP]</em></p>
                        <br>
                        <p><strong>User:</strong> "What space events happened on my birthday?"</p>
                        <p><strong>Assistant:</strong> "I'll check astronomy pictures, asteroids, and Mars activity for that date..." <em>[Uses all 3 MCPs]</em></p>
                    </div>
                    """)
            
            # =================================
            # TAB 2: MCP SERVER MANAGEMENT
            # =================================
            with gr.Tab("🛠️ MCP Server Dashboard") as mcp_tab:
                gr.Markdown("### 🔧 MCP Server Status & Management")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### 📊 Server Status")
                        status_button = gr.Button("🔄 Check Server Status", variant="secondary")
                        status_output = gr.JSON(label="Detailed Status")
                        
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
                        gr.Markdown("#### 🔗 Connection Information")
                        gr.Markdown("""
                        **For External MCP Clients:**
                        
                        - **Protocol**: MCP 2024-11-05
                        - **Endpoint**: `http://localhost:8000/sse`
                        - **Tools**: 15 available across 3 MCPs
                        - **Capabilities**: tools, cross-mcp queries
                        
                        **Tool Prefixes:**
                        - `apod_*` - Astronomy Picture tools (3)
                        - `neows_*` - Asteroid tools (6)
                        - `marsrover_*` - Mars Rover tools (6)
                        """)
                
                # Tool testing interface
                gr.Markdown("### 🧪 Interactive Tool Testing")
                
                with gr.Row():
                    with gr.Column():
                        tool_dropdown = gr.Dropdown(
                            choices=[
                                "apod_get_apod_today",
                                "apod_get_apod_by_date",
                                "neows_get_asteroids_today",
                                "neows_get_potentially_hazardous",
                                "marsrover_get_latest_photos",
                                "marsrover_get_rover_status"
                            ],
                            label="Select Tool to Test",
                            value="apod_get_apod_today"
                        )
                        
                        args_input = gr.JSON(
                            label="Tool Arguments (JSON)",
                            value={}
                        )
                        
                        test_button = gr.Button("🧪 Execute Tool", variant="primary")
                    
                    with gr.Column():
                        test_output = gr.JSON(label="Tool Response", height=400)
                
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
                
                # Quick test buttons
                with gr.Row():
                    quick_test1 = gr.Button("🌌 Test APOD Today", size="sm")
                    quick_test2 = gr.Button("🌍 Test Asteroids", size="sm")
                    quick_test3 = gr.Button("🔴 Test Mars Status", size="sm")
                
                quick_test1.click(
                    lambda: ("apod_get_apod_today", {}),
                    outputs=[tool_dropdown, args_input]
                )
                quick_test2.click(
                    lambda: ("neows_get_asteroids_today", {}),
                    outputs=[tool_dropdown, args_input]
                )
                quick_test3.click(
                    lambda: ("marsrover_get_rover_status", {"rover": "curiosity"}),
                    outputs=[tool_dropdown, args_input]
                )
            
            # =================================
            # TAB 3: CROSS-MCP QUERIES
            # =================================
            with gr.Tab("🌟 Cross-MCP Queries") as cross_tab:
                gr.Markdown("### 🚀 Advanced Cross-MCP Capabilities")
                gr.Markdown("These queries combine data from multiple NASA APIs for unique insights:")
                
                with gr.Row():
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
                        
                        # Preset buttons
                        gr.Markdown("#### 🎯 Preset Queries")
                        preset_summary = gr.Button("📊 Today's Space Summary", variant="secondary")
                        preset_correlate = gr.Button("🔍 Correlate Jan 1, 2024", variant="secondary")
                    
                    with gr.Column():
                        cross_output = gr.JSON(label="Cross-MCP Response", height=500)
                
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
                
                preset_summary.click(
                    lambda: ("space_summary", {"date": "2025-06-07"}),
                    outputs=[cross_query_type, cross_args]
                )
                preset_correlate.click(
                    lambda: ("correlate_date", {"date": "2024-01-01"}),
                    outputs=[cross_query_type, cross_args]
                )
            
            # =================================
            # TAB 4: DOCUMENTATION & EXAMPLES
            # =================================
            with gr.Tab("📚 Documentation") as docs_tab:
                gr.Markdown("""
                ### 📖 NASA Space Explorer Documentation
                
                #### 🏗️ Architecture
                ```
                User Interface (Gradio)
                    ↓
                Chat Agent (LlamaIndex + Mistral)
                    ↓
                MCP Server (NASA Space Explorer)
                    ├── APOD MCP ──→ NASA APOD API
                    ├── NeoWs MCP ──→ NASA Asteroids API
                    └── Mars Rover MCP ──→ NASA Mars Rover API
                ```
                
                #### 🛠️ Available MCP Tools
                
                **APOD MCP (3 tools):**
                - `apod_get_apod_today` - Get today's astronomy picture
                - `apod_get_apod_by_date` - Get picture for specific date
                - `apod_get_apod_date_range` - Get pictures for date range
                
                **NeoWs MCP (6 tools):**
                - `neows_get_asteroids_today` - Today's approaching asteroids
                - `neows_get_asteroids_week` - This week's asteroids
                - `neows_get_asteroids_date_range` - Asteroids for date range
                - `neows_get_potentially_hazardous` - Only dangerous asteroids
                - `neows_get_largest_asteroids_week` - Largest asteroids this week
                - `neows_analyze_asteroid_danger` - Detailed threat analysis
                
                **Mars Rover MCP (6 tools):**
                - `marsrover_get_rover_status` - Rover mission status
                - `marsrover_get_latest_photos` - Most recent photos
                - `marsrover_get_photos_by_earth_date` - Photos by Earth date
                - `marsrover_get_photos_by_sol` - Photos by Martian day
                - `marsrover_get_photos_by_camera` - Photos by specific camera
                - `marsrover_compare_rovers` - Compare all rovers
                
                #### 🌟 Cross-MCP Features
                - **Space Summary**: Combine APOD + asteroids + Mars data for any date
                - **Date Correlation**: Find all space events for a specific date
                - **Intelligent Analysis**: AI-powered insights across multiple data sources
                
                #### 💡 Example Conversations
                
                **Simple Queries:**
                - "What's today's astronomy picture?"
                - "Are there dangerous asteroids this week?"
                - "Show me latest Curiosity photos"
                
                **Cross-MCP Queries:**
                - "What space events happened on my birthday?"
                - "Compare asteroid sizes to Mars rover scale"
                - "Give me a complete space summary for July 4th, 2023"
                
                **Advanced Analysis:**
                - "Analyze the threat level of asteroid 2023 BU"
                - "How has Curiosity's mission progressed over the years?"
                - "Correlate astronomy pictures with asteroid activity"
                
                #### ⚙️ Technical Details
                
                **MCP Protocol:** 2024-11-05  
                **Chat LLM:** Mistral Large (via API)  
                **Framework:** LlamaIndex + Gradio  
                **NASA APIs:** APOD, NeoWs, Mars Rover Photos  
                **Rate Limiting:** 950 requests/hour (NASA limit buffer)  
                **Error Handling:** Comprehensive retry logic and validation  
                """)
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; margin-top: 30px; border-top: 1px solid #ddd;">
            <p style="color: #666;">
                🏆 <strong>Built for Gradio Agents & MCP Hackathon 2025</strong> 🚀<br>
                NASA Space Explorer Assistant - Making space data accessible to everyone
            </p>
        </div>
        """)
    
    return app

async def main():
    """Main application entry point."""
    print("🌌 NASA Space Explorer Assistant")
    print("=" * 50)
    
    # Configuration validation
    print("📋 Validating configuration...")
    config_valid = Config.validate()
    
    if Config.NASA_API_KEY == "DEMO_KEY":
        print("ℹ️  Using NASA DEMO_KEY (30 requests/hour limit)")
    else:
        print("✅ NASA API key configured")
    
    if Config.MISTRAL_API_KEY:
        print("✅ Mistral API key configured - chat enabled")
    else:
        print("⚠️  Mistral API key missing - chat disabled")
    
    # Initialize all servers
    print("\n🚀 Initializing services...")
    await init_servers()
    
    # Create and launch application
    print("\n🌐 Creating Gradio interface...")
    app = create_app()
    
    print("🎉 Launch complete!")
    print("=" * 50)
    print("📡 MCP Server: http://localhost:8000")
    print("🤖 Chat Interface: Available if Mistral API key configured")
    print("🛠️  Dashboard: Interactive MCP testing available")
    print("🌟 Cross-MCP: Advanced query capabilities")
    print("=" * 50)
    
    # Launch the application
    app.launch(
        server_name="0.0.0.0",
        server_port=8000,
        share=True,  # Enable sharing for Hugging Face Spaces
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    asyncio.run(main())