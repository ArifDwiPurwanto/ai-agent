"""
Memory Manager - Coordinates STM and LTM operations
"""
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from ..config import settings

class MemoryManager:
    """
    Manages both short-term and long-term memory systems
    Handles memory consolidation and retrieval
    """
    
    def __init__(self):
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.consolidation_threshold = 10  # Messages before considering consolidation
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add user message to STM"""
        self.stm.add_message("user", content, metadata)
        self._check_consolidation()
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add assistant message to STM"""
        self.stm.add_message("assistant", content, metadata)
        self._check_consolidation()
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add system message to STM"""
        self.stm.add_message("system", content, metadata)
    
    def get_conversation_context(self, include_ltm: bool = True) -> List[Dict[str, str]]:
        """
        Get conversation context for LLM
        
        Args:
            include_ltm: Whether to include relevant long-term memories
            
        Returns:
            List of messages for LLM context
        """
        context = []
        
        # Add relevant long-term memories if requested
        if include_ltm:
            recent_messages = self.stm.get_messages(limit=3)
            if recent_messages:
                # Search for relevant memories based on recent conversation
                search_query = " ".join([msg["content"] for msg in recent_messages])
                relevant_memories = self.ltm.search_memories(
                    search_query, 
                    limit=3, 
                    min_importance=0.6
                )
                
                if relevant_memories:
                    memory_context = "Relevant context from previous conversations:\n"
                    for memory in relevant_memories:
                        memory_context += f"- {memory['content']}\n"
                    
                    context.append({
                        "role": "system",
                        "content": memory_context
                    })
        
        # Add short-term conversation history
        context.extend(self.stm.get_conversation_history())
        
        return context
    
    def store_important_memory(
        self, 
        content: str, 
        memory_type: str = "conversation",
        importance_score: float = 0.7,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Store important information in long-term memory
        
        Args:
            content: Memory content
            memory_type: Type of memory
            importance_score: Importance score
            tags: Memory tags
            
        Returns:
            Memory ID
        """
        return self.ltm.store_memory(
            content=content,
            memory_type=memory_type,
            importance_score=importance_score,
            tags=tags
        )
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search long-term memories"""
        return self.ltm.search_memories(query, limit=limit)
    
    def store_user_preference(self, key: str, value: str) -> None:
        """Store user preference in long-term memory"""
        self.ltm.store_user_preference(key, value)
        
        # Also update STM context
        self.stm.update_context(f"user_pref_{key}", value)
    
    def get_user_preference(self, key: str) -> Optional[str]:
        """Get user preference from long-term memory"""
        return self.ltm.get_user_preference(key)
    
    def store_fact(
        self, 
        fact_content: str, 
        category: Optional[str] = None,
        confidence_score: float = 0.5
    ) -> int:
        """Store a fact in long-term memory"""
        return self.ltm.store_fact(
            fact_content=fact_content,
            category=category,
            confidence_score=confidence_score
        )
    
    def _check_consolidation(self) -> None:
        """
        Check if memory consolidation is needed
        Move important STM content to LTM
        """
        if len(self.stm.messages) >= self.consolidation_threshold:
            self._consolidate_memories()
    
    def _consolidate_memories(self) -> None:
        """
        Consolidate memories from STM to LTM
        Identify important conversations and store them
        """
        messages = self.stm.get_messages()
        
        # Group messages into conversation chunks
        conversation_chunks = self._group_messages_into_chunks(messages)
        
        for chunk in conversation_chunks:
            # Calculate importance score based on various factors
            importance_score = self._calculate_importance_score(chunk)
            
            if importance_score > 0.5:  # Only store moderately important conversations
                conversation_text = "\n".join([
                    f"{msg['role']}: {msg['content']}" for msg in chunk
                ])
                
                # Extract tags from conversation
                tags = self._extract_tags_from_conversation(chunk)
                
                # Store in LTM
                self.ltm.store_memory(
                    content=conversation_text,
                    memory_type="conversation",
                    importance_score=importance_score,
                    tags=tags,
                    metadata={
                        "message_count": len(chunk),
                        "consolidated_at": datetime.now().isoformat()
                    }
                )
    
    def _group_messages_into_chunks(self, messages: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group messages into conversation chunks"""
        chunks = []
        current_chunk = []
        
        for message in messages:
            current_chunk.append(message)
            
            # Start new chunk based on conditions
            should_create_new_chunk = (
                (message["role"] == "assistant" and len(current_chunk) >= 2) or
                len(current_chunk) >= 5
            )
            
            if should_create_new_chunk:
                chunks.append(current_chunk)
                current_chunk = []
        
        # Add remaining messages
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _calculate_importance_score(self, chunk: List[Dict[str, Any]]) -> float:
        """
        Calculate importance score for a conversation chunk
        
        Args:
            chunk: List of messages in the chunk
            
        Returns:
            Importance score between 0.0 and 1.0
        """
        score = 0.5  # Base score
        
        # Increase score for longer conversations
        if len(chunk) > 3:
            score += 0.1
        
        # Increase score for conversations with questions
        question_keywords = ["how", "what", "when", "where", "why", "can you", "help me"]
        for message in chunk:
            content = message["content"].lower()
            if any(keyword in content for keyword in question_keywords):
                score += 0.1
                break
        
        # Increase score for conversations with personal information
        personal_keywords = ["my name", "i am", "i like", "i prefer", "remember"]
        for message in chunk:
            content = message["content"].lower()
            if any(keyword in content for keyword in personal_keywords):
                score += 0.2
                break
        
        # Increase score for longer messages (more detailed conversations)
        avg_length = sum(len(msg["content"]) for msg in chunk) / len(chunk)
        if avg_length > 100:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _extract_tags_from_conversation(self, chunk: List[Dict[str, Any]]) -> List[str]:
        """Extract tags from conversation chunk"""
        tags = []
        
        # Combine all message content
        text = " ".join([msg["content"].lower() for msg in chunk])
        
        # Define tag keywords
        tag_keywords = {
            "personal": ["my name", "i am", "about me", "personal"],
            "preference": ["i like", "i prefer", "favorite", "don't like"],
            "question": ["how", "what", "when", "where", "why"],
            "help": ["help", "assist", "support", "problem"],
            "information": ["tell me", "explain", "describe", "information"],
            "task": ["do", "create", "make", "generate", "write"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def clear_stm(self) -> None:
        """Clear short-term memory"""
        self.stm.clear_all()
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory systems"""
        stm_summary = self.stm.get_summary()
        ltm_stats = self.ltm.get_memory_stats()
        
        return {
            "short_term": stm_summary,
            "long_term": ltm_stats,
            "consolidation_threshold": self.consolidation_threshold
        }
