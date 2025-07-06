"""
Advanced logging system for AI Agent
Organizes logs by type, date, and severity
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import traceback
import json
from typing import Dict, Any, Optional

class AgentLogger:
    """Enhanced logging system for AI Agent with organized file structure"""
    
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.error_dir = self.log_dir / "errors"
        self.debug_dir = self.log_dir / "debug"
        self.chat_dir = self.log_dir / "chat"
        self.performance_dir = self.log_dir / "performance"
        
        for dir_path in [self.error_dir, self.debug_dir, self.chat_dir, self.performance_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.setup_loggers()
    
    def setup_loggers(self):
        """Setup different loggers for different purposes"""
        
        # Remove existing handlers to avoid duplication
        for logger_name in ['agent.error', 'agent.debug', 'agent.chat', 'agent.performance']:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
        
        # Date for filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Error logger - for exceptions and critical errors
        self.error_logger = logging.getLogger('agent.error')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(
            self.error_dir / f"errors_{date_str}.log",
            encoding='utf-8'
        )
        error_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Debug logger - for detailed debugging information
        self.debug_logger = logging.getLogger('agent.debug')
        self.debug_logger.setLevel(logging.DEBUG)
        debug_handler = logging.FileHandler(
            self.debug_dir / f"debug_{date_str}.log",
            encoding='utf-8'
        )
        debug_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        debug_handler.setFormatter(debug_formatter)
        self.debug_logger.addHandler(debug_handler)
        
        # Chat logger - for conversation logs
        self.chat_logger = logging.getLogger('agent.chat')
        self.chat_logger.setLevel(logging.INFO)
        chat_handler = logging.FileHandler(
            self.chat_dir / f"chat_{date_str}.log",
            encoding='utf-8'
        )
        chat_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        chat_handler.setFormatter(chat_formatter)
        self.chat_logger.addHandler(chat_handler)
        
        # Performance logger - for timing and performance metrics
        self.perf_logger = logging.getLogger('agent.performance')
        self.perf_logger.setLevel(logging.INFO)
        perf_handler = logging.FileHandler(
            self.performance_dir / f"performance_{date_str}.log",
            encoding='utf-8'
        )
        perf_formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        perf_handler.setFormatter(perf_formatter)
        self.perf_logger.addHandler(perf_handler)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, module: str = "unknown"):
        """Log error with full traceback and context"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "module": module,
            "context": context or {}
        }
        
        self.error_logger.error(json.dumps(error_info, indent=2, ensure_ascii=False))
        
        # Also create individual error file for critical errors
        if isinstance(error, (ConnectionError, TimeoutError, ValueError)):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file = self.error_dir / f"critical_error_{timestamp}.json"
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_info, f, indent=2, ensure_ascii=False)
    
    def log_debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Log debug information"""
        if data:
            debug_entry = {
                "message": message,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            self.debug_logger.debug(json.dumps(debug_entry, ensure_ascii=False))
        else:
            self.debug_logger.debug(message)
    
    def log_chat(self, user_message: str, agent_response: str, metadata: Optional[Dict[str, Any]] = None):
        """Log chat interactions"""
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }
        self.chat_logger.info(json.dumps(chat_entry, ensure_ascii=False))
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        perf_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "duration_seconds": duration,
            "details": details or {}
        }
        self.perf_logger.info(json.dumps(perf_entry, ensure_ascii=False))
    
    def log_api_call(self, api_name: str, success: bool, response_time: float, error: Optional[str] = None):
        """Log API calls with timing and success status"""
        api_entry = {
            "timestamp": datetime.now().isoformat(),
            "api": api_name,
            "success": success,
            "response_time_ms": response_time * 1000,
            "error": error
        }
        
        if success:
            self.debug_logger.info(f"API_CALL_SUCCESS: {json.dumps(api_entry, ensure_ascii=False)}")
        else:
            self.error_logger.error(f"API_CALL_FAILED: {json.dumps(api_entry, ensure_ascii=False)}")
    
    def log_agent_lifecycle(self, event: str, details: Optional[Dict[str, Any]] = None):
        """Log agent lifecycle events (initialization, shutdown, etc.)"""
        lifecycle_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "details": details or {}
        }
        self.debug_logger.info(f"LIFECYCLE: {json.dumps(lifecycle_entry, ensure_ascii=False)}")
    
    def create_error_summary(self) -> Dict[str, Any]:
        """Create a summary of recent errors for debugging"""
        today = datetime.now().strftime("%Y-%m-%d")
        error_file = self.error_dir / f"errors_{today}.log"
        
        if not error_file.exists():
            return {"message": "No errors today", "count": 0}
        
        error_count = 0
        error_types = {}
        
        try:
            with open(error_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            error_data = json.loads(line)
                            error_type = error_data.get('error_type', 'Unknown')
                            error_types[error_type] = error_types.get(error_type, 0) + 1
                            error_count += 1
                        except json.JSONDecodeError:
                            continue
        except Exception:
            return {"message": "Error reading log file", "count": 0}
        
        return {
            "total_errors": error_count,
            "error_types": error_types,
            "log_file": str(error_file)
        }

# Global logger instance
agent_logger = AgentLogger()

# Convenience functions
def log_error(error: Exception, context: Optional[Dict[str, Any]] = None, module: str = "unknown"):
    """Log error with context"""
    agent_logger.log_error(error, context, module)

def log_debug(message: str, data: Optional[Dict[str, Any]] = None):
    """Log debug message"""
    agent_logger.log_debug(message, data)

def log_chat(user_message: str, agent_response: str, metadata: Optional[Dict[str, Any]] = None):
    """Log chat interaction"""
    agent_logger.log_chat(user_message, agent_response, metadata)

def log_performance(operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
    """Log performance metric"""
    agent_logger.log_performance(operation, duration, details)

def log_api_call(api_name: str, success: bool, response_time: float, error: Optional[str] = None):
    """Log API call"""
    agent_logger.log_api_call(api_name, success, response_time, error)

def log_agent_lifecycle(event: str, details: Optional[Dict[str, Any]] = None):
    """Log agent lifecycle event"""
    agent_logger.log_agent_lifecycle(event, details)
