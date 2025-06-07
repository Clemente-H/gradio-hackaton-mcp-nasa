# NASA Space Explorer Assistant 🚀

**MCP-powered space data access for LLMs - Gradio Agents & MCP Hackathon 2025**

## 🏷️ Hackathon Submission

**Track:** `mcp-server-track`

This project provides **3 specialized MCP servers** that enable LLMs to access NASA's space data through a standardized protocol.

## 🌟 Features

### 📡 **3 MCP Services**
- **🌌 APOD MCP**: Astronomy Picture of the Day (3 tools)
- **🌍 NeoWs MCP**: Near Earth Objects - Asteroids (6 tools)  
- **🔴 Mars Rover MCP**: Photos from Mars rovers (6 tools)

### 🛠️ **15 Total MCP Tools**
```
apod_get_apod_today              # Today's astronomy picture
apod_get_apod_by_date           # Picture for specific date
apod_get_apod_date_range        # Pictures for date range

neows_get_asteroids_today       # Today's approaching asteroids
neows_get_asteroids_week        # This week's asteroids
neows_get_asteroids_date_range  # Asteroids for date range
neows_get_potentially_hazardous # Only dangerous asteroids
neows_get_largest_asteroids_week # Largest asteroids
neows_analyze_asteroid_danger   # Detailed threat analysis

marsrover_get_rover_status      # Rover mission status
marsrover_get_latest_photos     # Most recent photos
marsrover_get_photos_by_earth_date # Photos by Earth date
marsrover_get_photos_by_sol     # Photos by Martian day
marsrover_get_photos_by_camera  # Photos by specific camera
marsrover_compare_rovers        # Compare all rovers
```

### 🌟 **Cross-MCP Capabilities**
- **Space Summary**: Combine APOD + asteroids + Mars data
- **Date Correlation**: Find all space events for a specific date
- **Size Comparisons**: Compare asteroid sizes with Mars rover scale

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone <your-repo-url>
cd nasa-space-explorer

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your NASA API key
```

### Run MCP Server
```bash
python app_mcp.py
```

### Connect LLM Client
- **Protocol**: MCP 2024-11-05
- **Server**: localhost:8000
- **Tools**: 15 available tools across 3 MCPs

## 🎥 Demo Video

[Link to demo video showing MCP integration with LLM client]

## 🏗️ Architecture

```
LLM Client (Claude Desktop, etc.)
    ↓ MCP Protocol
NASA MCP Server
    ├── APOD MCP ──→ NASA APOD API
    ├── NeoWs MCP ──→ NASA Asteroids API  
    └── Mars Rover MCP ──→ NASA Mars Rover API
```

## 🧪 Testing

All MCPs are thoroughly tested:
```bash
# Test individual MCPs
python tests/test_apod_quick.py      # 4/4 tests
python tests/test_neows_quick.py     # 5/5 tests  
python tests/test_marsrover_quick.py # 6/6 tests

# Test MCP server
python app_mcp.py  # Interactive testing interface
```

## 📊 Technical Highlights

- **✅ Full MCP Protocol**: Implements MCP 2024-11-05 standard
- **✅ Rate Limiting**: Respects NASA API limits (1000/hour)
- **✅ Error Handling**: Robust retry logic and validation
- **✅ Cross-MCP Queries**: Unique capability to combine multiple NASA APIs
- **✅ Production Ready**: Comprehensive testing and error handling

## 🎯 Example Queries

**Natural language queries your LLM can now answer:**

1. *"What's today's astronomy picture and are there any dangerous asteroids?"*
2. *"Show me Mars photos from the same day as the astronomy picture on July 4th, 2023"*
3. *"Compare this week's largest asteroid to the size of Curiosity rover"*
4. *"Give me a complete space summary for today"*

## 🏆 Why This Project Wins

1. **🔧 Technical Excellence**: Full MCP protocol implementation
2. **🌍 Real Impact**: Makes NASA's incredible data accessible to any LLM
3. **🎯 Innovation**: Cross-MCP queries that don't exist elsewhere
4. **📈 Scalable**: Architecture ready for additional space APIs
5. **🧪 Tested**: 15+ comprehensive tests ensuring reliability

---

**Built for Gradio Agents & MCP Hackathon 2025** 🚀