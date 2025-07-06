"""
Short-term Memory (STM) implementation for the AI Agent
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from collections import deque
from ..config import settings

class ShortTermMemory:
    """
    Short-term memory implementation using in-memory storage
    Stores recent conversation history and context
    """
    
    def __init__(self, max_messages: int = None):
        self.max_messages = max_messages or settings.STM_MAX_MESSAGES
        self.messages = deque(maxlen=self.max_messages)
        self.context = {}
        self.session_start = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to short-term memory
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Message content
            metadata: Additional metadata for the message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent messages from short-term memory
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        if limit:
            return list(self.messages)[-limit:]
        return list(self.messages)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history in format suitable for LLM
        
        Returns:
            List of messages with role and content only
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]
    
    def update_context(self, key: str, value: Any) -> None:
        """
        Update context information
        
        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
    
    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Get context information
        
        Args:
            key: Context key (if None, returns all context)
            
        Returns:
            Context value or entire context dict
        """
        if key:
            return self.context.get(key)
        return self.context.copy()
    
    def clear_messages(self) -> None:
        """Clear all messages from short-term memory"""
        self.messages.clear()
    
    def clear_context(self) -> None:
        """Clear all context from short-term memory"""
        self.context.clear()
    
    def clear_all(self) -> None:
        """Clear all data from short-term memory"""
        self.clear_messages()
        self.clear_context()
        self.session_start = datetime.now()
    
    def get_session_duration(self) -> float:
        """
        Get session duration in seconds
        
        Returns:
            Session duration in seconds
        """
        return (datetime.now() - self.session_start).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of short-term memory
        
        Returns:
            Summary dictionary
        """
        return {
            "message_count": len(self.messages),
            "max_messages": self.max_messages,
            "context_keys": list(self.context.keys()),
            "session_duration_seconds": self.get_session_duration(),
            "session_start": self.session_start.isoformat()
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export STM data to dictionary
        
        Returns:
            Dictionary representation of STM
        """
        return {
            "messages": list(self.messages),
            "context": self.context,
            "session_start": self.session_start.isoformat(),
            "max_messages": self.max_messages
        }
    
    def import_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Import STM data from dictionary
        
        Args:
            data: Dictionary representation of STM
        """
        self.messages.clear()
        for msg in data.get("messages", []):
            self.messages.append(msg)
        
        self.context = data.get("context", {})
        self.session_start = datetime.fromisoformat(
            data.get("session_start", datetime.now().isoformat())
        )
