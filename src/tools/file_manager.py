"""
File manager tool for AI Agent
"""
import os
import asyncio
import aiofiles
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base_tool import BaseTool, ToolResult

class FileManagerTool(BaseTool):
    """Tool for basic file operations"""
    
    ACCESS_DENIED_ERROR = "Access denied: path not allowed"
    
    def __init__(self, allowed_paths: Optional[List[str]] = None):
        super().__init__(
            name="file_manager",
            description="Perform basic file operations like reading, writing, listing files and directories"
        )
        # Security: restrict operations to allowed paths
        self.allowed_paths = allowed_paths or [
            os.getcwd(),  # Current working directory
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Desktop"),
        ]
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute file operation
        
        Args:
            operation: Type of operation (read, write, list, create_dir, delete)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation result
        """
        try:
            if operation == "read":
                return await self._read_file(kwargs.get("file_path"))
            elif operation == "write":
                return await self._write_file(
                    kwargs.get("file_path"), 
                    kwargs.get("content")
                )
            elif operation == "list":
                return await self._list_directory(kwargs.get("directory_path"))
            elif operation == "create_dir":
                return await self._create_directory(kwargs.get("directory_path"))
            elif operation == "delete":
                return await self._delete_file(kwargs.get("file_path"))
            elif operation == "exists":
                return await self._check_exists(kwargs.get("path"))
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Unknown operation: {operation}"
                )
                
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"File operation failed: {str(e)}"
            )
    
    def _is_path_allowed(self, path: str) -> bool:
        """
        Check if path is within allowed directories
        
        Args:
            path: Path to check
            
        Returns:
            True if path is allowed
        """
        abs_path = os.path.abspath(path)
        
        for allowed_path in self.allowed_paths:
            abs_allowed = os.path.abspath(allowed_path)
            if abs_path.startswith(abs_allowed):
                return True
        
        return False
    
    async def _read_file(self, file_path: str) -> ToolResult:
        """Read file content"""
        if not file_path:
            return ToolResult(
                success=False,
                result=None,
                error="File path is required"
            )
        
        if not self._is_path_allowed(file_path):
            return ToolResult(
                success=False,
                result=None,
                error="Access denied: path not allowed"
            )
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
                
            return ToolResult(
                success=True,
                result={
                    "file_path": file_path,
                    "content": content,
                    "size": len(content)
                },
                metadata={"operation": "read"}
            )
            
        except FileNotFoundError:
            return ToolResult(
                success=False,
                result=None,
                error="File not found"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to read file: {str(e)}"
            )
    
    async def _write_file(self, file_path: str, content: str) -> ToolResult:
        """Write content to file"""
        if not file_path or content is None:
            return ToolResult(
                success=False,
                result=None,
                error="File path and content are required"
            )
        
        if not self._is_path_allowed(file_path):
            return ToolResult(
                success=False,
                result=None,
                error="Access denied: path not allowed"
            )
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
                await file.write(content)
                
            return ToolResult(
                success=True,
                result={
                    "file_path": file_path,
                    "bytes_written": len(content.encode('utf-8'))
                },
                metadata={"operation": "write"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to write file: {str(e)}"
            )
    
    async def _list_directory(self, directory_path: str) -> ToolResult:
        """List directory contents"""
        if not directory_path:
            directory_path = os.getcwd()
        
        if not self._is_path_allowed(directory_path):
            return ToolResult(
                success=False,
                result=None,
                error="Access denied: path not allowed"
            )
        
        try:
            items = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                is_dir = os.path.isdir(item_path)
                
                items.append({
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "size": os.path.getsize(item_path) if not is_dir else None,
                    "modified": os.path.getmtime(item_path)
                })
            
            return ToolResult(
                success=True,
                result={
                    "directory": directory_path,
                    "items": items,
                    "count": len(items)
                },
                metadata={"operation": "list"}
            )
            
        except FileNotFoundError:
            return ToolResult(
                success=False,
                result=None,
                error="Directory not found"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to list directory: {str(e)}"
            )
    
    async def _create_directory(self, directory_path: str) -> ToolResult:
        """Create directory"""
        if not directory_path:
            return ToolResult(
                success=False,
                result=None,
                error="Directory path is required"
            )
        
        if not self._is_path_allowed(directory_path):
            return ToolResult(
                success=False,
                result=None,
                error="Access denied: path not allowed"
            )
        
        try:
            os.makedirs(directory_path, exist_ok=True)
            
            return ToolResult(
                success=True,
                result={
                    "directory_path": directory_path,
                    "created": True
                },
                metadata={"operation": "create_dir"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to create directory: {str(e)}"
            )
    
    async def _delete_file(self, file_path: str) -> ToolResult:
        """Delete file"""
        if not file_path:
            return ToolResult(
                success=False,
                result=None,
                error="File path is required"
            )
        
        if not self._is_path_allowed(file_path):
            return ToolResult(
                success=False,
                result=None,
                error="Access denied: path not allowed"
            )
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                operation_type = "file"
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Only removes empty directories
                operation_type = "directory"
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error="Path does not exist"
                )
            
            return ToolResult(
                success=True,
                result={
                    "path": file_path,
                    "deleted": True,
                    "type": operation_type
                },
                metadata={"operation": "delete"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to delete: {str(e)}"
            )
    
    async def _check_exists(self, path: str) -> ToolResult:
        """Check if path exists"""
        if not path:
            return ToolResult(
                success=False,
                result=None,
                error="Path is required"
            )
        
        try:
            exists = os.path.exists(path)
            is_file = os.path.isfile(path) if exists else False
            is_dir = os.path.isdir(path) if exists else False
            
            return ToolResult(
                success=True,
                result={
                    "path": path,
                    "exists": exists,
                    "is_file": is_file,
                    "is_directory": is_dir
                },
                metadata={"operation": "exists"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                result=None,
                error=f"Failed to check path: {str(e)}"
            )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get parameters schema for file manager tool"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "File operation to perform",
                    "enum": ["read", "write", "list", "create_dir", "delete", "exists"]
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file (for read, write, delete operations)"
                },
                "directory_path": {
                    "type": "string",
                    "description": "Path to the directory (for list, create_dir operations)"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to file (for write operation)"
                },
                "path": {
                    "type": "string",
                    "description": "Path to check (for exists operation)"
                }
            },
            "required": ["operation"]
        }
