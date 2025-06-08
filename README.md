---
title: Nasa Space Explorer
emoji: 🚀
colorFrom: indigo
colorTo: gray
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
license: mit
short_description: 'NASA MCP server: APOD images, asteroid tracking, Mars rover'
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
# NASA Space Explorer Assistant 🚀

**MCP-powered space data access for LLMs - Gradio Agents & MCP Hackathon 2025**

## 🏷️ Hackathon Submission

**Track:** `mcp-server-track`  

**Author:** @Clemente-H

**Hackathon:** Gradio Agents & MCP Hackathon 2025 (June 2-10, 2025)

**Organization:** Agents-MCP-Hackathon  

This project implements a **custom MCP server** with advanced NASA space data integration, featuring unique cross-API correlations and natural language access through an integrated chat interface.

## 🚀 Live Demo

**Try it now:** https://huggingface.co/spaces/Agents-MCP-Hackathon/nasa-space-explorer


## 🎥 Demo Video

**🚀 [Link to Demo Video - NASA MCP Server in Action]**

This video demonstrates the NASA Space Explorer MCP implementation showcasing:
- Custom MCP server architecture with 15 specialized NASA tools
- Unique cross-MCP queries combining APOD + Asteroids + Mars data
- Natural language interface through integrated chat (MCP client)
- Interactive testing dashboard for all NASA tools

*Demonstrates advanced MCP architecture with capabilities beyond standard implementations*

## 🌟 Features

### 🏗️ **Custom MCP Architecture**
- **🌌 APOD MCP**: Astronomy Picture of the Day (3 tools)
- **🌍 NeoWs MCP**: Near Earth Objects - Asteroids (6 tools)  
- **🔴 Mars Rover MCP**: Photos from Mars rovers (6 tools)
- **🔮 Cross-MCP Engine**: Advanced correlation queries (unique capability)

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
- **Natural Language Access**: Chat interface using LlamaIndex + Mistral integration

## 🚀 Quick Start

### Interactive Demo
Visit the live Space and explore:

1. **🤖 Chat with NASA Assistant**
   - Ask natural language questions about space
   - AI automatically uses appropriate NASA tools
   - Get comprehensive answers with live data

2. **🛠️ MCP Server Dashboard** 
   - Test individual NASA tools interactively
   - See real-time tool execution and responses
   - Monitor server status and performance

3. **🌟 Cross-MCP Queries**
   - Advanced correlations across multiple NASA APIs
   - Date-based space event summaries
   - Unique insights not available elsewhere

4. **📚 Complete Documentation**
   - Technical architecture details
   - Example queries and use cases


### Local Development
```bash
# Clone repository
git clone https://github.com/Clemente-H/gradio-hackaton-mcp-nasa
cd gradio-hackaton-mcp-nasa
# Install dependencies
pip install -r requirements.txt
# Setup environment variables
cp .env.example .env
# Add your NASA_API_KEY and MISTRAL_API_KEY
# Run the application
python app.py
```

## 🏗️ Architecture

```
🌐 User Interface (Gradio)
    ↓
🤖 Chat Agent (LlamaIndex + Mistral) ← MCP Client
    ↓
🛠️ Custom NASA MCP Server (Advanced Implementation)
    ├── 🌌 APOD MCP ──→ NASA APOD API
    ├── 🌍 NeoWs MCP ──→ NASA Asteroids API
    └── 🔴 Mars Rover MCP ──→ NASA Mars Rover API
```

**Key Innovation:** The integrated chat acts as an intelligent MCP client, automatically selecting and combining the appropriate NASA tools based on user queries.

## 🧪 Comprehensive Testing

Production-ready implementation with extensive testing:

```bash
# Individual MCP testing
python tests/test_apod_quick.py      # 4/4 tests ✅
python tests/test_neows_quick.py     # 5/5 tests ✅  
python tests/test_marsrover_quick.py # 6/6 tests ✅
# Integration testing
python app.py  # Interactive testing dashboard
```

**Test Coverage:** 15+ individual tool tests + integration testing + error handling validation

## 💡 Example Interactions

### Natural Language Queries
*Ask the chat interface these questions and watch it automatically use the right NASA tools:*

**Single API Queries:**
- *"What's today's astronomy picture?"*
- *"Are there any dangerous asteroids approaching Earth this week?"*
- *"Show me the latest photos from Curiosity rover on Mars"*
- *"Compare the mission statistics of all Mars rovers"*

**Cross-API Magic ✨ (Unique Feature):**
- *"What space events happened on July 4th, 2023? Show me the astronomy picture, any asteroids, and Mars rover activity for that date."*
- *"Compare this week's largest asteroid to the size of a Mars rover"*
- *"Give me a complete space summary for today: astronomy highlights, asteroid activity, and Mars discoveries"*
- *"Find correlations between interesting astronomy pictures and asteroid approaches"*

**Advanced Analysis:**
- *"Analyze the threat level of asteroid 2023 BU and tell me if any cool space images were taken that day"*
- *"How has Curiosity's mission progressed compared to when the most spectacular nebula photos were taken?"*
- *"Show me patterns: when do we see more asteroids vs more interesting deep space images?"*

## 📊 Technical Implementation Highlights

### **🔧 Advanced MCP Architecture**
- **Custom Protocol Implementation**: Full MCP 2024-11-05 compliance with extensions
- **Tool Discovery**: Dynamic registration and discovery of all 15 NASA tools
- **Cross-MCP Engine**: Unique capability to correlate data across multiple APIs
- **Error Handling**: Production-grade retry logic with exponential backoff

### **🤖 Intelligent Agent Integration**
- **LlamaIndex Framework**: Advanced tool selection and response synthesis
- **Mistral Large Model**: Natural language understanding and generation
- **Automatic Tool Selection**: AI chooses appropriate NASA tools based on queries
- **Context Awareness**: Maintains conversation context across multiple tool calls

### **🌐 Production Features**
- **Rate Limiting**: Intelligent request pacing (950 requests/hour with buffer)
- **Comprehensive Logging**: Full request/response tracking and debugging
- **Schema Validation**: Pydantic models for all NASA API responses
- **Async Architecture**: Non-blocking operations for better performance

### **🚀 NASA API Integration**
- **APOD API**: Complete access to Astronomy Picture archive
- **NeoWs API**: Real-time asteroid tracking and threat analysis
- **Mars Rover API**: Photos and mission data from Curiosity, Opportunity, Spirit
- **Live Data**: Always current information from NASA's active missions

## 🎯 Why This Implementation Stands Out

### **1. 🌟 Unique Innovation**
- **Cross-MCP Queries**: Only implementation that correlates multiple NASA APIs
- **Date-Based Correlations**: Find all space events for any specific date
- **Intelligent Analysis**: AI-powered insights across different data sources
- **Natural Language Interface**: No need to learn API specifics

### **2. 🔧 Technical Excellence**
- **Advanced Architecture**: Goes far beyond standard MCP implementations  
- **Custom Protocol Extensions**: Cross-API correlation capabilities
- **Production Quality**: Comprehensive error handling, testing, and monitoring
- **Scalable Design**: Easy to extend with additional NASA APIs

### **3. 🌍 Real-World Value**
- **Live NASA Data**: Access to current space missions and discoveries
- **Educational Impact**: Perfect for students, educators, and space enthusiasts
- **Research Applications**: Valuable for space science community
- **Instant Access**: No API setup required for end users

### **4. 🎨 User Experience**
- **Multiple Interfaces**: Chat, dashboard testing, and cross-API queries
- **Rich Responses**: Detailed explanations with context and insights
- **Error Resilience**: Graceful handling of API failures and edge cases
- **Accessible Design**: Works for both technical and non-technical users

### **5. 📈 Professional Quality**
- **Clean Architecture**: Proper separation of concerns and modularity
- **Comprehensive Documentation**: Clear guides for users and developers
- **Extensive Testing**: Ensures reliability and handles edge cases
- **Open Source**: Available for community contributions and extensions

## 🔧 Configuration

### Environment Variables
```bash
# Required
NASA_API_KEY=your_nasa_api_key_here    # Get free at https://api.nasa.gov/
MISTRAL_API_KEY=your_mistral_key_here  # Get at https://console.mistral.ai/
# Optional
DEBUG=false
LOG_LEVEL=INFO
```

### NASA API Details
- **Rate Limits**: 1000 requests/hour (we use 950 with safety buffer)
- **Endpoints**: APOD, NeoWs, Mars Rover Photos
- **Data Coverage**: Real-time space events, historical archive access
- **Update Frequency**: Live data from ongoing NASA missions

## 🔮 Future Enhancements

### **Immediate Extensions**
- **Additional NASA APIs**: Earth Imagery, Exoplanet Archive, Solar System Dynamics
- **Enhanced Visualizations**: Interactive plots and 3D models
- **External MCP Endpoint**: Standard endpoint for other MCP clients
- **Mobile Optimization**: Responsive design improvements

### **Advanced Features**
- **Machine Learning**: Pattern recognition in space data
- **Notification System**: Alerts for significant space events
- **Historical Analysis**: Trend analysis across years of space data
- **API Expansion**: Integration with other space agencies (ESA, JAXA)

## 📖 Project Structure

```
nasa-space-explorer/
├── app.py                    # Main Gradio application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── src/
│   ├── mcp_server.py        # Custom MCP server implementation
│   ├── chat_agent.py        # LlamaIndex + Mistral integration
│   ├── config.py            # Configuration management
│   ├── mcps/               # Individual MCP implementations
│   │   ├── apod_mcp.py     # APOD tools
│   │   ├── neows_mcp.py    # Asteroid tools
│   │   └── marsrover_mcp.py # Mars rover tools
│   ├── nasa_api/           # NASA API clients
│   └── schemas/            # Pydantic validation schemas
├── tests/                  # Comprehensive test suite
└── docs/                   # Additional documentation
```

## 🤝 Contributing

This project was created for the Gradio Agents & MCP Hackathon 2025. The core implementation is complete and production-ready. Future contributions are welcome:

1. **Fork** the repository
2. **Create** a feature branch  
3. **Add** comprehensive tests for new features
4. **Submit** a pull request with clear documentation

## 📄 License

MIT License - See LICENSE file for complete terms

## 🙏 Acknowledgments

This project uses public NASA APIs available at https://api.nasa.gov.  
*While this project uses NASA data, it is not endorsed or certified by NASA.*

**Special Thanks:**
- **NASA** for providing incredible free APIs and inspiring space exploration
- **Gradio Team** for the excellent framework that made this possible
- **Anthropic** for the MCP protocol that inspired this advanced architecture  
- **Hackathon Organizers** for creating this amazing opportunity
- **Space Community** for the passion that drives projects like this

---

**🏆 Built for Gradio Agents & MCP Hackathon 2025** 🚀

**Created:** June 2-7, 2025  
**Author:** @Clemente-H on github. @ClementeH on HuggingFace
**Track:** MCP Server/Tool  
**Organization:** Agents-MCP-Hackathon  
**Repository:** https://github.com/Clemente-H/gradio-hackaton-mcp-nasa

*Making the universe accessible through advanced MCP architecture and AI* ✨
