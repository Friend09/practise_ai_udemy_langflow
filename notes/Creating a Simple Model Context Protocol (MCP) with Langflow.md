# Integrating External Model Context Protocol (MCP) Servers with Langflow

This guide provides step-by-step instructions on how to integrate external Model Context Protocol (MCP) servers with Langflow, enabling agentic workflows where the LLM orchestrates specialized tools through standardized communications. Langflow acts as an MCP client, connecting to external MCP servers to access their exposed tools within your agentic workflows [1].

## Prerequisites

Before you begin, ensure you have the following:

*   **Python 3.9+**: Langflow requires a compatible Python version.
*   **Docker (Recommended)**: The easiest way to run Langflow is via Docker. If you don't have Docker installed, you can download it from [Docker Desktop](https://www.docker.com/products/docker-desktop/).
*   **A running external MCP Server**: You will need an MCP server that exposes tools. For example, the `system_info_server.py`, `pg_mcp_server.py`, or `productivity_mcp_server.py` from our MCP course can serve this purpose.
*   **Understanding of MCP and agentic workflows**: Familiarity with how MCP serves as a communication protocol between LLMs and specialized tools within agentic workflows will be beneficial.

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
3.  Give your project a meaningful name (e.g., "External MCP Integration") and click "Create". You will be presented with a blank canvas.

## Step 3: Adding the `MCP Tools` Component (Communication Layer)

Langflow uses the `MCP Tools` component to create the communication infrastructure between your LLM and external MCP servers. This component enables the standardized MCP protocol that allows your agentic workflows to discover and interact with specialized external tools.

1.  On the left-hand sidebar, search for **"MCP Tools"** in the components search bar.
2.  Drag and drop the `MCP Tools` component onto the canvas.

## Step 4: Configuring the `MCP Tools` Component to Connect to an External Server

This is the crucial step where you tell Langflow how to connect to your external MCP server. The `MCP Tools` component offers different modes for connection:

1.  **Double-click** on the `MCP Tools` component on the canvas to open its configuration panel.
2.  In the `MCP Server` field, click **"Add MCP Server"**.
3.  You will see options to add a server via **JSON**, **STDIO**, or **SSE**. For the MCP servers we built in the course (which communicate over standard input/output), the **STDIO** mode is most appropriate.

    *   **STDIO Mode Configuration (for our course MCP servers)**:
        *   **Name**: Provide a descriptive name for your MCP server (e.g., `SystemInfoServer`, `PostgreSQLServer`, `ProductivityAppServer`).
        *   **Command**: This is the command that Langflow will execute to start your MCP server. It should be the Python command to run your server script. For example:
            ```
            python /path/to/your/mcp_course/system_info_server.py
            ```
            (Replace `/path/to/your/mcp_course/` with the actual absolute path to your `mcp_course` directory on your system).
        *   **Arguments**: Any command-line arguments your server script might need (leave blank for our course examples).
        *   **Environment Variables**: If your MCP server relies on environment variables (like `PG_HOST`, `PG_DATABASE`, etc., for the PostgreSQL MCP server), you can define them here. Enter each variable as `VARIABLE=value`.

4.  Click **"Add Server"** after configuring the details.
5.  Back in the `MCP Tools` component configuration, in the **"Tool"** field, you can select a specific tool exposed by your connected MCP server, or leave it blank to allow access to all tools. For example, for `system_info_server.py`, you might select `get_system_info`.
6.  **Enable Tool Mode**: In the component's header menu (usually a small gear icon or context menu), ensure **"Tool mode"** is enabled. This makes the tools from this MCP server available to an `Agent` component.

## Step 5: Connecting to an Agent (The Orchestrator of Your Agentic Workflow)

To create a complete agentic workflow, you need to connect your MCP tools to an `Agent` component. The Agent component contains the LLM that will serve as the "brain" of your workflow - planning actions, orchestrating tools, and synthesizing responses.

1.  Drag and drop an `Agent` component onto your canvas (if you don't have one already).
2.  Connect the **`Toolset`** port of your `MCP Tools` component to the **`Tools`** port of your `Agent` component. This makes the MCP tools accessible to the Agent's LLM through the MCP protocol.
3.  Configure your `Agent` component with:
    * An appropriate LLM (e.g., OpenAI, Anthropic)
    * Clear instructions that guide the Agent on when and how to use each MCP tool
    * Specifications for the planning, action, and synthesis phases of your workflow

## Step 6: Testing Your Agentic Workflow

1.  Connect a `Chat Input` component to the `Input` of your `Agent` component (perception phase).
2.  Connect the `Response` output of your `Agent` component to a `Chat Output` component (response phase).
3.  Open the Langflow **Playground** (usually a chat interface on the right side).
4.  Enter a prompt that would trigger your agentic workflow. For example, if you connected the `system_info_server.py`, you could ask: "What is the system information?" or "Tell me about the operating system."
5.  Observe how your agentic workflow executes:
   * **Perception**: The system receives your query
   * **Planning**: The Agent (LLM) determines it needs to use an MCP tool
   * **Action Execution**: The Agent calls the appropriate MCP tool through the MCP protocol
   * **Response Synthesis**: The Agent creates a comprehensive answer based on the tool's output
   * **Output**: The system presents the final response
6.  You can also monitor the logs in the terminal where Langflow is running to see the MCP protocol communication in action.

## Conclusion

By following these steps, you've created a complete agentic workflow in Langflow where the LLM orchestrates specialized tools through the standardized MCP protocol. Understanding the distinction is important:

- **The overall system is an agentic workflow** where the Agent (LLM) perceives, plans, executes actions, and responds
- **MCP is the communication protocol** that enables standardized interaction between the LLM and external tools
- **Each specialized capability is provided by an MCP server** that exposes specific functions

This architecture allows you to build sophisticated AI applications where the LLM serves as the orchestrator of specialized tools, each handling specific tasks within your workflow. The MCP protocol ensures clean separation of concerns and standardized interfaces between components.

## References

[1] Langflow Documentation: Use Langflow as an MCP client. Available at: [https://docs.langflow.org/mcp-client](https://docs.langflow.org/mcp-client)
[2] Model Context Protocol Specification: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
[3] MCP Server Examples: [https://github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)
