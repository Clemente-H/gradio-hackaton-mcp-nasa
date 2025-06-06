"""Quick test script for NeoWs MCP."""

import asyncio
import sys
import os

# Add src to path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, '..', 'src')
sys.path.insert(0, src_path)

async def test_neows_mcp():
    """Test NeoWs MCP functionality."""
    
    print("🌍 Testing NASA NeoWs MCP...")
    print("=" * 50)
    
    try:
        from mcps.neows_mcp import NeoWsMCP
        from config import Config
        
        print(f"📡 NASA API Key: {'✅ Set' if Config.NASA_API_KEY != 'DEMO_KEY' else '⚠️  Using DEMO_KEY'}")
        print()
        
        # Initialize MCP
        neows_mcp = NeoWsMCP()
        print(f"🛠️  MCP Name: {neows_mcp.name}")
        print(f"📝 Description: {neows_mcp.description}")
        print()
        
        # Test tools discovery
        tools = neows_mcp.get_tools()
        print(f"🔧 Available Tools: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        print()
        
        # Test 1: Get today's asteroids
        print("🌟 Test 1: Getting today's asteroids...")
        result1 = await neows_mcp.call_tool("get_asteroids_today", {})
        
        if result1["success"]:
            data = result1["data"]
            print(f"   ✅ Success: Found {data['total_count']} asteroids")
            print(f"   ⚠️  Hazardous: {data['hazardous_count']} potentially dangerous")
        else:
            print(f"   ❌ Failed: {result1.get('error', 'Unknown error')}")
        print()
        
        # Test 2: Get this week's asteroids
        print("📅 Test 2: Getting this week's asteroids...")
        result2 = await neows_mcp.call_tool("get_asteroids_week", {})
        
        if result2["success"]:
            data = result2["data"]
            print(f"   ✅ Success: Found {data['total_count']} asteroids this week")
            print(f"   ⚠️  Hazardous: {data['hazardous_count']} potentially dangerous")
            print(f"   📊 Days with data: {len(data['by_date'])} days")
        else:
            print(f"   ❌ Failed: {result2.get('error', 'Unknown error')}")
        print()
        
        # Test 3: Get potentially hazardous asteroids
        print("🚨 Test 3: Getting potentially hazardous asteroids...")
        result3 = await neows_mcp.call_tool("get_potentially_hazardous", {})
        
        if result3["success"]:
            data = result3["data"]
            count = data['hazardous_count']
            print(f"   ✅ Success: Found {count} potentially hazardous asteroids")
            if count > 0:
                first_hazardous = data['asteroids'][0]
                print(f"      Example: {first_hazardous['name']} - {first_hazardous['size_comparison']}")
        else:
            print(f"   ❌ Failed: {result3.get('error', 'Unknown error')}")
        print()
        
        # Test 4: Get largest asteroids
        print("📏 Test 4: Getting largest asteroids this week...")
        result4 = await neows_mcp.call_tool("get_largest_asteroids_week", {"count": 3})
        
        if result4["success"]:
            data = result4["data"]
            print(f"   ✅ Success: Found top {data['count']} largest asteroids")
            for i, asteroid in enumerate(data['asteroids']):
                diameter = asteroid['diameter_km']['max']
                print(f"      {i+1}. {asteroid['name']}: {diameter:.3f} km")
        else:
            print(f"   ❌ Failed: {result4.get('error', 'Unknown error')}")
        print()
        
        # Test 5: Date range query
        print("📆 Test 5: Testing date range query...")
        result5 = await neows_mcp.call_tool("get_asteroids_date_range", {
            "start_date": "2024-01-01",
            "end_date": "2024-01-03"
        })
        
        if result5["success"]:
            data = result5["data"]
            print(f"   ✅ Success: Found {data['total_count']} asteroids in date range")
        else:
            print(f"   ❌ Failed: {result5.get('error', 'Unknown error')}")
        print()
        
        # Summary
        successful_tests = sum([
            result1["success"],
            result2["success"], 
            result3["success"],
            result4["success"],
            result5["success"]
        ])
        
        print("=" * 50)
        print(f"🎯 Test Summary: {successful_tests}/5 tests passed")
        
        if successful_tests == 5:
            print("🎉 All tests passed! NeoWs MCP is ready!")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
        
        return successful_tests == 5
    
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_neows_mcp())
    sys.exit(0 if success else 1)