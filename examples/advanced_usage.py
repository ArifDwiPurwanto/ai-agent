"""
Advanced usage example demonstrating different personas and capabilities
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import create_agent

async def advanced_example():
    """Advanced usage example with different personas"""
    print("=== Advanced AI Agent Example ===\n")
    
    # Test different personas
    personas = ["personal", "research", "technical"]
    
    for persona in personas:
        print(f"🎭 Testing {persona.upper()} persona:")
        print("-" * 30)
        
        agent = create_agent(model_type="openai", persona=persona)
        
        if persona == "personal":
            messages = [
                "Help me plan my day",
                "What's a good recipe for dinner?",
                "Remind me to call mom later"
            ]
        elif persona == "research":
            messages = [
                "Research the latest developments in quantum computing",
                "Find information about climate change effects",
                "Compare different renewable energy sources"
            ]
        else:  # technical
            messages = [
                "Explain how to optimize database queries",
                "What are the best practices for API design?",
                "Help me debug this Python code issue"
            ]
        
        for message in messages:
            print(f"👤 User: {message}")
            try:
                response = await agent.chat(message)
                print(f"🤖 Assistant: {response[:200]}...")  # Truncate for readability
            except Exception as e:
                print(f"❌ Error: {e}")
            print()
        
        print("=" * 50)

async def memory_example():
    """Example demonstrating memory capabilities"""
    print("\n=== Memory System Example ===\n")
    
    agent = create_agent(model_type="openai", persona="personal")
    
    # Store some information
    print("📝 Storing user information...")
    responses = []
    
    info_messages = [
        "My name is Alice and I work as a software engineer",
        "I'm learning Python and machine learning",
        "I prefer working in the morning and like coffee",
        "I live in Seattle and enjoy hiking on weekends"
    ]
    
    for message in info_messages:
        print(f"👤 User: {message}")
        response = await agent.chat(message)
        responses.append(response)
        print(f"🤖 Assistant: {response}")
        print()
    
    # Test memory recall
    print("🧠 Testing memory recall...")
    recall_messages = [
        "What do you remember about me?",
        "What's my profession?",
        "What are my hobbies?",
        "Where do I live?"
    ]
    
    for message in recall_messages:
        print(f"👤 User: {message}")
        response = await agent.chat(message)
        print(f"🤖 Assistant: {response}")
        print()
    
    # Show memory summary
    memory_summary = agent.get_memory_summary()
    print("📊 Memory Summary:")
    print(f"Short-term messages: {memory_summary['short_term']['message_count']}")
    print(f"Long-term memories: {memory_summary['long_term']['total_memories']}")

async def tool_usage_example():
    """Example demonstrating tool usage"""
    print("\n=== Tool Usage Example ===\n")
    
    agent = create_agent(model_type="openai", persona="personal")
    
    tool_messages = [
        "What's 234 * 567 + 123?",
        "Search for recent news about artificial intelligence",
        "What's the weather like in New York?",
        "Calculate the square root of 144"
    ]
    
    for message in tool_messages:
        print(f"👤 User: {message}")
        try:
            response = await agent.chat(message)
            print(f"🤖 Assistant: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 30)
    
    # Show tool usage statistics
    stats = agent.get_statistics()
    print("\n🔧 Tool Usage Statistics:")
    for tool_name, tool_stats in stats['tools'].items():
        print(f"{tool_name}: {tool_stats['usage_count']} uses")

if __name__ == "__main__":
    async def run_all_examples():
        await advanced_example()
        await memory_example()
        await tool_usage_example()
    
    asyncio.run(run_all_examples())
