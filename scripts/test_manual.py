"""
Test manual untuk agent dengan berbagai prompt
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import create_agent

async def test_agent_prompts():
    """Test agent dengan berbagai jenis prompt"""
    print("=== Creating Gemini Agent ===")
    try:
        agent = create_agent(model_type="gemini", persona="personal")
        print("✅ Agent created successfully!")
        
        # Test prompts
        test_prompts = [
            "Halo, siapa kamu dan apa yang bisa kamu lakukan?",
            "Jelaskan tentang kecerdasan buatan dengan bahasa sederhana",
            "Buatkan contoh kode Python untuk menghitung faktorial",
            "Apa perbedaan antara machine learning dan deep learning?",
            "Ceritakan lelucon yang lucu tentang programmer"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n=== Test {i}: {prompt[:50]}... ===")
            try:
                response = await agent.chat(prompt)
                print(f"Response: {response[:200]}...")
                print("✅ Success")
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")

if __name__ == "__main__":
    asyncio.run(test_agent_prompts())
