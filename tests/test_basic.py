"""
Basic tests for AI Agent components
"""
import unittest
import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.memory import ShortTermMemory, MemoryManager
from src.tools import CalculatorTool, get_all_tools
from src.config import settings

class TestShortTermMemory(unittest.TestCase):
    """Test short-term memory functionality"""
    
    def setUp(self):
        self.stm = ShortTermMemory(max_messages=5)
    
    def test_add_message(self):
        """Test adding messages to STM"""
        self.stm.add_message("user", "Hello")
        self.stm.add_message("assistant", "Hi there!")
        
        messages = self.stm.get_messages()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "Hello")
    
    def test_max_messages_limit(self):
        """Test STM respects max messages limit"""
        for i in range(10):
            self.stm.add_message("user", f"Message {i}")
        
        messages = self.stm.get_messages()
        self.assertEqual(len(messages), 5)  # Max limit
        self.assertEqual(messages[-1]["content"], "Message 9")
    
    def test_context_management(self):
        """Test context storage and retrieval"""
        self.stm.update_context("user_name", "Alice")
        self.stm.update_context("user_location", "Seattle")
        
        self.assertEqual(self.stm.get_context("user_name"), "Alice")
        self.assertEqual(self.stm.get_context("user_location"), "Seattle")
        
        all_context = self.stm.get_context()
        self.assertIn("user_name", all_context)
        self.assertIn("user_location", all_context)

class TestCalculatorTool(unittest.TestCase):
    """Test calculator tool functionality"""
    
    def setUp(self):
        self.calc = CalculatorTool()
    
    def test_basic_arithmetic(self):
        """Test basic arithmetic operations"""
        async def run_test():
            result = await self.calc.execute("2 + 3")
            self.assertTrue(result.success)
            self.assertEqual(result.result["result"], 5)
            
            result = await self.calc.execute("10 * 5")
            self.assertTrue(result.success)
            self.assertEqual(result.result["result"], 50)
        
        asyncio.run(run_test())
    
    def test_advanced_functions(self):
        """Test advanced mathematical functions"""
        async def run_test():
            result = await self.calc.execute("sqrt(16)")
            self.assertTrue(result.success)
            self.assertEqual(result.result["result"], 4.0)
            
            result = await self.calc.execute("sin(0)")
            self.assertTrue(result.success)
            self.assertEqual(result.result["result"], 0.0)
        
        asyncio.run(run_test())
    
    def test_invalid_expression(self):
        """Test handling of invalid expressions"""
        async def run_test():
            result = await self.calc.execute("invalid_expression")
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)
        
        asyncio.run(run_test())

class TestMemoryManager(unittest.TestCase):
    """Test memory manager functionality"""
    
    def setUp(self):
        self.memory_manager = MemoryManager()
    
    def test_message_management(self):
        """Test message addition and retrieval"""
        self.memory_manager.add_user_message("Hello")
        self.memory_manager.add_assistant_message("Hi there!")
        
        context = self.memory_manager.get_conversation_context(include_ltm=False)
        self.assertEqual(len(context), 2)
        self.assertEqual(context[0]["role"], "user")
        self.assertEqual(context[1]["role"], "assistant")
    
    def test_preference_storage(self):
        """Test user preference storage and retrieval"""
        self.memory_manager.store_user_preference("language", "English")
        self.memory_manager.store_user_preference("timezone", "UTC")
        
        self.assertEqual(self.memory_manager.get_user_preference("language"), "English")
        self.assertEqual(self.memory_manager.get_user_preference("timezone"), "UTC")

class TestToolRegistry(unittest.TestCase):
    """Test tool registry and loading"""
    
    def test_tool_loading(self):
        """Test that all tools can be loaded"""
        tools = get_all_tools()
        self.assertGreater(len(tools), 0)
        
        # Check that each tool has required attributes
        for tool in tools:
            self.assertTrue(hasattr(tool, 'name'))
            self.assertTrue(hasattr(tool, 'description'))
            self.assertTrue(hasattr(tool, 'execute'))
            self.assertTrue(hasattr(tool, 'get_parameters_schema'))

class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def test_settings_attributes(self):
        """Test that settings has required attributes"""
        required_attrs = [
            'AGENT_NAME', 'DEFAULT_MODEL', 'MAX_TOKENS', 
            'TEMPERATURE', 'STM_MAX_MESSAGES'
        ]
        
        for attr in required_attrs:
            self.assertTrue(hasattr(settings, attr))
    
    def test_default_values(self):
        """Test default configuration values"""
        self.assertIsInstance(settings.MAX_TOKENS, int)
        self.assertIsInstance(settings.TEMPERATURE, float)
        self.assertGreater(settings.STM_MAX_MESSAGES, 0)

if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
