# hello-agent Copilot Instructions

A LLM agent learning repository implementing ReAct pattern with LangChain and LangGraph.

## Python Environment

This project uses **`uv`** for package management (Python 3.12).

**Run Python scripts:**
```bash
uv run <script>.py
uv run demo/base_agent.py
```

**Run tests:**
```bash
uv run pytest                # Run all tests
uv run pytest <test_file>.py # Run specific test
```

## Architecture Overview

### LLM Provider Integration

The project supports multiple LLM providers through LangChain's unified interface:

- **Aliyun Qwen** (Production): Uses `ChatOpenAI` (OpenAI-compatible) + `DashScopeEmbeddings`
  - Config: `DASHSCOPE_API_KEY` environment variable
  - Models: qwen-plus (chat), text-embedding-v4 (embeddings)
  
- **Ollama** (Local/Open-source): Uses `ChatOllama`
  - Config: `OLLAMA_BASE_URL` environment variable (default: `http://host.docker.internal:11434`)
  - Models: Configurable via `model` parameter

**Initialization pattern:**
```python
from llm.ollama_chat import init_ollama_chatmodel
from llm.aliyun import init_qwen_chatmodel, init_qwen_embeddings

chat_model = init_ollama_chatmodel()  # Returns BaseChatModel
chat_model = init_qwen_chatmodel()    # Returns BaseChatModel
embeddings = init_qwen_embeddings()   # Returns Embeddings
```

All providers use LangChain's message types (`SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage`) and methods (`.invoke()`, `.stream()`).

### Agent Architecture (ReAct Pattern)

Agents are created using LangChain's `create_agent()` with tools:

```python
from langchain.agents import create_agent
from tools import weather

tools = [weather.get_weather]
agent = create_agent(chat_model, tools=tools)
```

**Streaming modes:**
- `values`: Full state after each step
- `updates`: Incremental updates per step (recommended for tool calls)
- `messages`: LLM tokens with metadata
- `debug`: Maximum execution information

**Message flow:**
1. User query → `HumanMessage`
2. Agent reasoning → `AIMessage` (may contain `tool_calls`)
3. Tool execution → `ToolMessage`
4. Final response → `AIMessage`

### Tools Structure

Location: `src/tools/`

**Two implementation approaches:**

1. **@tool decorator (recommended):**
   ```python
   from langchain_core.tools import tool

   @tool
   def get_weather(city: str) -> str:
       """Docstring becomes tool description"""
       return weather_data.get(city)
   ```

2. **BaseTool class (for advanced config):**
   ```python
   from langchain_core.tools import BaseTool

   class WeatherTool(BaseTool):
       name: str = "get_weather"
       description: str = "获取指定城市的天气信息"
       weather_url: str = Field(default="...")
       
       def _run(self, city: str) -> str:
           return weather_data.get(city)
   ```

Tools are passed as a list to `create_agent()` and automatically invoked by the LLM when needed.

### Stock Module

Location: `src/stock/`

This module provides stock-related tools and services, organized by functionality. It includes data fetching, news retrieval, search capabilities, and business logic for stock analysis.

Organized into subdirectories:
- `consts/`: Constants
- `data/`: Data fetching (e.g., alltick)
- `news/`: News sources (jin10, wallstreet)
- `search/`: Search functionality (tencent)
- `service/`: Business logic (stock service)
- `types/`: Type definitions (market types)

### Logging

Location: `src/log/`

Uses Protocol-based interface (`Logger`) for type-safe logging with support for debug, info, warning, error levels. Likely backed by `loguru` (project dependency).

## Development Environment

**Docker Compose:**
```bash
docker compose up -d                           # Start container
docker compose up -d --build --force-recreate  # Rebuild and recreate
docker compose exec hello-agent /bin/bash      # Enter container
docker compose down                            # Stop and remove
```

**Environment variables** (set in `.env` or docker-compose.yml):
- `DASHSCOPE_API_KEY`: Aliyun Qwen API key
- `DEEPSEEK_API_KEY`: DeepSeek API key  
- `OLLAMA_BASE_URL`: Ollama server URL
- `QODER_PERSONAL_ACCESS_TOKEN`: Qoder token
- `TAVILY_API_KEY`: Tavily API key

Container uses `host.docker.internal` to access host services like local Ollama.

## Key Conventions

- **Message handling**: Always use LangChain's message types (`HumanMessage`, `AIMessage`, etc.)
- **Tool docstrings**: The function docstring becomes the tool description for the LLM
- **Temperature guidance** (from code comments):
  - 0.0-0.3: Deterministic tasks (extraction, classification)
  - 0.5-0.7: Chat/QA
  - 0.8-2.0: Creative generation
- **Mirror configuration**: Uses Chinese PyPI mirrors (USTC, Tencent Cloud) in `pyproject.toml`
- **Import paths**: Use relative imports from `src/` modules (e.g., `from llm.ollama_chat import ...`)

## Documentation

External documentation: https://henryzhuhr.github.io/toyllm/

## References

- Paper: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Code: [langchain-ai/react-agent](https://github.com/langchain-ai/react-agent)
- Related: [microsoft/TaskWeaver](https://github.com/microsoft/TaskWeaver)
