"""
Base tool class for AI Agent tools
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    """Result returned by a tool execution"""
    success: bool = Field(description="Whether the tool execution was successful")
    result: Any = Field(description="The result of the tool execution")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class BaseTool(ABC):
    """
    Abstract base class for all AI Agent tools
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.usage_count = 0
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult object
        """
        pass
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the parameters schema for this tool
        
        Returns:
            JSON schema for tool parameters
        """
        pass
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get tool information for LLM function calling
        
        Returns:
            Tool information dictionary
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema()
            }
        }
    
    def increment_usage(self) -> None:
        """Increment usage counter"""
        self.usage_count += 1
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "name": self.name,
            "usage_count": self.usage_count
        }
    
    async def safe_execute(self, **kwargs) -> ToolResult:
        """
        Safely execute the tool with error handling
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult object
        """
        try:
            self.increment_usage()
            result = await self.execute(**kwargs)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool execution failed: {str(e)}"
            )
