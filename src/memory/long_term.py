"""
Long-term Memory (LTM) implementation for the AI Agent using vector database
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
import sqlite3
import json
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from ..config import settings

class LongTermMemory:
    """
    Long-term memory implementation using vector database and SQLite
    Stores important conversations, facts, and user preferences
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or settings.VECTOR_DB_PATH
        self.db_path = settings.SQLITE_DB_PATH
        
        # Ensure directories exist
        os.makedirs(self.persist_directory, exist_ok=True)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None
        
        # Initialize vector store
        self.vector_store = None
        if self.embeddings:
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        
        # Initialize SQLite database
        self._init_sqlite_db()
    
    def _init_sqlite_db(self) -> None:
        """Initialize SQLite database for structured data storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance_score REAL DEFAULT 0.5,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Create user_preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create facts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact_content TEXT NOT NULL,
                    category TEXT,
                    confidence_score REAL DEFAULT 0.5,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.commit()
    
    def store_memory(
        self, 
        content: str, 
        memory_type: str = "conversation",
        importance_score: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store a memory in long-term storage
        
        Args:
            content: Memory content
            memory_type: Type of memory (conversation, fact, preference, etc.)
            importance_score: Importance score (0.0 to 1.0)
            tags: List of tags for categorization
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        # Store in vector database for semantic search
        if self.vector_store:
            doc = Document(
                page_content=content,
                metadata={
                    "memory_type": memory_type,
                    "importance_score": importance_score,
                    "tags": tags or [],
                    "created_at": datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            self.vector_store.add_documents([doc])
            self.vector_store.persist()
        
        # Store in SQLite for structured queries
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (content, memory_type, importance_score, tags, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                content,
                memory_type,
                importance_score,
                json.dumps(tags) if tags else None,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            return cursor.lastrowid
    
    def search_memories(
        self, 
        query: str, 
        limit: int = 5,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity
        
        Args:
            query: Search query
            limit: Maximum number of results
            memory_type: Filter by memory type
            min_importance: Minimum importance score
            
        Returns:
            List of matching memories
        """
        if not self.vector_store:
            return []
        
        try:
            # Perform semantic search
            docs = self.vector_store.similarity_search(
                query, 
                k=limit,
                filter={
                    "memory_type": memory_type,
                    "importance_score": {"$gte": min_importance}
                } if memory_type else {"importance_score": {"$gte": min_importance}}
            )
            
            memories = []
            for doc in docs:
                memories.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": getattr(doc, 'relevance_score', 0.0)
                })
            
            return memories
            
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def store_user_preference(self, key: str, value: str) -> None:
        """
        Store user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (preference_key, preference_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
    
    def get_user_preference(self, key: str) -> Optional[str]:
        """
        Get user preference
        
        Args:
            key: Preference key
            
        Returns:
            Preference value or None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT preference_value FROM user_preferences WHERE preference_key = ?
            """, (key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def store_fact(
        self, 
        fact_content: str, 
        category: Optional[str] = None,
        confidence_score: float = 0.5,
        source: Optional[str] = None
    ) -> int:
        """
        Store a fact in long-term memory
        
        Args:
            fact_content: Content of the fact
            category: Fact category
            confidence_score: Confidence in the fact (0.0 to 1.0)
            source: Source of the fact
            
        Returns:
            Fact ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO facts (fact_content, category, confidence_score, source)
                VALUES (?, ?, ?, ?)
            """, (fact_content, category, confidence_score, source))
            conn.commit()
            return cursor.lastrowid
    
    def get_facts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get facts by category
        
        Args:
            category: Fact category
            
        Returns:
            List of facts
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM facts WHERE category = ? ORDER BY confidence_score DESC
            """, (category,))
            
            facts = []
            for row in cursor.fetchall():
                facts.append({
                    "id": row[0],
                    "content": row[1],
                    "category": row[2],
                    "confidence_score": row[3],
                    "source": row[4],
                    "created_at": row[5],
                    "verified": bool(row[6])
                })
            
            return facts
    
    def update_memory_access(self, memory_id: int) -> None:
        """
        Update memory access statistics
        
        Args:
            memory_id: Memory ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE memories 
                SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                WHERE id = ?
            """, (memory_id,))
            conn.commit()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Dictionary with memory statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get memory counts by type
            cursor.execute("""
                SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type
            """)
            memory_counts = dict(cursor.fetchall())
            
            # Get total memories
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]
            
            # Get total preferences
            cursor.execute("SELECT COUNT(*) FROM user_preferences")
            total_preferences = cursor.fetchone()[0]
            
            # Get total facts
            cursor.execute("SELECT COUNT(*) FROM facts")
            total_facts = cursor.fetchone()[0]
            
            return {
                "total_memories": total_memories,
                "memory_counts_by_type": memory_counts,
                "total_preferences": total_preferences,
                "total_facts": total_facts,
                "vector_store_enabled": self.vector_store is not None
            }
