# Implementing the Price Comparison Agent in Langflow

This document provides corrected guidance on how to implement the Price Comparison Agent, as depicted in the architecture diagram, within Langflow. This implementation demonstrates an **agentic workflow** where the LLM orchestrates multiple external Model Context Protocol (MCP) servers through standardized communications to achieve a complex goal.

## Understanding the Agentic Workflow and MCP

Before implementing, it's important to understand that:

1. **The entire system is an agentic workflow** where the Agent (LLM) perceives user input, plans actions, executes tools, and produces responses
2. **MCP is the communication protocol** that enables standardized interaction between the LLM and external tools
3. **Each specialized capability is provided by an MCP server** that exposes specific functions

As clarified in the MCP documentation, Langflow acts as an MCP client and connects to external MCP servers using the `MCP Tools` component. This means:

1. **Create separate MCP servers** (as Python scripts) that expose the required tools
2. **Use the `MCP Tools` component** in Langflow to connect to these external servers
3. **Connect the `MCP Tools` components** to an `Agent` component that orchestrates their use through the MCP protocol

## Step 1: Create External MCP Servers (The Communication Infrastructure)

Before building your Langflow flow, you need to create the external MCP servers that will provide the specialized capabilities for your price comparison agent. Remember that MCP is the **communication infrastructure** that enables the LLM to interact with external tools. Based on our architecture, you need three separate MCP servers:

### 1.1 Web Scraping MCP Server

Create a file named `web_scraping_mcp_server.py`:

```python
import sys
import json
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

class WebScrapingAnalyzer:
    def __init__(self):
        self.mcp = FastMCP("web_scraping_analyzer")
        print("Web Scraping MCP Server initialized", file=sys.stderr)
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool()
        async def scrape_product_price(product_name: str, website_urls: list) -> dict:
            """Scrapes the price of a product from multiple websites."""
            print(f"Scraping {product_name} from {len(website_urls)} websites", file=sys.stderr)
            results = []

            for url in website_urls:
                try:
                    # This is a simplified example. Real web scraping would be more complex.
                    print(f"Attempting to scrape {url}", file=sys.stderr)

                    # For demonstration, return mock data
                    # In a real implementation, you would use requests and BeautifulSoup
                    mock_price = f"${(hash(url) % 500 + 100):.2f}"  # Generate a mock price

                    results.append({
                        "product": product_name,
                        "website": url,
                        "price": mock_price,
                        "success": True
                    })
                except Exception as e:
                    results.append({
                        "product": product_name,
                        "website": url,
                        "error": str(e),
                        "success": False
                    })

            print(f"Scraped {len(results)} results", file=sys.stderr)
            return {"results": results}

    def run(self):
        try:
            print("Running Web Scraping MCP Server...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    analyzer = WebScrapingAnalyzer()
    analyzer.run()
```

### 1.2 Data Processing MCP Server

Create a file named `data_processing_mcp_server.py`:

```python
import sys
import json
import re
from mcp.server.fastmcp import FastMCP

class DataProcessingAnalyzer:
    def __init__(self):
        self.mcp = FastMCP("data_processing_analyzer")
        print("Data Processing MCP Server initialized", file=sys.stderr)
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool()
        async def process_scraped_data(raw_data: dict) -> dict:
            """Processes raw scraped product data into a standardized format."""
            print("Processing scraped data", file=sys.stderr)
            processed_results = []

            for item in raw_data.get("results", []):
                if item.get("success"):
                    try:
                        # Extract numeric price from string
                        price_str = item.get("price", "0")
                        price_match = re.search(r'[\d,]+\.?\d*', price_str.replace("$", "").replace(",", ""))
                        price = float(price_match.group()) if price_match else 0.0

                        processed_results.append({
                            "product": item.get("product"),
                            "website": item.get("website"),
                            "price": price,
                            "original_price_string": price_str
                        })
                    except (ValueError, AttributeError) as e:
                        print(f"Could not process price: {item.get('price')} - {e}", file=sys.stderr)
                        continue

            print(f"Processed {len(processed_results)} valid results", file=sys.stderr)
            return {"processed_data": processed_results}

    def run(self):
        try:
            print("Running Data Processing MCP Server...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    analyzer = DataProcessingAnalyzer()
    analyzer.run()
```

### 1.3 Price Comparison MCP Server

Create a file named `price_comparison_mcp_server.py`:

```python
import sys
import json
from mcp.server.fastmcp import FastMCP

class PriceComparisonAnalyzer:
    def __init__(self):
        self.mcp = FastMCP("price_comparison_analyzer")
        print("Price Comparison MCP Server initialized", file=sys.stderr)
        self._register_tools()

    def _register_tools(self):
        @self.mcp.tool()
        async def find_lowest_price(processed_data: dict) -> dict:
            """Finds the lowest price from processed product data."""
            print("Finding lowest price", file=sys.stderr)

            data_list = processed_data.get("processed_data", [])
            if not data_list:
                return {
                    "lowest_price": "N/A",
                    "source": "N/A",
                    "message": "No valid data to compare.",
                    "all_prices": []
                }

            lowest_item = None
            all_prices = []

            for item in data_list:
                price = item.get("price", 0)
                all_prices.append({
                    "website": item.get("website"),
                    "price": price,
                    "original_price_string": item.get("original_price_string")
                })

                if lowest_item is None or price < lowest_item["price"]:
                    lowest_item = item

            if lowest_item:
                result = {
                    "lowest_price": lowest_item["price"],
                    "source": lowest_item["website"],
                    "product": lowest_item["product"],
                    "message": "Lowest price found successfully.",
                    "all_prices": all_prices
                }
                print(f"Lowest price: ${lowest_item['price']:.2f} from {lowest_item['website']}", file=sys.stderr)
                return result
            else:
                return {
                    "lowest_price": "N/A",
                    "source": "N/A",
                    "message": "Could not determine lowest price.",
                    "all_prices": all_prices
                }

    def run(self):
        try:
            print("Running Price Comparison MCP Server...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    analyzer = PriceComparisonAnalyzer()
    analyzer.run()
```

## Step 2: Building the Agentic Workflow in Langflow

Now that you have your external MCP servers (the specialized tools), you can build the agentic workflow in Langflow that will orchestrate these tools:

### 2.1 Add Core Agentic Workflow Components

1.  **Start a New Project**: Create a new project in Langflow (e.g., "Price Comparison Agentic Workflow").
2.  **Add `Chat Input` and `Chat Output`**: Place these on the canvas for perception (input) and response (output).
3.  **Add `Agent` Component**: This will be the "brain" of the agentic workflow, responsible for planning, reasoning, and orchestrating the tools.

### 2.2 Add and Configure `MCP Tools` Components (The Tool Communication Layer)

You need to add three separate `MCP Tools` components, one for each external MCP server. These components form the communication infrastructure of your agentic workflow, enabling the LLM to discover and interact with external tools through the standardized MCP protocol:

#### 2.2.1 Web Scraping MCP Tools Component

1.  Drag and drop an `MCP Tools` component onto the canvas.
2.  Rename it to "Web Scraping Tools" for clarity.
3.  Double-click to configure:
    *   Click **"Add MCP Server"**.
    *   Select **STDIO** mode.
    *   **Name**: `WebScrapingServer`
    *   **Command**: `python /absolute/path/to/your/web_scraping_mcp_server.py`
    *   Click **"Add Server"**.
4.  In the **Tool** field, select `scrape_product_price` (or leave blank for all tools).
5.  Enable **Tool Mode** in the component's header menu.

#### 2.2.2 Data Processing MCP Tools Component

1.  Add another `MCP Tools` component.
2.  Rename it to "Data Processing Tools".
3.  Configure:
    *   **Name**: `DataProcessingServer`
    *   **Command**: `python /absolute/path/to/your/data_processing_mcp_server.py`
    *   **Tool**: `process_scraped_data`
4.  Enable **Tool Mode**.

#### 2.2.3 Price Comparison MCP Tools Component

1.  Add a third `MCP Tools` component.
2.  Rename it to "Price Comparison Tools".
3.  Configure:
    *   **Name**: `PriceComparisonServer`
    *   **Command**: `python /absolute/path/to/your/price_comparison_mcp_server.py`
    *   **Tool**: `find_lowest_price`
4.  Enable **Tool Mode**.

### 2.3 Configure the Agent (The "Brain" of Your Agentic Workflow)

1.  Configure the `Agent` component, which acts as the central orchestrator of your agentic workflow:
    *   **Model Provider**: Select your LLM provider (e.g., `OpenAI`).
    *   **Model Name**: Choose a suitable model (e.g., `gpt-4-turbo`).
    *   **API Key**: Provide your API key.
    *   **Agent Instructions**: Provide clear instructions for orchestrating the workflow:
        ```
        You are a price comparison assistant coordinating an agentic workflow. When a user asks for product price comparisons:

        1. PLANNING: Analyze the user's request to understand the product they want to compare
        2. TOOL SELECTION: Use these MCP tools in sequence:
           a. First, use scrape_product_price to gather raw data from multiple websites
           b. Next, use process_scraped_data to clean and standardize the results
           c. Finally, use find_lowest_price to identify the best deal
        3. SYNTHESIS: Present a comprehensive answer including:
           - The lowest price and where to find it
           - Price comparison across all sources
           - Any relevant shipping or availability details
           - Savings compared to the highest price

        Remember that you are orchestrating these specialized tools via the MCP protocol, and each tool handles a specific part of the workflow.
        ```

### 2.4 Connect the Agentic Workflow Components

1.  Connect the **Toolset** outputs of all three `MCP Tools` components to the **Tools** input of the `Agent` component. This makes the MCP tools accessible to the Agent.
2.  Connect `Chat Input` to the `Input` of the `Agent` component (perception phase of the workflow).
3.  Connect the `Response` output of the `Agent` component to the `Chat Output` (action/response phase).

This connectivity represents the complete agentic workflow, where:
- The user input enters the system via Chat Input (perception)
- The Agent processes the input and plans necessary actions (reasoning/planning)
- The Agent orchestrates the MCP tools in sequence (action execution via MCP)
- The Agent synthesizes a response based on tool outputs (synthesis)
- The result is delivered to the user via Chat Output (response)

## Step 3: Testing Your Agentic Price Comparison Workflow

1.  Open the Langflow **Playground**.
2.  Enter a query like: "Find the lowest price for a DJI Mavic Pro 4 across different websites."
3.  Watch as the agentic workflow executes:
    * **Perception**: The system receives your query about the DJI Mavic Pro 4
    * **Planning**: The Agent (LLM) determines it needs to follow the defined workflow
    * **Action Execution** (via MCP protocol):
        * The Agent calls the web scraping MCP tool to gather raw price data
        * The Agent then calls the data processing MCP tool to standardize the results
        * Finally, the Agent calls the price comparison MCP tool to analyze and find the best deal
    * **Response Synthesis**: The Agent creates a comprehensive answer based on all tool results
    * **Output**: The system presents a clear comparison showing the lowest price, where to find it, and how much you'll save

## Implementation Best Practices

Based on MCP agent best practices:

### Technical Implementation Notes

*   **Absolute Paths**: Use absolute paths to your MCP server Python files in the **Command** fields.
*   **Dependencies**: Ensure that `fastmcp` and any other required libraries are installed in the Python environment where Langflow is running.
*   **Error Handling**: Monitor the Langflow logs and the stderr output from your MCP servers for debugging.
*   **Mock Data**: The web scraping server provided uses mock data for demonstration. In a real implementation, you would need to implement actual web scraping logic with proper error handling and respect for robots.txt files.

### MCP Tool Design Principles

*   **Single Responsibility**: Each MCP server focuses on one specific task (scraping, processing, or comparison)
*   **Composability**: Tools are designed to work together in sequence
*   **Idempotent Operations**: Same input produces the same output for reliability
*   **Error Tolerance**: Each server includes error handling for graceful failure recovery

### Agent Orchestration Guidelines

*   **Clear Instructions**: The agent has explicit guidance on when to use each tool
*   **Context Management**: Ensure the agent maintains context across tool calls
*   **Performance Considerations**: Be mindful of tool execution times for better user experience
*   **Fallback Strategies**: Define what the agent should do if a tool fails

### Advanced Extensions (Optional)

*   **Hierarchical Tool Structure**: Add sub-tools within each MCP server for more granular capabilities
*   **Adaptive Tool Selection**: Allow the agent to conditionally skip tools based on query complexity
*   **Multi-Agent Collaboration**: Consider specialized agents for different aspects of price comparison

This implementation leverages Langflow's MCP integration capabilities to create a sophisticated agentic workflow where the LLM serves as the orchestrator of specialized external tools, all communicating through the standardized MCP protocol.

## References

[1] Langflow Documentation: Use Langflow as an MCP client. Available at: [https://docs.langflow.org/mcp-client](https://docs.langflow.org/mcp-client)
[2] Model Context Protocol Specification: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
[3] MCP Server Examples: [https://github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)
