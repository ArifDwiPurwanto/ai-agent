"""
Core AI Agent implementation
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from .agent_loop import AgentLoop
from ..config import settings
from ..utils.logging import log_error, log_debug, log_chat, log_agent_lifecycle, log_performance


def validate_model_type(model_type: str) -> str:
    """Validate and return the model type"""
    supported_models = ["openai", "gemini"]
    if model_type not in supported_models:
        raise ValueError(f"Unsupported model type: {model_type}. Supported models: {supported_models}")
    return model_type


def validate_persona(persona: str) -> str:
    """Validate and return the persona"""
    valid_personas = ["personal", "research", "technical"]
    if persona not in valid_personas:
        raise ValueError(f"Invalid persona: {persona}. Valid personas: {valid_personas}")
    return persona


class PersonalAssistantAgent:
    """
    Main AI Personal Assistant Agent class
    Coordinates all agent components and provides high-level interface
    """
    
    def __init__(self, model_type: Optional[str] = None, agent_persona: str = "personal"):
        """
        Initialize the AI Agent
        
        Args:
            model_type: Model type ("openai" or "gemini")
            agent_persona: Agent persona ("personal", "research", "technical")
        """
        # Validate inputs early
        model_type = model_type or settings.DEFAULT_MODEL
        try:
            model_type = validate_model_type(model_type)
            agent_persona = validate_persona(agent_persona)
        except ValueError as e:
            log_error(e, {"model_type": model_type, "persona": agent_persona}, "core_agent")
            raise
        
        # Log agent initialization start
        log_agent_lifecycle("agent_init_start", {
            "model_type": model_type,
            "persona": agent_persona
        })
        
        # Check if API keys are valid (don't raise exception, just log warning)
        try:
            settings.validate_api_keys()
            log_debug("API keys validation passed")
        except ValueError as e:
            self.logger = logging.getLogger(__name__)
            self.logger.warning(f"API key validation failed: {e}")
            log_error(e, {"model_type": model_type}, "core_agent")
            # Continue initialization but agent will have limited functionality
        
        # Initialize agent loop
        try:
            self.agent_loop = AgentLoop(model_type)
            self.agent_loop.set_persona(agent_persona)
            log_debug("Agent loop initialized successfully")
        except Exception as e:
            log_error(e, {"model_type": model_type, "persona": agent_persona}, "core_agent")
            # Re-raise the exception to prevent creating invalid agents
            raise
        
        # Agent metadata
        self.agent_id = f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.created_at = datetime.now()
        self.total_interactions = 0
        
        # Logging
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(__name__)
        
        log_agent_lifecycle("agent_init_complete", {
            "agent_id": self.agent_id,
            "model_type": model_type,
            "persona": agent_persona
        })
        
        self.logger.info(f"AI Agent initialized with {model_type} model")
    
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Main chat interface for the agent
        
        Args:
            message: User message
            context: Optional context information
            
        Returns:
            Agent response
        """
        start_time = time.time()
        try:
            self.total_interactions += 1
            self.logger.info(f"Processing user message (interaction #{self.total_interactions})")
            
            log_debug("Chat request received", {
                "interaction_id": self.total_interactions,
                "message_length": len(message),
                "user_message": message[:100] + "..." if len(message) > 100 else message
            })
            
            # Add interaction metadata to context
            enhanced_context = {
                **(context or {}),
                "interaction_id": self.total_interactions,
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Process through agent loop
            response = await self.agent_loop.process_user_input(message, enhanced_context)
            
            # Log performance and chat interaction
            response_time = time.time() - start_time
            log_performance("chat_processing", response_time, {
                "interaction_id": self.total_interactions,
                "message_length": len(message),
                "response_length": len(response)
            })
            
            log_chat(message, response, {
                "interaction_id": self.total_interactions,
                "response_time": response_time,
                "agent_id": self.agent_id
            })
            
            self.logger.info("Successfully processed user message")
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            log_error(e, {
                "message": message[:100] + "..." if len(message) > 100 else message,
                "interaction_id": self.total_interactions,
                "response_time": response_time
            }, "core_agent_chat")
            
            self.logger.error(f"Error in chat processing: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def set_persona(self, persona: str) -> bool:
        """
        Change agent persona
        
        Args:
            persona: New persona ("personal", "research", "technical")
            
        Returns:
            True if successful
        """
        try:
            self.agent_loop.set_persona(persona)
            self.logger.info(f"Agent persona changed to: {persona}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to change persona: {e}")
            return False
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of agent memory"""
        return self.agent_loop.memory_manager.get_memory_summary()
    
    def clear_memory(self, memory_type: str = "short_term") -> bool:
        """
        Clear agent memory
        
        Args:
            memory_type: Type of memory to clear ("short_term", "long_term", "all")
            
        Returns:
            True if successful
        """
        try:
            if memory_type in ["short_term", "all"]:
                self.agent_loop.memory_manager.clear_stm()
            # Note: We don't clear long-term memory by default for safety
                
            self.logger.info(f"Cleared {memory_type} memory")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear memory: {e}")
            return False
    
    def store_user_preference(self, key: str, value: str) -> bool:
        """
        Store user preference
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful
        """
        try:
            self.agent_loop.memory_manager.store_user_preference(key, value)
            self.logger.info(f"Stored user preference: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store preference: {e}")
            return False
    
    def get_user_preference(self, key: str) -> Optional[str]:
        """
        Get user preference
        
        Args:
            key: Preference key
            
        Returns:
            Preference value or None
        """
        try:
            return self.agent_loop.memory_manager.get_user_preference(key)
        except Exception as e:
            self.logger.error(f"Failed to get preference: {e}")
            return None
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search agent memories
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        try:
            return self.agent_loop.memory_manager.search_memories(query, limit)
        except Exception as e:
            self.logger.error(f"Failed to search memories: {e}")
            return []
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.agent_loop.tools.keys())
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        status = self.agent_loop.get_status()
        status.update({
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat(),
            "total_interactions": self.total_interactions,
            "uptime_seconds": (datetime.now() - self.created_at).total_seconds()
        })
        return status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent usage statistics"""
        memory_stats = self.get_memory_summary()
        
        # Tool usage stats
        tool_stats = {}
        for tool_name, tool in self.agent_loop.tools.items():
            tool_stats[tool_name] = tool.get_usage_stats()
        
        return {
            "interactions": {
                "total": self.total_interactions,
                "uptime_hours": (datetime.now() - self.created_at).total_seconds() / 3600
            },
            "memory": memory_stats,
            "tools": tool_stats,
            "agent_info": {
                "id": self.agent_id,
                "persona": self.agent_loop.agent_persona,
                "model": self.agent_loop.model.get_model_info()
            }
        }
    
    async def run_interactive_session(self) -> None:
        """
        Run an interactive chat session in the terminal
        Useful for testing and development
        """
        print(f"🤖 AI Personal Assistant Agent ({self.agent_loop.agent_persona} mode)")
        print("💡 Type 'help' for commands, 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                user_input = await asyncio.to_thread(input, "\n👤 You: ")
                user_input = user_input.strip()
                
                if not user_input:
                    continue
                
                if self._handle_special_commands(user_input):
                    continue
                
                # Process message
                print("🤖 Assistant: ", end="", flush=True)
                response = await self.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """
        Handle special commands in interactive session
        
        Args:
            user_input: User input to check for commands
            
        Returns:
            True if command was handled, False otherwise
        """
        lower_input = user_input.lower()
        
        if lower_input in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            return False  # This will break the while loop
        
        if lower_input == 'help':
            self._show_help()
            return True
        
        if lower_input == 'status':
            self._show_status()
            return True
        
        if lower_input == 'clear':
            self.clear_memory("short_term")
            print("� Short-term memory cleared!")
            return True
        
        if lower_input.startswith('persona '):
            persona = user_input.split(' ', 1)[1]
            if self.set_persona(persona):
                print(f"🎭 Persona changed to: {persona}")
            else:
                print("❌ Invalid persona. Use: personal, research, or technical")
            return True
        
        return False
    
    def _show_help(self) -> None:
        """Show help information"""
        help_text = """
🤖 AI Personal Assistant Commands:
├── help          - Show this help message
├── status        - Show agent status
├── clear         - Clear short-term memory
├── persona <type> - Change persona (personal/research/technical)
├── quit/exit/bye - Exit the session
└── <message>     - Chat with the assistant

Available Tools: {tools}
Current Persona: {persona}
""".format(
            tools=", ".join(self.get_available_tools()),
            persona=self.agent_loop.agent_persona
        )
        print(help_text)
    
    def _show_status(self) -> None:
        """Show agent status"""
        status = self.get_agent_status()
        memory_summary = self.get_memory_summary()
        
        print(f"""
📊 Agent Status:
├── ID: {status['agent_id']}
├── Persona: {status['persona']}
├── Model: {status['model_info']['provider']} ({status['model_info']['model']})
├── State: {status['state']}
├── Interactions: {status['total_interactions']}
├── Uptime: {status['uptime_seconds']:.1f}s
└── Memory:
    ├── Short-term: {memory_summary['short_term']['message_count']} messages
    └── Long-term: {memory_summary['long_term']['total_memories']} memories
""")

# Convenience function for creating agent instances
def create_agent(model_type: str = None, persona: str = "personal") -> PersonalAssistantAgent:
    """
    Create a new AI agent instance
    
    Args:
        model_type: Model type ("openai" or "gemini")
        persona: Agent persona ("personal", "research", "technical")
        
    Returns:
        PersonalAssistantAgent instance
        
    Raises:
        ValueError: If model_type or persona is invalid
    """
    try:
        return PersonalAssistantAgent(model_type, persona)
    except Exception as e:
        log_error(e, {"model_type": model_type, "persona": persona}, "create_agent")
        raise
