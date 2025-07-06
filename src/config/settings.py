"""
Configuration settings for the AI Agent
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    
    # Agent Configuration
    AGENT_NAME: str = os.getenv("AGENT_NAME", "PersonalAssistant")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "openai")
    MEMORY_PERSIST_PATH: str = os.getenv("MEMORY_PERSIST_PATH", "./data/memory")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database Configuration
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vectordb")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "./data/agent.db")
    
    # Model Configuration
    OPENAI_MODEL: str = "gpt-4"
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Updated to working model
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # Memory Configuration
    STM_MAX_MESSAGES: int = 20
    LTM_SIMILARITY_THRESHOLD: float = 0.7
    VECTOR_EMBEDDING_SIZE: int = 1536
    
    @classmethod
    def validate_api_keys(cls) -> bool:
        """Validate that required API keys are present and look valid"""
        if cls.DEFAULT_MODEL == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI model")
            if "dummy" in cls.OPENAI_API_KEY.lower() or "test" in cls.OPENAI_API_KEY.lower() or not cls.OPENAI_API_KEY.startswith("sk-"):
                raise ValueError("OPENAI_API_KEY appears to be a dummy/test key. Please provide a valid OpenAI API key.")
                
        if cls.DEFAULT_MODEL == "gemini":
            if not cls.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY is required when using Gemini model")
            if "dummy" in cls.GOOGLE_API_KEY.lower() or "test" in cls.GOOGLE_API_KEY.lower() or not cls.GOOGLE_API_KEY.startswith("AIza"):
                raise ValueError("GOOGLE_API_KEY appears to be a dummy/test key. Please provide a valid Google API key.")
                
        return True
    
    @classmethod
    def is_api_key_valid(cls, model_type: str = None) -> bool:
        """Check if API key is valid for the given model type"""
        model = model_type or cls.DEFAULT_MODEL
        
        try:
            if model == "openai":
                return (cls.OPENAI_API_KEY and 
                       cls.OPENAI_API_KEY.startswith("sk-") and 
                       len(cls.OPENAI_API_KEY) > 20 and
                       "dummy" not in cls.OPENAI_API_KEY.lower() and
                       "test" not in cls.OPENAI_API_KEY.lower())
            elif model == "gemini":
                return (cls.GOOGLE_API_KEY and 
                       cls.GOOGLE_API_KEY.startswith("AIza") and 
                       len(cls.GOOGLE_API_KEY) > 30 and
                       "dummy" not in cls.GOOGLE_API_KEY.lower() and
                       "test" not in cls.GOOGLE_API_KEY.lower())
            return False
        except:
            return False

# Global settings instance
settings = Settings()
