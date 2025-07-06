"""
Focused test untuk action phase error yang sering muncul
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import create_agent
from src.utils.logging import log_error, log_debug

async def test_action_phase_error():
    """Test spesifik untuk error 'str' object has no attribute 'get'"""
    
    print("🔍 Testing Action Phase Error...")
    
    try:
        agent = create_agent(model_type="gemini", persona="personal")
        print("✅ Agent created")
        
        # Test messages yang menyebabkan action phase error
        problematic_messages = [
            "Hitung 2 + 2",
            "Tampilkan file dalam folder ini", 
            "Cari informasi tentang Python",
            "Buatkan list tugas untuk hari ini",
            "Jelaskan konsep machine learning",
        ]
        
        for i, message in enumerate(problematic_messages, 1):
            print(f"\n--- Test {i}: {message} ---")
            try:
                response = await agent.chat(message)
                print(f"Response: {response[:100]}...")
                
                # Check if response indicates action failure
                if "Action failed" in response and "'str' object has no attribute 'get'" in response:
                    print("🚨 DETECTED: Action phase error!")
                    
                    # Log this as a critical error untuk investigation
                    error_context = {
                        "test_type": "action_phase_investigation",
                        "message": message,
                        "response": response,
                        "error_pattern": "'str' object has no attribute 'get'"
                    }
                    
                    # Create a mock exception untuk logging
                    action_error = Exception("Action phase error detected: 'str' object has no attribute 'get'")
                    log_error(action_error, error_context, "action_phase_test")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                log_error(e, {"message": message, "test": "action_phase"}, "action_phase_test")
    
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        log_error(e, {"test": "action_phase_agent_creation"}, "action_phase_test")

if __name__ == "__main__":
    asyncio.run(test_action_phase_error())
