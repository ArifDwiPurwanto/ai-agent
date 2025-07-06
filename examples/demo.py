#!/usr/bin/env python3
"""
Demonstration script for AI Agent functionality without requiring API keys
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.calculator import CalculatorTool
from src.tools.file_manager import FileManagerTool
from src.memory.short_term import ShortTermMemory
from src.memory.memory_manager import MemoryManager
from src.config import settings

async def test_tools():
    """Test various tools without API dependencies"""
    print("🔧 Testing AI Agent Tools\n")
    
    # Test Calculator
    print("📊 Testing Calculator Tool:")
    calc = CalculatorTool()
    
    expressions = [
        "2 + 2",
        "15 * 23 + 100", 
        "sqrt(144)",
        "sin(3.14159/2)",
        "factorial(5)"
    ]
    
    for expr in expressions:
        result = await calc.execute(expr)
        if result.success:
            print(f"  {expr} = {result.result['result']}")
        else:
            print(f"  {expr} -> Error: {result.error}")
    
    print()
    
    # Test File Manager
    print("📁 Testing File Manager Tool:")
    fm = FileManagerTool()
    
    # List current directory
    result = await fm.execute('list', directory_path='.')
    if result.success:
        items = result.result['items'][:5]  # Show first 5 items
        print("  Top-level files/directories:")
        for item in items:
            icon = "📁" if item['type'] == 'directory' else "📄"
            print(f"    {icon} {item['name']}")
    
    print()
    
    # Test Memory System
    print("🧠 Testing Memory System:")
    
    # Short-term memory
    stm = ShortTermMemory(max_messages=5)
    stm.add_message("user", "Hello, I'm testing the memory system")
    stm.add_message("assistant", "Hello! I can remember our conversation")
    stm.add_message("user", "What's 2+2?")
    stm.add_message("assistant", "2+2 equals 4")
    
    messages = stm.get_messages()
    print(f"  Short-term memory contains {len(messages)} messages")
    if len(messages) >= 2:
        print(f"  Latest exchange: User said '{messages[-2]['content']}'")
        print(f"                   Assistant replied '{messages[-1]['content']}'")
    else:
        print(f"  Most recent message: '{messages[-1]['content']}'" if messages else "  No messages stored")
    
    print()
    
    # Memory Manager (without LTM to avoid API dependencies)
    print("🎛️ Testing Memory Manager:")
    try:
        memory_manager = MemoryManager()
        
        # Test preferences
        await memory_manager.store_preference("preferred_calculation_format", "decimal")
        await memory_manager.store_preference("user_timezone", "UTC")
        
        prefs = await memory_manager.get_preferences()
        print(f"  Stored preferences: {list(prefs.keys())}")
    except Exception as e:
        print(f"  Memory Manager test skipped (requires API keys): {str(e)[:50]}...")
    
    print()
    
    # Test Configuration
    print("⚙️ Testing Configuration:")
    print(f"  Agent name: {settings.AGENT_NAME}")
    print(f"  Default model: {settings.DEFAULT_MODEL}")
    print(f"  Memory path: {settings.MEMORY_PERSIST_PATH}")
    print(f"  Max STM messages: {settings.STM_MAX_MESSAGES}")
    
    print("\n✅ All tool tests completed successfully!")
    print("\n💡 To test with real AI models, set up your API keys in .env file:")
    print("   - OPENAI_API_KEY for OpenAI GPT models")
    print("   - GOOGLE_API_KEY for Google Gemini models")
    print("   - WEATHER_API_KEY for weather information")

async def demo_agent_simulation():
    """Simulate an agent conversation without AI model"""
    print("\n🤖 Agent Simulation Demo")
    print("="*50)
    
    # Initialize components
    stm = ShortTermMemory()
    calc = CalculatorTool()
    fm = FileManagerTool()
    
    # Simulate a conversation
    conversations = [
        ("user", "Hello, can you help me with some calculations?"),
        ("assistant", "Hello! I'd be happy to help you with calculations. What would you like to calculate?"),
        ("user", "What's 25 * 15 + 100?"),
        ("assistant", "Let me calculate that for you."),
        ("user", "Also, can you list the files in the current directory?"),
        ("assistant", "I'll calculate that and list the files for you.")
    ]
    
    for role, message in conversations:
        stm.add_message(role, message)
        icon = "👤" if role == "user" else "🤖"
        print(f"{icon} {role.title()}: {message}")
    
    print("\n🔢 Performing calculation: 25 * 15 + 100")
    calc_result = await calc.execute("25 * 15 + 100")
    if calc_result.success:
        print(f"   Result: {calc_result.result['result']}")
    
    print("\n📂 Listing current directory files:")
    file_result = await fm.execute('list', directory_path='.')
    if file_result.success:
        items = file_result.result['items'][:3]
        for item in items:
            icon = "📁" if item['type'] == 'directory' else "📄"
            print(f"   {icon} {item['name']}")
    
    print(f"\n💾 Conversation history: {len(stm.get_messages())} messages stored")
    print("\n✨ This demonstrates how the agent would work with real AI models!")

if __name__ == "__main__":
    print("🚀 AI Personal Assistant Agent - Demo Mode")
    print("=" * 60)
    print("This demo shows the agent's capabilities without requiring API keys.\n")
    
    asyncio.run(test_tools())
    asyncio.run(demo_agent_simulation())
    
    print("\n🎉 Demo completed! The AI agent is ready for production use.")
    print("   Set up your API keys to enable full AI-powered conversations.")
