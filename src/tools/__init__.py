"""Tools module for AI Agent"""
from .base_tool import BaseTool, ToolResult
from .web_search import WebSearchTool
from .calculator import CalculatorTool
from .weather import WeatherTool
from .file_manager import FileManagerTool

# Tool registry
AVAILABLE_TOOLS = {
    "web_search": WebSearchTool,
    "calculator": CalculatorTool,
    "get_weather": WeatherTool,
    "file_manager": FileManagerTool,
}

def get_all_tools():
    """Get instances of all available tools"""
    return [tool_class() for tool_class in AVAILABLE_TOOLS.values()]

def get_tool_by_name(name: str):
    """Get tool instance by name"""
    if name in AVAILABLE_TOOLS:
        return AVAILABLE_TOOLS[name]()
    return None

__all__ = [
    "BaseTool", 
    "ToolResult", 
    "WebSearchTool", 
    "CalculatorTool", 
    "WeatherTool", 
    "FileManagerTool",
    "AVAILABLE_TOOLS",
    "get_all_tools",
    "get_tool_by_name"
]
