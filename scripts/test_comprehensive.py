"""
Comprehensive testing script untuk AI Agent
Test berbagai scenario dan catat error ke logging system
"""
import asyncio
import sys
import traceback
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import create_agent
from src.utils.logging import log_error, log_debug, log_chat, agent_logger

async def test_agent_comprehensive():
    """Test agent dengan berbagai scenario untuk menemukan error"""
    
    print("🧪 Starting Comprehensive Agent Testing...")
    
    # Test 1: Agent Creation dengan model yang salah
    print("\n=== Test 1: Invalid Model Creation ===")
    try:
        invalid_agent = create_agent(model_type="invalid_model", persona="personal")
        print("❌ Expected error but agent created successfully")
    except Exception as e:
        print(f"✅ Expected error caught: {e}")
        log_error(e, {"test": "invalid_model_creation"}, "comprehensive_test")
    
    # Test 2: Agent Creation dengan persona yang salah
    print("\n=== Test 2: Invalid Persona ===")
    try:
        persona_agent = create_agent(model_type="gemini", persona="invalid_persona")
        print("⚠️ Agent created with invalid persona (might be handled gracefully)")
    except Exception as e:
        print(f"✅ Error caught: {e}")
        log_error(e, {"test": "invalid_persona"}, "comprehensive_test")
    
    # Test 3: Normal Agent Creation
    print("\n=== Test 3: Normal Agent Creation ===")
    try:
        agent = create_agent(model_type="gemini", persona="personal")
        print("✅ Agent created successfully")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        log_error(e, {"test": "normal_agent_creation"}, "comprehensive_test")
        return
    
    # Test 4: Normal Chat
    print("\n=== Test 4: Normal Chat ===")
    try:
        response = await agent.chat("Halo, siapa kamu?")
        print(f"✅ Normal chat successful: {response[:50]}...")
        log_chat("Halo, siapa kamu?", response, {"test": "normal_chat"})
    except Exception as e:
        print(f"❌ Normal chat failed: {e}")
        log_error(e, {"test": "normal_chat", "message": "Halo, siapa kamu?"}, "comprehensive_test")
    
    # Test 5: Empty Message
    print("\n=== Test 5: Empty Message ===")
    try:
        response = await agent.chat("")
        print(f"✅ Empty message handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ Empty message error: {e}")
        log_error(e, {"test": "empty_message"}, "comprehensive_test")
    
    # Test 6: Very Long Message
    print("\n=== Test 6: Very Long Message ===")
    try:
        long_message = "Ini adalah pesan yang sangat panjang. " * 200  # ~7000 characters
        response = await agent.chat(long_message)
        print(f"✅ Long message handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ Long message error: {e}")
        log_error(e, {"test": "long_message", "message_length": len(long_message)}, "comprehensive_test")
    
    # Test 7: Special Characters
    print("\n=== Test 7: Special Characters ===")
    try:
        special_message = "Test dengan emoji 🤖😀💻 dan karakter khusus: @#$%^&*()_+-=[]{}|;':\",./<>?"
        response = await agent.chat(special_message)
        print(f"✅ Special characters handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ Special characters error: {e}")
        log_error(e, {"test": "special_characters"}, "comprehensive_test")
    
    # Test 8: Code Request
    print("\n=== Test 8: Code Request ===")
    try:
        code_message = "Buatkan kode Python untuk menghitung faktorial dengan rekursi"
        response = await agent.chat(code_message)
        print(f"✅ Code request handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ Code request error: {e}")
        log_error(e, {"test": "code_request"}, "comprehensive_test")
    
    # Test 9: Math Problem
    print("\n=== Test 9: Math Problem ===")
    try:
        math_message = "Jelaskan rumus kuadrat dan berikan contoh penggunaannya"
        response = await agent.chat(math_message)
        print(f"✅ Math problem handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ Math problem error: {e}")
        log_error(e, {"test": "math_problem"}, "comprehensive_test")
    
    # Test 10: Multiple Rapid Messages
    print("\n=== Test 10: Multiple Rapid Messages ===")
    try:
        for i in range(3):
            rapid_message = f"Pesan cepat ke-{i+1}: Apa kabar?"
            response = await agent.chat(rapid_message)
            print(f"✅ Rapid message {i+1}: {response[:30]}...")
    except Exception as e:
        print(f"❌ Rapid messages error: {e}")
        log_error(e, {"test": "rapid_messages"}, "comprehensive_test")
    
    # Test 11: Non-ASCII Characters
    print("\n=== Test 11: Non-ASCII Characters ===")
    try:
        unicode_message = "测试中文, العربية, русский, 日本語,한국어"
        response = await agent.chat(unicode_message)
        print(f"✅ Unicode characters handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ Unicode characters error: {e}")
        log_error(e, {"test": "unicode_characters"}, "comprehensive_test")
    
    # Test 12: Context with None
    print("\n=== Test 12: Chat with None Context ===")
    try:
        response = await agent.chat("Test dengan context None", context=None)
        print(f"✅ None context handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ None context error: {e}")
        log_error(e, {"test": "none_context"}, "comprehensive_test")
    
    # Test 13: Chat with Complex Context
    print("\n=== Test 13: Chat with Complex Context ===")
    try:
        complex_context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "preferences": {"language": "id", "style": "formal"},
            "metadata": {"timestamp": "2025-07-06", "version": "1.0"}
        }
        response = await agent.chat("Test dengan context kompleks", context=complex_context)
        print(f"✅ Complex context handled: {response[:50]}...")
    except Exception as e:
        print(f"❌ Complex context error: {e}")
        log_error(e, {"test": "complex_context", "context": complex_context}, "comprehensive_test")

if __name__ == "__main__":
    asyncio.run(test_agent_comprehensive())
    
    print("\n" + "="*60)
    print("🔍 TESTING COMPLETED - Checking Error Summary...")
    
    # Show error summary
    try:
        error_summary = agent_logger.create_error_summary()
        print(f"\n📊 Error Summary:")
        print(f"Total Errors Today: {error_summary['total_errors']}")
        if error_summary['total_errors'] > 0:
            print("Error Types:")
            for error_type, count in error_summary['error_types'].items():
                print(f"  - {error_type}: {count}")
        else:
            print("✅ No errors recorded!")
    except Exception as e:
        print(f"❌ Could not generate error summary: {e}")
