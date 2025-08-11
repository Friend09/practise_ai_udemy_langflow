# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI learning project focused on Langflow and Model Context Protocol (MCP) implementations. The project demonstrates agentic workflows where an LLM orchestrates multiple specialized MCP servers to achieve complex tasks, particularly price comparison functionality.

## Development Commands

### Environment Setup
```bash
# Compile requirements from .in file
make compile

# Install dependencies using uv
make install

# Clean cache directories
make clean

# Full setup (clean, compile, install)
make all
```

### Python Environment
The project uses a virtual environment at `.venv/bin/python3`. All MCP servers are configured to use this Python interpreter.

### Running MCP Servers
MCP servers are located in `dev/mcp_servers/` and can be run directly:
```bash
python dev/mcp_servers/price_comparision_mcp_server.py
python dev/mcp_servers/data_processing_mcp_server.py  
python dev/mcp_servers/web_scraping_mcp_server.py
```

## Architecture

### MCP Server Implementation
The project follows a modular MCP architecture with three specialized servers:

1. **Web Scraping MCP Server** (`web_scraping_mcp_server.py`): Handles product data scraping from multiple websites
2. **Data Processing MCP Server** (`data_processing_mcp_server.py`): Processes and standardizes scraped data
3. **Price Comparison MCP Server** (`price_comparision_mcp_server.py`): Analyzes processed data to find lowest prices

Each MCP server:
- Uses `fastmcp` library for implementation
- Follows single responsibility principle
- Includes comprehensive docstrings
- Handles errors gracefully with stderr logging
- Runs via stdio transport protocol

### VS Code Workspace Configuration
MCP servers are pre-configured in the workspace settings (`.code-workspace`) with proper Python paths and arguments for easy testing and development.

### Agentic Workflow Design
The system implements an agentic workflow pattern where:
- **Perception**: LLM receives user queries via Langflow Chat Input
- **Planning**: LLM determines which MCP tools to orchestrate
- **Action Execution**: Sequential tool calls via MCP protocol
- **Response Synthesis**: LLM creates comprehensive responses from tool outputs

## Key Files and Directories

### Core Implementation
- `dev/mcp_servers/` - MCP server implementations
- `requirements.in` - Project dependencies specification
- `requirements.txt` - Compiled dependencies with versions
- `Makefile` - Development automation commands

### Documentation and Examples
- `notes/` - Implementation guides and MCP documentation
- `files/` - Langflow project files and training materials
- `images/` - Architecture diagrams
- `ref_powerpoint_mcp/` - Reference MCP server implementation

### Data and Notebooks  
- `data/` - Project data files
- `notebooks/` - Jupyter notebooks for experimentation

## Code Conventions

### Python Style
- All Python files include comprehensive docstrings
- Class and method documentation follows Google style
- Error handling with proper logging to stderr
- Type hints used for function parameters and returns

### MCP Server Patterns
- Server classes follow `NameAnalyzer` pattern
- Tool registration in `_register_tools()` method
- Async tool functions with descriptive names
- Consistent error response format across servers

### File Naming
- MCP servers use snake_case with descriptive suffixes
- Configuration files follow standard conventions
- Documentation uses descriptive filenames

## Dependencies

The project uses:
- **Langflow**: Main workflow orchestration platform
- **fastmcp**: MCP server implementation framework  
- **Python 3.10+**: Required for MCP and modern Python features
- **uv**: Fast Python package installer and resolver

Key MCP-related dependencies are installed via `fastmcp[cli]` which includes the full MCP toolkit.