# test_apod_quick.py
"""Quick test script for APOD MCP - Run this to verify everything works."""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_apod_mcp():
    """Test APOD MCP functionality."""
    
    print("🚀 Testing NASA APOD MCP...")
    print("=" * 50)
    
    try:
        # Import after adding to path
        from src.mcps.apod_mcp import APODMCP
        from src.config import Config
        
        # Verify config
        print(f"📡 NASA API Key: {'✅ Set' if Config.NASA_API_KEY != 'DEMO_KEY' else '⚠️  Using DEMO_KEY'}")
        print(f"🔗 Base URL: {Config.NASA_BASE_URL}")
        print()
        
        # Initialize MCP
        apod_mcp = APODMCP()
        print(f"🛠️  MCP Name: {apod_mcp.name}")
        print(f"📝 Description: {apod_mcp.description}")
        print()
        
        # Test tools discovery
        tools = apod_mcp.get_tools()
        print(f"🔧 Available Tools: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        print()
        
        # Test 1: Get today's APOD
        print("🌟 Test 1: Getting today's APOD...")
        result1 = await apod_mcp.call_tool("get_apod_today", {})
        
        if result1["success"]:
            data = result1["data"]
            print(f"   ✅ Success: {data['title']}")
            print(f"   📅 Date: {data['date']}")
            print(f"   🎬 Media Type: {data['media_type']}")
            print(f"   🔗 URL: {data['url']}")
            if data.get('copyright'):
                print(f"   ©️  Copyright: {data['copyright']}")
        else:
            print(f"   ❌ Failed: {result1.get('error', 'Unknown error')}")
        print()
        
        # Test 2: Get APOD by specific date
        test_date = "2023-07-04"  # A good date with likely interesting content
        print(f"🗓️  Test 2: Getting APOD for {test_date}...")
        result2 = await apod_mcp.call_tool("get_apod_by_date", {"date": test_date})
        
        if result2["success"]:
            data = result2["data"]
            print(f"   ✅ Success: {data['title']}")
            print(f"   📝 Explanation (first 100 chars): {data['explanation'][:100]}...")
        else:
            print(f"   ❌ Failed: {result2.get('error', 'Unknown error')}")
        print()
        
        # Test 3: Get APOD date range (small range)
        start_date = "2023-07-01"
        end_date = "2023-07-03"
        print(f"📅 Test 3: Getting APOD range {start_date} to {end_date}...")
        result3 = await apod_mcp.call_tool("get_apod_date_range", {
            "start_date": start_date,
            "end_date": end_date
        })
        
        if result3["success"]:
            data = result3["data"]
            print(f"   ✅ Success: Found {len(data)} APODs")
            for i, apod in enumerate(data):
                print(f"      {i+1}. {apod['date']}: {apod['title']}")
        else:
            print(f"   ❌ Failed: {result3.get('error', 'Unknown error')}")
        print()
        
        # Test 4: Error handling (invalid date)
        print("🚨 Test 4: Testing error handling with invalid date...")
        result4 = await apod_mcp.call_tool("get_apod_by_date", {"date": "invalid-date"})
        
        if not result4["success"]:
            print(f"   ✅ Error handling works: {result4.get('error', 'Unknown error')}")
        else:
            print("   ⚠️  Expected error but got success")
        print()
        
        # Summary
        successful_tests = sum([
            result1["success"],
            result2["success"], 
            result3["success"],
            not result4["success"]  # This should fail
        ])
        
        print("=" * 50)
        print(f"🎯 Test Summary: {successful_tests}/4 tests passed")
        
        if successful_tests == 4:
            print("🎉 All tests passed! APOD MCP is ready!")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
        
        return successful_tests == 4
    
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you've installed all requirements and created the file structure.")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_apod_mcp())
    sys.exit(0 if success else 1)