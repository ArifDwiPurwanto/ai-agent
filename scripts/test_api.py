"""
Test script untuk mengecek validitas API keys
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.agent import create_agent
import asyncio

async def test_api_keys():
    """Test API keys validation"""
    print("=== Testing API Keys ===")
    print(f"OpenAI Key: {settings.OPENAI_API_KEY[:10] + '...' if settings.OPENAI_API_KEY else 'None'}")
    print(f"Google Key: {settings.GOOGLE_API_KEY[:10] + '...' if settings.GOOGLE_API_KEY else 'None'}")
    print(f"Default Model: {settings.DEFAULT_MODEL}")
    
    # Test OpenAI key validation
    print(f"\nOpenAI Key Valid: {settings.is_api_key_valid('openai')}")
    print(f"Gemini Key Valid: {settings.is_api_key_valid('gemini')}")
    
    # Test agent creation
    print("\n=== Testing Agent Creation ===")
    try:
        print("Creating Gemini agent...")
        gemini_agent = create_agent(model_type="gemini", persona="personal")
        print("✅ Gemini agent created successfully")
        
        # Test simple chat
        print("\nTesting Gemini chat...")
        response = await gemini_agent.chat("Halo, siapa kamu?")
        print(f"Response: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ Gemini agent failed: {e}")
    
    try:
        print("\nCreating OpenAI agent...")
        openai_agent = create_agent(model_type="openai", persona="personal")
        print("✅ OpenAI agent created successfully")
        
        # Test simple chat
        print("\nTesting OpenAI chat...")
        response = await openai_agent.chat("Halo, siapa kamu?")
        print(f"Response: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ OpenAI agent failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_keys())
