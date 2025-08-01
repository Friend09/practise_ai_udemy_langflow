# Creating a Simple Model Context Protocol (MCP) with Langflow

This guide provides step-by-step instructions on how to create and test a basic Model Context Protocol (MCP) using the Langflow tool. Langflow is a visual programming interface for building and deploying AI applications, and it offers robust support for MCP as both a client and a server [1].

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.9+**: Langflow requires a compatible Python version.
- **Docker (Recommended)**: The easiest way to run Langflow is via Docker. If you don't have Docker installed, you can download it from [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Basic understanding of MCP**: Familiarity with MCP concepts (hosts, clients, servers, tools) will be beneficial.

## Step 1: Setting Up Langflow

The quickest way to get Langflow up and running is by using Docker. Open your terminal and execute the following commands:

1.  **Pull the Langflow Docker image:**

    ```bash
    docker pull langflowai/langflow
    ```

2.  **Run the Langflow Docker container:**

    ```bash
    docker run -p 7860:7860 langflowai/langflow
    ```

    This command will start the Langflow server, typically accessible at `http://localhost:7860` in your web browser. Keep this terminal window open as it will display Langflow's logs.

## Step 2: Creating a New Langflow Project

1.  Open your web browser and navigate to `http://localhost:7860`.
2.  You will be greeted by the Langflow interface. Click on the **"New Project"** button or navigate to the project creation section.
3.  Give your project a meaningful name (e.g., "Simple MCP Demo") and click "Create". You will be presented with a blank canvas, which is where you will build your MCP flow.

## Step 3: Adding MCP Components

Langflow provides specific components for working with MCP. We will use the `MCP Tool` component to define our MCP server's capabilities.

1.  On the left-hand sidebar, search for **"MCP Tool"** in the components search bar.
2.  Drag and drop the `MCP Tool` component onto the canvas.
3.  You can rename the component on the canvas for clarity (e.g., "System Info Tool").

## Step 4: Configuring the MCP Tool

Now, let's configure our `MCP Tool` to expose a simple function, similar to the `get_system_info` example from our course.

1.  Double-click on the `MCP Tool` component on the canvas to open its configuration panel.
2.  In the `Code` field, you will define the Python function that your MCP tool will execute. For a simple system information tool, you can use the following Python code:

```python
import platform

def get_system_info() -> dict:
    """Returns basic system information."""
    info = {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }
    return info
```

3.  **Important**: In the `Function Name` field, enter `get_system_info`. This tells Langflow which function within your provided code should be exposed as an MCP tool.
4.  Ensure the `Tool Name` field is set to something descriptive, like `system_info_tool`.
5.  Click **"Save"** to apply the changes to the component.

## Step 5: Exposing the MCP Flow as a Server

To make your Langflow project accessible as an MCP server, you need to configure the project's deployment settings.

1.  In the Langflow interface, locate the **"Deploy"** or **"Export"** option for your project (usually found in the top right corner or a dedicated deployment tab).
2.  Look for options related to **"MCP Server"** or **"Expose as MCP"**. Enable this option.
3.  Langflow will provide you with a command or instructions to run your project as an MCP server. This typically involves a command like `langflow run --as-mcp <project_id>` or similar, which you would execute in a new terminal window.

    **Note**: The exact command might vary slightly depending on your Langflow version and how you installed it. Refer to Langflow's official documentation for the most up-to-date deployment instructions [2].

## Step 6: Testing Your MCP Flow

Once your Langflow project is running as an MCP server, you can test it using an MCP client (like Claude Desktop, Cursor, or a custom Python script).

### Using a Custom Python Client (Conceptual)

Similar to the `mcp_client.py` we developed in the course, you would send a JSON-RPC request to the Langflow-hosted MCP server. The request would look like this:

```json
{
  "jsonrpc": "2.0",
  "method": "system_info_tool_get_system_info",
  "params": [],
  "id": 1
}
```

**Explanation of the `method` name**: Langflow typically prefixes the function name with the tool name (e.g., `system_info_tool_get_system_info`). You might need to inspect the Langflow server logs or documentation to confirm the exact method name exposed.

When you send this request to your running Langflow MCP server, it will execute the `get_system_info` function you defined, and return the system information as a JSON-RPC response.

### Testing within Langflow (if available)

Some versions of Langflow might offer an integrated testing environment for MCP servers. Look for a "Test MCP" or "Client" tab within your deployed project's interface. This would allow you to send test requests directly from the Langflow UI.

## Conclusion

By following these steps, you can successfully create a simple MCP using Langflow, exposing custom tools that can be consumed by any MCP-compatible client. Langflow's visual interface simplifies the process of building and managing complex MCP flows, making it an excellent tool for developing AI agents that interact with external systems.

## References

[1] Langflow Documentation: Use Langflow as an MCP server. Available at: [https://docs.langflow.org/mcp-server](https://docs.langflow.org/mcp-server)

[2] Langflow Documentation: Deploying your flows. Available at: [https://docs.langflow.org/deployment](https://docs.langflow.org/deployment)
