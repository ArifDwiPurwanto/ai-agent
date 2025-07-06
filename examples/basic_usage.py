"""
Basic usage example for AI Personal Assistant Agent
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import create_agent

async def basic_example():
    """Basic usage example"""
    print("=== Basic AI Agent Example ===\n")
    
    # Create agent
    agent = create_agent(model_type="openai", persona="personal")
    
    # Example conversations
    examples = [
        "Hello! What can you help me with?",
        "What's the weather like in Jakarta?",
        "Calculate 15 * 23 + 87",
        "Search for information about artificial intelligence",
        "Remember that my name is John and I prefer coffee over tea",
        "What did I tell you about my preferences?"
    ]
    
    for i, message in enumerate(examples, 1):
        print(f"Example {i}:")
        print(f"👤 User: {message}")
        
        try:
            response = await agent.chat(message)
            print(f"🤖 Assistant: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    # Show agent statistics
    stats = agent.get_statistics()
    print("\n📊 Agent Statistics:")
    print(f"Total interactions: {stats['interactions']['total']}")
    print(f"Memory summary: {stats['memory']}")

if __name__ == "__main__":
    asyncio.run(basic_example())
