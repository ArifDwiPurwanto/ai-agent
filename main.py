"""
Main entry point for AI Personal Assistant Agent
"""
import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agent import PersonalAssistantAgent, create_agent
from src.config import settings

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('agent.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Personal Assistant Agent")
    parser.add_argument(
        "--model", 
        choices=["openai", "gemini"], 
        default=settings.DEFAULT_MODEL,
        help="Model to use (default: %(default)s)"
    )
    parser.add_argument(
        "--persona", 
        choices=["personal", "research", "technical"], 
        default="personal",
        help="Agent persona (default: %(default)s)"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--message", 
        type=str,
        help="Single message to process (non-interactive mode)"
    )
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        default="INFO",
        help="Logging level (default: %(default)s)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    try:
        # Create agent
        print("🚀 Initializing AI Personal Assistant Agent...")
        print(f"   Model: {args.model}")
        print(f"   Persona: {args.persona}")
        
        agent = create_agent(model_type=args.model, persona=args.persona)
        
        print("✅ Agent initialized successfully!")
        
        if args.interactive:
            # Run interactive session
            await agent.run_interactive_session()
        elif args.message:
            # Process single message
            print(f"\n👤 User: {args.message}")
            response = await agent.chat(args.message)
            print(f"🤖 Assistant: {response}")
        else:
            # Show agent status and available commands
            status = agent.get_agent_status()
            print(f"""
📊 Agent Ready:
├── ID: {status['agent_id']}
├── Model: {status['model_info']['provider']} ({status['model_info']['model']})
├── Persona: {status['persona']}
├── Available Tools: {', '.join(status['available_tools'])}
└── Memory: {status['memory_summary']['short_term']['message_count']} messages in STM

💡 Usage:
├── Interactive mode: python main.py --interactive
├── Single message: python main.py --message "Hello, how are you?"
└── Help: python main.py --help
""")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
