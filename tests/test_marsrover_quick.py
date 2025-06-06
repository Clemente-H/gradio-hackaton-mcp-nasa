"""Quick test script for Mars Rover MCP."""

import asyncio
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, '..', 'src')
sys.path.insert(0, src_path)

async def test_marsrover_mcp():
    """Test Mars Rover MCP functionality."""
    
    print("🔴 Testing NASA Mars Rover MCP...")
    print("=" * 50)
    
    try:
        from mcps.marsrover_mcp import MarsRoverMCP
        from config import Config
        
        print(f"📡 NASA API Key: {'✅ Set' if Config.NASA_API_KEY != 'DEMO_KEY' else '⚠️  Using DEMO_KEY'}")
        print()
        
        # Initialize MCP
        marsrover_mcp = MarsRoverMCP()
        print(f"🛠️  MCP Name: {marsrover_mcp.name}")
        print(f"📝 Description: {marsrover_mcp.description}")
        print()
        
        # Test tools discovery
        tools = marsrover_mcp.get_tools()
        print(f"🔧 Available Tools: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        print()
        
        # Test 1: Get Curiosity status
        print("🤖 Test 1: Getting Curiosity rover status...")
        result1 = await marsrover_mcp.call_tool("get_rover_status", {"rover": "curiosity"})
        
        if result1["success"]:
            data = result1["data"]
            print(f"   ✅ Success: {data['name']} - {data['status']}")
            print(f"   📅 Mission duration: {data['mission_duration_years']} years")
            print(f"   📸 Total photos: {data['total_photos']:,}")
            print(f"   📷 Cameras: {len(data['available_cameras'])}")
        else:
            print(f"   ❌ Failed: {result1.get('error', 'Unknown error')}")
        print()
        
        # Test 2: Get latest photos
        print("📸 Test 2: Getting latest Curiosity photos...")
        result2 = await marsrover_mcp.call_tool("get_latest_photos", {"rover": "curiosity", "count": 10})
        
        if result2["success"]:
            data = result2["data"]
            print(f"   ✅ Success: Found {data['count']} latest photos")
            print(f"   🗓️  Latest sol: {data['latest_sol']}")
            print(f"   📅 Latest Earth date: {data['latest_earth_date']}")
            print(f"   📷 Cameras used: {len(data['by_camera'])} different cameras")
        else:
            print(f"   ❌ Failed: {result2.get('error', 'Unknown error')}")
        print()
        
        # Test 3: Get photos by Earth date
        print("📅 Test 3: Getting photos by Earth date...")
        result3 = await marsrover_mcp.call_tool("get_photos_by_earth_date", {
            "rover": "curiosity",
            "earth_date": "2023-01-01"
        })
        
        if result3["success"]:
            data = result3["data"]
            print(f"   ✅ Success: Found {data['count']} photos on {data['earth_date']}")
        else:
            print(f"   ❌ Failed: {result3.get('error', 'Unknown error')}")
        print()
        
        # Test 4: Get photos by sol
        print("🌅 Test 4: Getting photos by Martian sol...")
        result4 = await marsrover_mcp.call_tool("get_photos_by_sol", {
            "rover": "curiosity",
            "sol": 1000
        })
        
        if result4["success"]:
            data = result4["data"]
            print(f"   ✅ Success: Found {data['count']} photos on sol {data['sol']}")
        else:
            print(f"   ❌ Failed: {result4.get('error', 'Unknown error')}")
        print()
        
        # Test 5: Get photos by camera
        print("📷 Test 5: Getting MAST camera photos...")
        result5 = await marsrover_mcp.call_tool("get_photos_by_camera", {
            "rover": "curiosity",
            "camera": "MAST",
            "count": 5
        })
        
        if result5["success"]:
            data = result5["data"]
            print(f"   ✅ Success: Found {data['count']} {data['camera']} photos")
            print(f"   📷 Camera: {data['camera_full_name']}")
        else:
            print(f"   ❌ Failed: {result5.get('error', 'Unknown error')}")
        print()
        
        # Test 6: Compare rovers
        print("🤖 Test 6: Comparing all rovers...")
        result6 = await marsrover_mcp.call_tool("compare_rovers", {})
        
        if result6["success"]:
            data = result6["data"]
            summary = data["summary"]
            print(f"   ✅ Success: Compared {summary['total_rovers']} rovers")
            print(f"   🟢 Active rovers: {', '.join(summary['active_rovers'])}")
            print(f"   📸 Total photos: {summary['total_photos_all_rovers']:,}")
            print(f"   ⏱️  Longest mission: {summary['longest_mission']} days")
        else:
            print(f"   ❌ Failed: {result6.get('error', 'Unknown error')}")
        print()
        
        # Summary
        successful_tests = sum([
            result1["success"],
            result2["success"], 
            result3["success"],
            result4["success"],
            result5["success"],
            result6["success"]
        ])
        
        print("=" * 50)
        print(f"🎯 Test Summary: {successful_tests}/6 tests passed")
        
        if successful_tests == 6:
            print("🎉 All tests passed! Mars Rover MCP is ready!")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
        
        return successful_tests == 6
    
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_marsrover_mcp())
    sys.exit(0 if success else 1)