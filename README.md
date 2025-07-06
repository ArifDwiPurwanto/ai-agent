# AI Personal Assistant Agent

This is a modular AI agent personal assistant built with LangChain, implementing the observe-decide-act loop with comprehensive memory management and tool integration.

## Architecture

The agent follows a modular architecture based on the **Model Context Protocol (MCP)** principles with the following components:

### Core Components

- **🧠 Agent Loop**: Main agent implementation (observe->decide->act pattern)
- **💾 Memory System**: Short-term (STM) and Long-term (LTM) memory management
- **🔧 Tools**: Functional calling capabilities for various tasks
- **🤖 Models**: OpenAI/Gemini integration with LangChain
- **📝 Prompts**: System and user prompt management

### Agent Loop (Observe-Decide-Act)

1. **OBSERVE**: Gather and process input information
   - Parse user input and context
   - Retrieve relevant memories
   - Prepare enhanced context

2. **DECIDE**: Analyze observation and decide on action
   - Use LLM to determine best action type
   - Choose between: respond, use_tool, store_memory, ask_clarification
   - Generate reasoning and confidence scores

3. **ACT**: Execute the decided action
   - Execute tools with parameters
   - Generate responses
   - Store important information
   - Handle errors gracefully

4. **REFLECT**: Learn from the interaction
   - Store important conversations in LTM
   - Update memory systems
   - Consolidate learning

## Project Structure

```
ai-agent/
├── src/                       # Core source code
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core_agent.py      # Main agent implementation
│   │   └── agent_loop.py      # Observe-Decide-Act loop
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── short_term.py      # STM implementation
│   │   ├── long_term.py       # LTM with vector DB
│   │   └── memory_manager.py  # Memory coordination
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base_tool.py       # Base tool class
│   │   ├── web_search.py      # Web searching
│   │   ├── weather.py         # Weather information
│   │   ├── calculator.py      # Math calculations
│   │   └── file_manager.py    # File operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── openai_model.py    # OpenAI integration
│   │   └── gemini_model.py    # Gemini integration
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── system_prompts.py  # System prompts
│   │   └── user_prompts.py    # User prompts
│   └── config/
│       ├── __init__.py
│       └── settings.py        # Configuration
├── apps/                      # Application entry points
│   ├── streamlit_app.py       # Streamlit web UI
│   ├── web_app.py            # Flask web app
│   ├── web_demo.py           # Web demo
│   ├── streamlit_error_test.py # Error testing
│   └── web/                   # Web assets
│       ├── static/
│       │   ├── app.js
│       │   └── style.css
│       └── templates/
│           └── index.html
├── scripts/                   # Utility and test scripts
│   ├── test_api.py           # API key testing
│   ├── test_manual.py        # Manual testing
│   ├── test_comprehensive.py # Comprehensive tests
│   ├── test_action_error.py  # Error testing
│   ├── analyze_logs.py       # Log analysis
│   └── detailed_error_analysis.py # Error analysis
├── config/                    # Configuration files
│   └── .env.example          # Environment template
├── docs/                      # Documentation
│   ├── PROJECT_SUMMARY.md    # Project overview
│   ├── WEB_SETUP.md         # Web setup guide
│   ├── API_KEYS_SETUP.md    # API setup guide
│   ├── EXAMPLE_PROMPTS.md   # Prompt examples
│   ├── DEBUG_GUIDE.md       # Debug guide
│   └── ERROR_ANALYSIS_REPORT.md # Error analysis
├── tests/                     # Unit tests
│   └── test_basic.py         # Basic tests
├── examples/                  # Usage examples
│   ├── basic_usage.py        # Basic examples
│   ├── advanced_usage.py     # Advanced examples
│   └── demo.py              # Demo without API keys
├── logs/                      # Log files
│   ├── errors/               # Error logs
│   ├── debug/               # Debug logs
│   ├── chat/                # Chat logs
│   └── performance/         # Performance logs
├── data/                      # Persistent data
│   ├── agent.db             # SQLite database
│   └── vectordb/            # Vector database
├── main.py                    # Main entry point
├── requirements.txt           # Dependencies
├── README.md                 # This file
└── .env                      # Environment variables
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the configuration template:
```bash
cp config/.env.example .env
```

Edit `.env` with your API keys:

```env
# Required for OpenAI model
OPENAI_API_KEY=your_openai_api_key_here

# Required for Gemini model  
GOOGLE_API_KEY=your_google_api_key_here

# Optional for weather tool
WEATHER_API_KEY=your_weather_api_key_here

# Agent Configuration
AGENT_NAME=PersonalAssistant
DEFAULT_MODEL=openai
MEMORY_PERSIST_PATH=./data/memory
```

### 3. Git Setup (Optional)

This project includes a comprehensive `.gitignore` file that automatically excludes:
- API keys and environment files (`.env`)
- Log files and databases (`logs/`, `data/agent.db`)
- Cache and build files (`__pycache__/`, `*.pyc`)
- IDE configurations (`.vscode/`, `.idea/`)
- Temporary files and OS-specific files

**Important**: Never commit your actual `.env` file with real API keys!

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# The .gitignore will automatically exclude sensitive files
```

For more details, see [docs/GIT_SETUP.md](docs/GIT_SETUP.md)

### 4. Run the Agent

#### Interactive Mode
```bash
python main.py --interactive
```

#### Single Message
```bash
python main.py --message "Hello, what can you help me with?"
```

#### Different Personas
```bash
python main.py --interactive --persona research
python main.py --interactive --persona technical
```

#### Different Models
```bash
python main.py --interactive --model gemini
```

### 5. Web Applications

#### Streamlit Web UI
```bash
streamlit run apps/streamlit_app.py
```

#### Flask Web App
```bash
python apps/web_app.py
```

#### Web Demo
```bash
python apps/web_demo.py
```

### 6. Examples and Testing

#### Run Demo (No API Keys Required)
```bash
python examples/demo.py
```

#### Basic Usage Example
```bash
python examples/basic_usage.py
```

#### Advanced Usage Example
```bash
python examples/advanced_usage.py
```

### 7. Utility Scripts

#### Test API Keys
```bash
python scripts/test_api.py
```

#### Comprehensive Testing
```bash
python scripts/test_comprehensive.py
```

#### Analyze Logs
```bash
python scripts/analyze_logs.py
```

#### Manual Testing
```bash
python scripts/test_manual.py
```

## Features

### 🧠 Advanced Memory System
- **Short-term Memory (STM)**: Maintains conversation context
- **Long-term Memory (LTM)**: Persistent storage with vector search
- **Memory Consolidation**: Automatic transfer of important information
- **User Preferences**: Persistent user settings and preferences

### 🔧 Comprehensive Tool Integration
- **Web Search**: Real-time information retrieval
- **Calculator**: Mathematical computations and functions
- **Weather**: Current weather information
- **File Manager**: File and directory operations
- **Extensible**: Easy to add new tools

### 🤖 Multi-Model Support
- **OpenAI GPT**: State-of-the-art language understanding
- **Google Gemini**: Advanced reasoning capabilities
- **Seamless Switching**: Change models without losing context

### 🎭 Multiple Personas
- **Personal Assistant**: Daily tasks and productivity
- **Research Assistant**: Information gathering and analysis
- **Technical Assistant**: Programming and technical support

### 🛡️ Security & Safety
- **Path Restrictions**: File operations limited to safe directories
- **Input Validation**: Secure handling of user inputs
- **Error Handling**: Graceful failure management
- **Privacy Protection**: Secure memory management

## Usage Examples

### Basic Conversation
```python
from src.agent import create_agent

# Create agent
agent = create_agent(model_type="openai", persona="personal")

# Chat
response = await agent.chat("What's the weather like in Jakarta?")
print(response)
```

### Memory Management
```python
# Store user preference
agent.store_user_preference("language", "English")

# Search memories
memories = agent.search_memories("weather Jakarta")

# Get memory summary
summary = agent.get_memory_summary()
```

### Tool Usage
```python
# The agent automatically selects and uses appropriate tools
response = await agent.chat("Calculate 15 * 23 + 87")
response = await agent.chat("Search for AI news")
response = await agent.chat("What's the weather in New York?")
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Or run basic tests:

```bash
python tests/test_basic.py
```

## Examples

### Basic Usage
```bash
python examples/basic_usage.py
```

### Advanced Features
```bash
python examples/advanced_usage.py
```

## Architecture Deep Dive

### Agent Loop Implementation

The core agent follows the **Observe-Decide-Act** pattern:

1. **Observation Phase**:
   - Processes user input and context
   - Retrieves relevant memories
   - Prepares enhanced context for decision making

2. **Decision Phase**:
   - Uses LLM to analyze the situation
   - Determines the best action type
   - Generates reasoning and confidence scores

3. **Action Phase**:
   - Executes the chosen action
   - Handles tool execution
   - Manages error cases

4. **Reflection Phase**:
   - Analyzes the interaction
   - Stores important information
   - Updates memory systems

### Memory Architecture

- **STM**: In-memory deque with configurable size
- **LTM**: SQLite + ChromaDB for structured and semantic storage
- **Memory Manager**: Coordinates STM/LTM operations and consolidation

### Tool System

- **Base Tool Class**: Standardized interface for all tools
- **Async Execution**: Non-blocking tool operations
- **Error Handling**: Graceful failure management
- **Parameter Validation**: JSON schema-based validation

## Configuration

The agent can be configured through environment variables or the settings module:

```python
from src.config import settings

# Modify settings
settings.MAX_TOKENS = 3000
settings.TEMPERATURE = 0.5
settings.STM_MAX_MESSAGES = 30
```

## Extending the Agent

### Adding New Tools

1. Create a new tool class inheriting from `BaseTool`
2. Implement the required methods
3. Register in `tools/__init__.py`

```python
from src.tools import BaseTool, ToolResult

class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("my_tool", "Description of my tool")
    
    async def execute(self, **kwargs) -> ToolResult:
        # Tool implementation
        pass
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        # Return JSON schema
        pass
```

### Adding New Personas

Extend the system prompts with new persona types:

```python
from src.prompts import SystemPrompts

# Add new persona prompt
SystemPrompts.CUSTOM_PERSONA_PROMPT = "Your custom persona prompt..."
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your API keys are set correctly in `.env`
2. **Memory Issues**: Check that the `data/` directory is writable
3. **Tool Failures**: Verify network connectivity for web-based tools
4. **Model Errors**: Ensure you have sufficient API credits

### Logging

The agent logs activities to both console and `agent.log`. Adjust log level:

```bash
python main.py --log-level DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [LangChain](https://langchain.readthedocs.io/)
- Inspired by [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses OpenAI and Google AI APIs
