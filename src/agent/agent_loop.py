"""
Agent Loop implementation - Observe-Decide-Act pattern
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

from ..memory import MemoryManager
from ..tools import get_all_tools, ToolResult
from ..models import OpenAIModel, GeminiModel
from ..prompts import SystemPrompts
from ..config import settings

class AgentState(Enum):
    """Agent states in the observe-decide-act loop"""
    IDLE = "idle"
    OBSERVING = "observing"
    DECIDING = "deciding"
    ACTING = "acting"
    REFLECTING = "reflecting"

@dataclass
class Observation:
    """Represents an observation made by the agent"""
    user_input: str
    context: Dict[str, Any]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Decision:
    """Represents a decision made by the agent"""
    action_type: str  # "respond", "use_tool", "store_memory", "ask_clarification"
    action_details: Dict[str, Any]
    reasoning: str
    confidence: float
    timestamp: datetime

@dataclass
class Action:
    """Represents an action taken by the agent"""
    action_type: str
    parameters: Dict[str, Any]
    result: Any
    success: bool
    timestamp: datetime
    execution_time: float

class AgentLoop:
    """
    Core agent loop implementing observe-decide-act pattern
    """
    
    def __init__(self, model_type: str = None):
        self.state = AgentState.IDLE
        self.memory_manager = MemoryManager()
        self.tools = {tool.name: tool for tool in get_all_tools()}
        
        # Initialize model
        model_type = model_type or settings.DEFAULT_MODEL
        supported_models = ["openai", "gemini"]
        
        if model_type not in supported_models:
            raise ValueError(f"Unsupported model type: {model_type}. Supported models: {supported_models}")
        
        if model_type == "openai":
            self.model = OpenAIModel()
        elif model_type == "gemini":
            self.model = GeminiModel()
        else:
            # This should never happen due to the check above, but kept for safety
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Agent configuration
        self.max_iterations = 10
        self.current_iteration = 0
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Agent persona
        self.agent_persona = "personal"  # personal, research, technical
        
    async def process_user_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Main entry point for processing user input through the agent loop
        
        Args:
            user_input: User's input message
            context: Additional context information
            
        Returns:
            Agent's response
        """
        try:
            self.current_iteration = 0
            
            # OBSERVE
            observation = self._observe(user_input, context or {})
            
            # DECIDE-ACT loop
            final_response = ""
            while self.current_iteration < self.max_iterations:
                self.current_iteration += 1
                
                # DECIDE
                decision = await self._decide(observation)
                
                # ACT
                action = await self._act(decision)
                
                # Check if we have a final response
                if action.action_type in ["respond", "ask_clarification"]:
                    final_response = action.result
                    break
                
                # Update observation with action results for next iteration
                observation.context.update({
                    "last_action": action,
                    "iteration": self.current_iteration
                })
            
            # REFLECT
            self._reflect(observation, final_response)
            
            return final_response or "I apologize, but I couldn't process your request completely."
            
        except Exception as e:
            self.logger.error(f"Error in agent loop: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _observe(self, user_input: str, context: Dict[str, Any]) -> Observation:
        """
        Observe phase: gather and process input information
        
        Args:
            user_input: User's input
            context: Context information
            
        Returns:
            Observation object
        """
        self.state = AgentState.OBSERVING
        
        # Add user message to memory
        self.memory_manager.add_user_message(user_input, metadata=context)
        
        # Enhance context with relevant information
        enhanced_context = {
            **context,
            "conversation_history": self.memory_manager.get_conversation_context(),
            "available_tools": list(self.tools.keys()),
            "agent_persona": self.agent_persona,
            "session_info": self.memory_manager.stm.get_summary()
        }
        
        # Search for relevant memories
        relevant_memories = self.memory_manager.search_memories(user_input, limit=3)
        if relevant_memories:
            enhanced_context["relevant_memories"] = relevant_memories
        
        return Observation(
            user_input=user_input,
            context=enhanced_context,
            timestamp=datetime.now(),
            metadata={"iteration": self.current_iteration}
        )
    
    async def _decide(self, observation: Observation) -> Decision:
        """
        Decide phase: analyze observation and decide on action
        
        Args:
            observation: Current observation
            
        Returns:
            Decision object
        """
        self.state = AgentState.DECIDING
        
        # Prepare decision-making prompt
        decision_prompt = self._create_decision_prompt()
        
        # Get decision from model
        try:
            messages = [
                {"role": "system", "content": decision_prompt},
                {"role": "user", "content": observation.user_input}
            ]
            
            decision_response = await self.model.generate_response(messages)
            
            # Parse decision (simplified - in production you'd want more robust parsing)
            decision_data = self._parse_decision_response(decision_response)
            
            return Decision(
                action_type=decision_data["action_type"],
                action_details=decision_data["action_details"],
                reasoning=decision_data["reasoning"],
                confidence=decision_data.get("confidence", 0.7),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error in decision phase: {e}")
            # Fallback decision
            return Decision(
                action_type="respond",
                action_details={"message": "I'm having trouble processing your request. Could you please rephrase it?"},
                reasoning="Error in decision making process",
                confidence=0.3,
                timestamp=datetime.now()
            )
    
    async def _act(self, decision: Decision) -> Action:
        """
        Act phase: execute the decided action
        
        Args:
            decision: Decision to execute
            
        Returns:
            Action object
        """
        self.state = AgentState.ACTING
        start_time = datetime.now()
        
        try:
            if decision.action_type == "use_tool":
                result = await self._execute_tool(decision.action_details)
                success = isinstance(result, ToolResult) and result.success
                
            elif decision.action_type == "respond":
                result = await self._generate_response(decision.action_details)
                success = True
                
            elif decision.action_type == "store_memory":
                result = self._store_important_memory(decision.action_details)
                success = True
                
            elif decision.action_type == "ask_clarification":
                result = decision.action_details.get("message", "Could you please provide more details?")
                success = True
                
            else:
                result = f"Unknown action type: {decision.action_type}"
                success = False
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return Action(
                action_type=decision.action_type,
                parameters=decision.action_details,
                result=result,
                success=success,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Error in action phase: {e}")
            
            return Action(
                action_type=decision.action_type,
                parameters=decision.action_details,
                result=f"Action failed: {str(e)}",
                success=False,
                timestamp=datetime.now(),
                execution_time=execution_time
            )
    
    def _reflect(self, observation: Observation, final_response: str) -> None:
        """
        Reflect phase: analyze the interaction and learn
        
        Args:
            observation: Original observation
            final_response: Final response given to user
        """
        self.state = AgentState.REFLECTING
        
        # Add assistant response to memory
        self.memory_manager.add_assistant_message(final_response)
        
        # Check if this interaction should be stored in long-term memory
        if self._should_store_interaction(observation):
            interaction_summary = self._create_interaction_summary(observation, final_response)
            self.memory_manager.store_important_memory(
                content=interaction_summary,
                memory_type="interaction",
                importance_score=0.7,
                tags=["user_interaction", self.agent_persona]
            )
        
        self.state = AgentState.IDLE
    
    def _create_decision_prompt(self) -> str:
        """Create prompt for decision making"""
        base_prompt = SystemPrompts.get_system_prompt(self.agent_persona)
        
        tool_info = SystemPrompts.get_tool_instruction_prompt(list(self.tools.keys()))
        
        decision_instructions = """
DECISION MAKING INSTRUCTIONS:
Analyze the user's request and decide on the best action. You must choose ONE of these action types:

1. "use_tool" - Use a specific tool to gather information or perform a task
   - Specify tool_name and parameters
   - Use when you need current information, calculations, or specific capabilities

2. "respond" - Provide a direct response to the user
   - Use when you have sufficient information to answer
   - Include the complete response message

3. "store_memory" - Store important information for future reference
   - Use when user shares personal information or preferences
   - Specify what to store and why it's important

4. "ask_clarification" - Ask for more details or clarification
   - Use when the request is ambiguous or lacks necessary details
   - Provide a helpful clarification question

Format your decision as:
ACTION_TYPE: [action_type]
REASONING: [explanation of why you chose this action]
DETAILS: [specific parameters for the action]
CONFIDENCE: [0.0-1.0]
"""
        
        return f"{base_prompt}\n\n{tool_info}\n\n{decision_instructions}"
    
    def _parse_decision_response(self, response: str) -> Dict[str, Any]:
        """Parse decision response from model"""
        try:
            # Simple parsing - in production you'd want more robust parsing
            lines = response.strip().split('\n')
            decision_data = {
                "action_type": "respond",
                "action_details": {"message": "I need more information to help you."},
                "reasoning": "Default fallback decision",
                "confidence": 0.5
            }
            
            for line in lines:
                if line.startswith("ACTION_TYPE:"):
                    action_type = line.split(":", 1)[1].strip()
                    decision_data["action_type"] = action_type
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
                    decision_data["reasoning"] = reasoning
                elif line.startswith("DETAILS:"):
                    details_str = line.split(":", 1)[1].strip()
                    # Try to parse as JSON, fallback to simple parsing
                    try:
                        details = json.loads(details_str)
                    except Exception:
                        details = {"message": details_str}
                    decision_data["action_details"] = details
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                        decision_data["confidence"] = max(0.0, min(1.0, confidence))
                    except Exception:
                        pass
            
            # Validate and adjust decision
            if decision_data["action_type"] not in ["use_tool", "respond", "store_memory", "ask_clarification"]:
                decision_data["action_type"] = "respond"
                decision_data["action_details"] = {"message": response}
            
            return decision_data
            
        except Exception as e:
            self.logger.error(f"Error parsing decision: {e}")
            return {
                "action_type": "respond",
                "action_details": {"message": response},
                "reasoning": "Fallback due to parsing error",
                "confidence": 0.3
            }
    
    async def _execute_tool(self, action_details: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given parameters"""
        tool_name = action_details.get("tool_name")
        parameters = action_details.get("parameters", {})
        
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools[tool_name]
        return await tool.safe_execute(**parameters)
    
    async def _generate_response(self, action_details: Dict[str, Any]) -> str:
        """Generate final response to user"""
        message = action_details.get("message", "")
        
        # If the message is not complete, generate it using the model
        if not message or len(message) < 10:
            context_messages = self.memory_manager.get_conversation_context()
            response = await self.model.generate_response(context_messages)
            return response
        
        return message
    
    def _store_important_memory(self, action_details: Dict[str, Any]) -> str:
        """Store important information in long-term memory"""
        content = action_details.get("content", "")
        memory_type = action_details.get("memory_type", "user_info")
        importance = action_details.get("importance", 0.7)
        
        memory_id = self.memory_manager.store_important_memory(
            content=content,
            memory_type=memory_type,
            importance_score=importance
        )
        
        return f"Stored important information with ID: {memory_id}"
    
    def _should_store_interaction(self, observation: Observation) -> bool:
        """Determine if interaction should be stored in long-term memory"""
        # Store if user provided personal information
        personal_keywords = ["my name", "i am", "i like", "i prefer", "remember", "important"]
        user_input_lower = observation.user_input.lower()
        
        return any(keyword in user_input_lower for keyword in personal_keywords)
    
    def _create_interaction_summary(self, observation: Observation, response: str) -> str:
        """Create summary of interaction for storage"""
        return f"User: {observation.user_input}\nAssistant: {response}"
    
    def set_persona(self, persona: str) -> None:
        """Set agent persona (personal, research, technical)"""
        valid_personas = ["personal", "research", "technical"]
        if persona in valid_personas:
            self.agent_persona = persona
        else:
            raise ValueError(f"Invalid persona: {persona}. Valid personas: {valid_personas}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "state": self.state.value,
            "persona": self.agent_persona,
            "iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "available_tools": list(self.tools.keys()),
            "memory_summary": self.memory_manager.get_memory_summary(),
            "model_info": self.model.get_model_info()
        }
