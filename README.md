# NASA Space Explorer Assistant 🚀

**MCP-powered space data access for LLMs - Gradio Agents & MCP Hackathon 2025**

---
tags:
- mcp-server-track
- gradio
- mcp
- nasa
- space
- hackathon-2025
- astronomy
- asteroids
- mars-rover
---

## 🏷️ Hackathon Submission

**Track:** `mcp-server-track`  
**Author:** @Clemente-H
**Hackathon:** Gradio Agents & MCP Hackathon 2025 (June 2-10, 2025)  
**Organization:** Agents-MCP-Hackathon  

This project provides **3 specialized MCP servers** that enable LLMs to access NASA's space data through a standardized protocol.

## 🎥 Demo Video

**🚀 [Link to Demo Video - NASA MCP Server in Action]**

This video demonstrates the NASA Space Explorer MCP Server working with an MCP Client, showcasing:
- All 15 MCP tools in action across 3 NASA APIs
- Cross-MCP queries combining APOD + Asteroids + Mars data
- Real-time space data access through LLM conversation
- Advanced features like asteroid threat analysis and rover comparisons

*Video shows integration with [Claude Desktop/Cursor/Your MCP Client] using the MCP protocol*

## 🌟 Features

### 📡 **3 Specialized MCP Services**
- **🌌 APOD MCP**: Astronomy Picture of the Day (3 tools)
- **🌍 NeoWs MCP**: Near Earth Objects - Asteroids (6 tools)  
- **🔴 Mars Rover MCP**: Photos from Mars rovers (6 tools)

### 🛠️ **15 Total MCP Tools**
```
🌌 APOD Tools:
├── apod_get_apod_today              # Today's astronomy picture
├── apod_get_apod_by_date           # Picture for specific date
└── apod_get_apod_date_range        # Pictures for date range

🌍 NeoWs Tools:
├── neows_get_asteroids_today       # Today's approaching asteroids
├── neows_get_asteroids_week        # This week's asteroids
├── neows_get_asteroids_date_range  # Asteroids for date range
├── neows_get_potentially_hazardous # Only dangerous asteroids
├── neows_get_largest_asteroids_week # Largest asteroids
└── neows_analyze_asteroid_danger   # Detailed threat analysis

🔴 Mars Rover Tools:
├── marsrover_get_rover_status      # Rover mission status
├── marsrover_get_latest_photos     # Most recent photos
├── marsrover_get_photos_by_earth_date # Photos by Earth date
├── marsrover_get_photos_by_sol     # Photos by Martian day
├── marsrover_get_photos_by_camera  # Photos by specific camera
└── marsrover_compare_rovers        # Compare all rovers
```

### 🌟 **Cross-MCP Capabilities**
- **Space Summary**: Combine APOD + asteroids + Mars data for any date
- **Date Correlation**: Find all space events for a specific date
- **Size Comparisons**: Compare asteroid sizes with Mars rover scale
- **Intelligent Analysis**: AI-powered insights across multiple NASA APIs

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/Clemente-H/gradio-hackaton-mcp-nasa
cd gradio-hackaton-mcp-nasa

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your NASA API key and Mistral API key
```

### Run as MCP Server
```bash
# For Hugging Face Spaces, the main file should be app.py
python app.py
```

The application will start:
- **Web Interface**: http://localhost:8000
- **MCP Server**: http://localhost:8000/gradio_api/mcp/sse
- **Chat Interface**: Available with Mistral API key

### Connect MCP Client

**For most MCP Clients (Cursor, Cline, Tiny Agents):**
```json
{
  "mcpServers": {
    "nasa-space-explorer": {
      "url": "https://your-space-name.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

**For Claude Desktop (requires mcp-remote):**
```json
{
  "mcpServers": {
    "nasa-space-explorer": {
      "command": "npx",
      "args": [
        "mcp-remote", 
        "https://your-space-name.hf.space/gradio_api/mcp/sse"
      ]
    }
  }
}
```

## 🏗️ Architecture

```
LLM Client (Claude Desktop, Cursor, etc.)
    ↓ MCP Protocol 2024-11-05
NASA MCP Server (Gradio App)
    ├── Chat Agent (LlamaIndex + Mistral) 
    │   └── Direct MCP Integration
    ├── APOD MCP ──→ NASA APOD API
    ├── NeoWs MCP ──→ NASA Near Earth Objects API  
    └── Mars Rover MCP ──→ NASA Mars Rover Photos API
```

## 🧪 Testing & Validation

All MCPs are thoroughly tested with comprehensive test suites:

```bash
# Test individual MCPs
python tests/test_apod_quick.py      # 4/4 tests ✅
python tests/test_neows_quick.py     # 5/5 tests ✅  
python tests/test_marsrover_quick.py # 6/6 tests ✅

# Test complete MCP server
python app.py  # Interactive testing interface
```

**Total Test Coverage**: 15+ individual tests + integration testing

## 💡 Example Queries

**Natural language queries your LLM can now answer:**

### Single MCP Queries
- *"What's today's astronomy picture?"*
- *"Are there any dangerous asteroids approaching Earth this week?"*
- *"Show me the latest photos from Curiosity rover on Mars"*
- *"Get rover status for all Mars missions"*

### Cross-MCP Magic ✨
- *"What space events happened on July 4th, 2023? Show me the astronomy picture, any asteroids, and Mars rover activity for that date."*
- *"Compare this week's largest asteroid to the size of a Mars rover"*
- *"Give me a complete space summary for today: astronomy highlights, asteroid activity, and Mars discoveries"*
- *"Find correlations between astronomy pictures and asteroid approaches"*

### Advanced Analysis
- *"Analyze the threat level of asteroid 2023 BU and compare it to recent space images"*
- *"How has Curiosity's mission progressed over the years compared to other rovers?"*
- *"Show me space activity patterns: when do we see more asteroids vs more interesting astronomy pictures?"*

## 📊 Technical Highlights

- **✅ Full MCP Protocol**: Complete implementation of MCP 2024-11-05 standard
- **✅ Rate Limiting**: Respects NASA API limits (950 requests/hour with buffer)
- **✅ Error Handling**: Robust retry logic and comprehensive validation
- **✅ Cross-MCP Queries**: Unique capability to combine multiple NASA APIs
- **✅ Production Ready**: Comprehensive testing, logging, and monitoring
- **✅ Chat Integration**: LlamaIndex + Mistral for natural language interaction
- **✅ Real-time Data**: Live access to current space events and discoveries

## 🔧 Configuration

### Required Environment Variables
```bash
# NASA API (required for all features)
NASA_API_KEY=your_nasa_api_key_here  # Get at https://api.nasa.gov/

# Mistral API (optional, for chat features)
MISTRAL_API_KEY=your_mistral_api_key_here  # Get at https://console.mistral.ai/

# Optional settings
DEBUG=false
LOG_LEVEL=INFO
```

### API Rate Limits
- **NASA APIs**: 1000 requests/hour (we use 950 with safety buffer)
- **Mistral API**: Standard rate limits apply
- **Built-in Rate Limiting**: 3.6 seconds between requests

## 🎯 Why This Project Stands Out

### 1. **🔧 Technical Excellence**
- Full MCP protocol implementation with 15 working tools
- Professional architecture with proper separation of concerns
- Comprehensive error handling and retry logic
- Extensive testing suite with 15+ tests

### 2. **🌍 Real-World Impact**
- Access to NASA's incredible space data that people actually want
- Educational value for astronomy enthusiasts and students
- Research applications for space science community
- Real-time access to current space events

### 3. **🎯 Innovation**
- **Cross-MCP queries** that don't exist anywhere else
- Intelligent correlation between different space data sources
- Natural language interface to complex space APIs
- Unique combination of APOD, asteroids, and Mars data

### 4. **📈 Scalability**
- Modular architecture ready for additional space APIs
- Easy to extend with new NASA endpoints
- Professional codebase that others can build upon
- Clear documentation for contributors

### 5. **🚀 User Experience**
- Works with any MCP client (Claude Desktop, Cursor, Cline, etc.)
- Intuitive natural language queries
- Rich, detailed responses with context
- Both technical users and space enthusiasts can use it

## 🔮 Future Enhancements

- **Additional NASA APIs**: Earth Imagery, Exoplanet Archive, Solar System Dynamics
- **Enhanced Analysis**: ML-powered pattern recognition in space data
- **Visualization**: Integration with plotting libraries for data visualization
- **Scheduling**: Automated alerts for significant space events
- **Historical Analysis**: Trend analysis across years of space data

## 📖 Documentation

### Project Structure
```
nasa-space-explorer/
├── app.py                    # Main Gradio app + MCP server
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── src/
│   ├── mcp_server.py        # Main MCP server implementation
│   ├── chat_agent.py        # LlamaIndex chat integration
│   ├── config.py            # Configuration management
│   ├── mcps/               # Individual MCP implementations
│   ├── nasa_api/           # NASA API clients  
│   └── schemas/            # Pydantic schemas
├── tests/                  # Comprehensive test suite
└── docs/                   # Additional documentation
```

### MCP Protocol Details
- **Protocol Version**: 2024-11-05
- **Transport**: Server-Sent Events (SSE)
- **Capabilities**: Tools, Resources, Prompts
- **Tool Discovery**: Automatic via MCP handshake
- **Error Handling**: Standardized error responses

## 🤝 Contributing

This project was created for the Gradio Agents & MCP Hackathon 2025. While the initial implementation is complete, contributions are welcome for future enhancements:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

This project makes use of public NASA APIs available at [https://api.nasa.gov](https://api.nasa.gov).  
While this project uses data provided by NASA, it is **not endorsed or certified by NASA**.

- **NASA** for providing incredible free APIs 
- **Gradio Team** for MCP server capabilities
- **Anthropic** for the MCP protocol
- **Hackathon Organizers** for this amazing event
- **Space Community** for inspiring this project

---

**Built for Gradio Agents & MCP Hackathon 2025** 🚀

**Original Work Created:** June 2-7, 2025  
**Author:** [Tu nombre completo o @tu-username-github]  
**Submission Track:** MCP Server/Tool  
**Organization:** Agents-MCP-Hackathon  
**Repository:** https://github.com/tu-username/nasa-space-explorer

*Making space data accessible to everyone through the power of AI and MCP* ✨