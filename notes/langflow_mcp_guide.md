# Creating a Simple MCP Server with Langflow

## Overview

While our previous guide covered using Langflow as an MCP client within agentic workflows, Langflow can also act as an MCP server - exposing your complete flows as tools that other MCP clients can use. In this dual role, Langflow demonstrates the bi-directional capabilities of the MCP protocol. This guide will help you create a simple MCP server that can be used by MCP clients like Claude Desktop or Cursor.

## Prerequisites

- Langflow installed and running (`pip install langflow`)
- Python 3.10+
- Node.js LTS (for MCP Inspector testing)
- An MCP client like Claude Desktop or Cursor (optional for testing)

## Step 1: Create a Simple Flow in Langflow

### 1.1 Start Langflow

```bash
langflow run
# Langflow will start at http://127.0.0.1:7860
```

### 1.2 Create a New Flow

1. Open Langflow in your browser
2. Click **"New Flow"**
3. Select **"Simple Agent"** template or start from scratch

### 1.3 Build Your Flow

**Important**: A flow must contain a Chat Output component to be used as a tool by MCP clients

**Example Simple Weather Helper Flow:**

1. **Chat Input** component (for user questions)
2. **OpenAI** component (or your preferred LLM)
3. **Prompt** component with template:

   ```
   You are a helpful weather assistant. Answer questions about weather and provide helpful outdoor activity suggestions.

   User question: {input}
   ```

4. **Chat Output** component (required for MCP)

Connect: Chat Input → Prompt → OpenAI → Chat Output

### 1.4 Name and Describe Your Flow

It's helpful to think of the names and descriptions as function names and code comments, using clear statements describing the problems your flows solve

1. Click **Flow Name > Edit Details**
2. **Name**: `weather_assistant` (no spaces, use underscores)
3. **Description**: `A helpful assistant that provides weather information and outdoor activity recommendations`

## Step 2: Configure MCP Server Settings

### 2.1 Understanding the MCP Protocol Architecture

Before configuring, it's important to understand that:
- **MCP is a communication protocol** between LLMs and specialized tools
- When Langflow acts as an MCP server, your entire flow becomes a tool that other LLMs can use
- The LLM (in Claude Desktop or Cursor) becomes the orchestrator of an agentic workflow
- Your Langflow flow acts as one specialized component in that larger workflow

### 2.2 Access MCP Server Tab

From the Langflow dashboard, select the project that contains the flows you want to expose as MCP tools, and then click the MCP Server tab

Alternative: you can quickly access the MCP Server tab from within any flow by selecting Share > MCP Server

### 2.3 Configure Your Flow as an MCP Tool

1. In the MCP Server tab, click **"Edit Tools"**
2. Select your flow to expose as a tool
3. **Tool Name**: `weather_assistant` (letters, numbers, underscores, dashes only)
4. **Tool Description**: `Get weather information and outdoor activity recommendations`
5. Ensure your tool description clearly explains what problem this tool solves within a larger agentic workflow

## Step 3: Test Your MCP Server

### 3.1 Using MCP Inspector (Recommended)

MCP inspector is the standard tool for testing and debugging MCP servers

```bash
# Install and run MCP Inspector
npx @modelcontextprotocol/inspector

# Opens at http://localhost:5173
```

**In MCP Inspector:**

1. **Transport Type**: Select `SSE`
2. **URL**: `http://127.0.0.1:7860/api/v1/mcp/sse`
3. Click **Connect**
4. Go to **Tools** tab to see your flow listed as a tool

### 3.2 Test with Claude Desktop (macOS/Windows)

**Configure Claude Desktop:**

1. Open Claude Desktop settings
2. Click **Developer > Edit Config**
3. Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "langflow": {
      "command": "uvx",
      "args": [
        "--python",
        "/path/to/your/python",
        "mcp-sse-shim",
        "http://127.0.0.1:7860/api/v1/mcp/sse"
      ]
    }
  }
}
```

4. Restart Claude Desktop
5. Your Langflow tools will appear in Claude

**Understanding the Agentic Architecture:**
- Claude's LLM acts as the orchestrator of the agentic workflow
- Your Langflow flow becomes a specialized tool within Claude's larger workflow
- Claude communicates with your tool using the standardized MCP protocol
- The MCP protocol handles tool discovery, parameter passing, and result processing

## Step 4: Advanced Example - Document Q&A MCP

### 4.1 Create Document Q&A Flow

1. Use **"Document Q&A"** template in Langflow
2. Components needed:
   - **Chat Input**
   - **File Upload**
   - **Text Splitter**
   - **Embeddings** (OpenAI/Cohere)
   - **Vector Store** (Chroma/Pinecone)
   - **LLM** (OpenAI/Anthropic)
   - **Chat Output** (required)

### 4.2 Configure for MCP

- **Flow Name**: `document_qa_system`
- **Tool Description**: `Upload and query documents using RAG (Retrieval-Augmented Generation)`

## Step 5: Using Your MCP Server in an Agentic Workflow

### 5.1 In Claude Desktop's Agentic Workflow

```
User: "What's the weather like for hiking today?"
Claude: [Planning phase: determines weather information is needed]
Claude: [Action execution phase: calls your weather_assistant tool via MCP]
Claude: [Response synthesis: creates answer based on tool response]
Claude: "Based on the current weather data, it's perfect hiking weather today with sunny skies and temperatures around 75°F. Consider bringing sunscreen and water as UV index is high."
```

### 5.2 In Cursor's Development Workflow

1. Install Cursor
2. Configure MCP server in settings
3. As you code, Cursor's LLM can:
   - Plan which tools might help with your current task
   - Call your Langflow tools through MCP when needed
   - Integrate the results into its assistance

## Best Practices for MCP Tool Design

### Tool Design Principles

- **Single Responsibility**: Each MCP tool should have a clear, focused purpose
- **Composability**: Tools should work well with other tools in larger workflows
- **Idempotent Operations**: Same input should produce same output for reliability
- **Error Tolerance**: Include proper error handling for graceful failures

### Tool Naming and Description

- Tool names must contain only letters, numbers, underscores, and dashes (no spaces)
- Descriptions should clearly explain the tool's purpose within an agentic workflow
- Be explicit about inputs required and outputs provided
- Using clear descriptions helps the orchestrating LLM decide when to use your tool

### Environment Variables

- Set API keys in Langflow's `.env` file
- Langflow passes environment variables from the .env file to MCP
- Secure sensitive credentials properly

## Troubleshooting

### Common Issues

1. **Flow not appearing as tool**: Ensure Chat Output component is included
2. **Connection issues**: Verify Langflow is running on correct port (7860)
3. **Tool name errors**: Remove spaces and special characters from tool names

### Debugging

- Use MCP Inspector for detailed debugging
- Check Langflow logs for errors
- Verify MCP client configuration

## Advanced MCP Patterns

### Bidirectional MCP Usage

Langflow can participate in MCP-based agentic workflows in two ways:
1. **As an MCP Client**: Your Langflow flow uses external MCP tools
2. **As an MCP Server**: Your Langflow flow becomes a tool for external agents

You can even create complex configurations where:
- Langflow Instance A exposes flows as MCP tools
- Langflow Instance B uses those tools within its own workflows
- External agents like Claude Desktop or Cursor orchestrate both

### Example Use Cases

1. **Document Analysis**: Upload and query PDFs, docs
2. **API Integration**: Connect to external APIs through Langflow
3. **Data Processing**: ETL workflows as MCP tools
4. **Multi-Agent Collaboration**: Specialized Langflow agents working together

### Next Steps

1. Create multiple specialized tools for different tasks
2. Combine tools in hierarchical agentic workflows
3. Deploy Langflow to cloud for remote MCP access
4. Integrate with your existing development workflow through Cursor
5. Experiment with adaptive tool selection based on query complexity

---

**Resources:**

- [Langflow MCP Documentation](https://docs.langflow.org/mcp-server)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Claude Desktop MCP Setup](https://claude.ai/docs)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Server Examples](https://github.com/modelcontextprotocol)
