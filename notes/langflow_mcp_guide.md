# Creating a Simple MCP Server with Langflow

## Overview

As an MCP server, Langflow exposes your flows as tools that MCP clients can use to take actions. This guide will help you create a simple MCP server that can be used by MCP clients like Claude Desktop or Cursor.

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

### 2.1 Access MCP Server Tab

From the Langflow dashboard, select the project that contains the flows you want to serve as tools, and then click the MCP Server tab

Alternative: you can quickly access the MCP Server tab from within any flow by selecting Share > MCP Server

### 2.2 Configure Your Flow as an MCP Tool

1. In the MCP Server tab, click **"Edit Tools"**
2. Select your flow to expose as a tool
3. **Tool Name**: `weather_assistant` (letters, numbers, underscores, dashes only)
4. **Tool Description**: `Get weather information and outdoor activity recommendations`

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

## Step 5: Using Your MCP Server

### 5.1 In Claude Desktop

```
User: "What's the weather like for hiking today?"
Claude: [Uses your weather_assistant tool automatically]
```

### 5.2 In Cursor

1. Install Cursor
2. Configure MCP server in settings
3. Use tools in your code editor context

## Best Practices

### Tool Naming

Tool names must contain only letters, numbers, underscores, and dashes. Tool names cannot contain spaces

### Clear Descriptions

Using the context provided by your tool name and description, the agent can decide to use the document_qa_for_resume MCP tool

### Environment Variables

- Set API keys in Langflow's `.env` file
- Langflow passes environment variables from the .env file to MCP

## Troubleshooting

### Common Issues

1. **Flow not appearing as tool**: Ensure Chat Output component is included
2. **Connection issues**: Verify Langflow is running on correct port (7860)
3. **Tool name errors**: Remove spaces and special characters from tool names

### Debugging

- Use MCP Inspector for detailed debugging
- Check Langflow logs for errors
- Verify MCP client configuration

## Example Use Cases

1. **Document Analysis**: Upload and query PDFs, docs
2. **API Integration**: Connect to external APIs through Langflow
3. **Data Processing**: ETL workflows as MCP tools
4. **Custom Agents**: Multi-agent workflows exposed as tools

## Next Steps

1. Create multiple flows for different tasks
2. Combine flows to create complex workflows
3. Deploy Langflow to cloud for remote MCP access
4. Integrate with your existing development workflow through Cursor

---

**Resources:**

- [Langflow MCP Documentation](https://docs.langflow.org/mcp-server)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Claude Desktop MCP Setup](https://claude.ai/docs)
