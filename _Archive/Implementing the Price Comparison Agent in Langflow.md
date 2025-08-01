# Implementing the Price Comparison Agent in Langflow

This document provides guidance on how to implement the Price Comparison Agent, as depicted in the architecture diagram, within Langflow. This agent demonstrates how an LLM can orchestrate multiple Model Context Protocol (MCP) tools to achieve a complex goal.

> **Note for Langflow v1.5.13 Users**: This guide has been updated for Langflow v1.5.13, which still uses the `MCP Tools` component name (not `MCP Connection` as used in some documentation references).

## Overview of the Langflow Agent Flow

As clarified, the entire flow is an agentic workflow, with MCP (Model Context Protocol) serving as the communication protocol for the LLM to interact with external tools. In Langflow, the `Agent` component acts as the central orchestrator, leveraging various `Tool` components (which are backed by MCP servers) to perform specific tasks.

**Important Terminology:**
- **MCP (Model Context Protocol)**: A standardized way for LLMs to communicate with external tools and data sources
- **MCP Connection**: The Langflow component that configures and exposes MCP servers to agent components
- **MCP Server**: A service that provides tools or resources to an LLM via the Model Context Protocol
- **Tool**: A function that an LLM can call to perform a specific task

## Components and Their Configuration in Langflow

Here’s a breakdown of the components you would use in Langflow to build this agent:

### 1. Chatbot (Input/Output)

- **Langflow Component**: `Chat Input` and `Chat Output`
- **Purpose**: These components handle the user interface, allowing the user to provide a query (e.g., "lowest price for dji mavic pro 4") and receive the final answer.
- **Configuration**: Simply drag and drop these components onto your canvas. The `Chat Input` will connect to the `Agent (LLM)` component, and the `Agent (LLM)` component will connect to the `Chat Output`.

### 2. Agent (LLM)

- **Langflow Component**: `Agent`
- **Purpose**: This is the core of your agent. It uses an LLM (e.g., OpenAI GPT models) to understand the user's intent, reason about the necessary steps, select the appropriate tools, and synthesize the final response.
- **Configuration**:
  - **Model Provider**: Select your desired LLM provider (e.g., `OpenAI`).
  - **Model Name**: Choose a suitable model (e.g., `gpt-4-turbo`, `gpt-3.5-turbo`).
  - **API Key**: Provide your API key for the chosen LLM.
  - **Agent Instructions**: Provide clear instructions to the LLM about its role. For example:
    ```
    You are a helpful price comparison assistant. Your goal is to find the lowest price for a given product across multiple websites. You have access to tools for web scraping, data processing, and price comparison. When asked for a product price, use your tools to find and compare prices, then report the lowest price and its source.
    ```
  - **Tools**: This is the crucial part. You will connect the outputs of your MCP Tool components (described below) to the `Tools` input of this `Agent` component. This tells the LLM which external capabilities it has access to.

### 3. Web Scraping Tool (MCP Server)

> **⚠️ Note**: In Langflow v1.5.13, this component is still called `MCP Tools` rather than `MCP Connection`. The functionality is the same, just the name differs.

- **Langflow Component**: `MCP Tools`
- **Purpose**: This tool is responsible for visiting specified websites and extracting product price information. It acts as an MCP server, exposing a function like `scrape_product_price(product_name: str, website_url: str) -> dict`.
- **Configuration**:

  #### Step 1: Add MCP Tools Component to Canvas
  - Drag and drop the `MCP Tools` component onto your canvas

  #### Step 2: Create an MCP Server Definition
  - Click on the MCP Tools component to open its configuration panel
  - Click on "Add MCP Server"
  - Select the "JSON" tab (other options are "STDIO" and "SSE")

  #### Step 3: Configure the JSON Definition
  - Paste the following JSON configuration into the editor:

```json
{
  "name": "WebScraperServer",
  "transport": "json",
  "description": "Web scraping tools for price comparison",
  "tools": [
    {
      "name": "web_scraper",
      "description": "Scrapes product prices from websites",
      "function": {
        "name": "scrape_product_price",
        "description": "Scrapes the price of a product from a given website",
        "parameters": {
          "type": "object",
          "properties": {
            "product_name": {
              "type": "string",
              "description": "Name of the product to search for"
            },
            "website_url": {
              "type": "string",
              "description": "URL of the website to scrape"
            }
          },
          "required": ["product_name", "website_url"]
        }
      },
      "code": "import requests\nfrom bs4 import BeautifulSoup\n\ndef scrape_product_price(product_name, website_url):\n    print(f\"Attempting to scrape {product_name} from {website_url}\")\n    try:\n        response = requests.get(website_url, timeout=10)\n        soup = BeautifulSoup(response.text, 'html.parser')\n        price_element = soup.find(class_=\"price\")\n        price = price_element.text.strip() if price_element else \"N/A\"\n        return {\"product\": product_name, \"website\": website_url, \"price\": price, \"success\": True}\n    except Exception as e:\n        return {\"product\": product_name, \"website\": website_url, \"error\": str(e), \"success\": False}\n"
    }
  ]
}
```

  #### Step 4: Add and Select the Server
  - Click "Add Server" to create the MCP server
  - The server should appear in the dropdown list - select it to use
  - If you get "No valid MCP server found" errors:
    - Make sure the JSON is valid with no syntax errors
    - Ensure all required fields (name, type, tools) are present
    - Verify that the code doesn't contain encoding or special character issues

  #### Step 5: Connection
  - Connect the output of this `MCP Tools` component to the `Tools` input of your `Agent (LLM)` component

### 4. Data Processing Tool (MCP Server)

- **Langflow Component**: `MCP Tools`
- **Purpose**: This tool takes the raw, potentially messy, scraped data and processes it into a clean, standardized format that the LLM or other tools can easily use. It might handle currency conversion, data type normalization, or error filtering. It exposes a function like `process_scraped_data(raw_data: list) -> list`.
- **Configuration**:

  #### Step 1: Add Another MCP Tools Component
  - Drag and drop another `MCP Tools` component onto your canvas
  - Follow the same initial steps as with the Web Scraping tool

  #### Step 2: Configure the JSON Definition
  - Paste the following JSON configuration into the editor:

    ```json
    {
      "name": "DataProcessingServer",
      "transport": "json",
      "description": "Data processing tools for price comparison",
      "tools": [
        {
          "name": "data_processor",
          "description": "Processes raw scraped data into a standardized format",
          "function": {
            "name": "process_scraped_data",
            "description": "Processes raw scraped product data into a standardized format",
            "parameters": {
              "type": "object",
              "properties": {
                "raw_data": {
                  "type": "array",
                  "description": "List of raw scraped data items",
                  "items": {
                    "type": "object"
                  }
                }
              },
              "required": ["raw_data"]
            }
          },
          "code": "def process_scraped_data(raw_data):\n    \"\"\"Processes raw scraped product data into a standardized format.\"\"\"\n    processed_results = []\n    for item in raw_data:\n        if item.get(\"success\"):\n            try:\n                price_str = item.get(\"price\", \"0\").replace(\"$\", \"\").replace(\",\", \"\")\n                price = float(price_str)\n                processed_results.append({\n                    \"product\": item.get(\"product\"),\n                    \"website\": item.get(\"website\"),\n                    \"price\": price\n                })\n            except ValueError:\n                print(f\"Could not convert price: {item.get('price')}\")\n                continue\n    return processed_results"
        }
      ]
    }
    ```

  #### Step 3: Add and Select the Server
  - Click "Add Server" to create the MCP server
  - Select this new server from the dropdown list

  #### Step 4: Connection
  - Connect the output of this `MCP Tools` component to the `Tools` input of your `Agent (LLM)` component

### 5. Price Comparison Tool (MCP Server)

- **Langflow Component**: `MCP Tools`
- **Purpose**: This tool takes the processed product data and identifies the lowest price, along with its source. It exposes a function like `find_lowest_price(processed_data: list) -> dict`.
- **Configuration**:

  #### Step 1: Add Another MCP Tools Component
  - Drag and drop another `MCP Tools` component onto your canvas
  - Follow the same initial steps as with the previous tools

  #### Step 2: Configure the JSON Definition
  - Paste the following JSON configuration into the editor:

    ```json
    {
      "name": "PriceComparisonServer",
      "transport": "json",
      "description": "Price comparison tools",
      "tools": [
        {
          "name": "price_comparer",
          "description": "Finds the lowest price from a list of processed product data",
          "function": {
            "name": "find_lowest_price",
            "description": "Finds the lowest price from a list of processed product data",
            "parameters": {
              "type": "object",
              "properties": {
                "processed_data": {
                  "type": "array",
                  "description": "List of processed product data items",
                  "items": {
                    "type": "object"
                  }
                }
              },
              "required": ["processed_data"]
            }
          },
          "code": "def find_lowest_price(processed_data):\n    \"\"\"Finds the lowest price from a list of processed product data.\"\"\"\n    if not processed_data:\n        return {\"lowest_price\": \"N/A\", \"source\": \"N/A\", \"message\": \"No valid data to compare.\"}\n\n    lowest_item = None\n    for item in processed_data:\n        if lowest_item is None or item[\"price\"] < lowest_item[\"price\"]:\n            lowest_item = item\n\n    if lowest_item:\n        return {\"lowest_price\": lowest_item[\"price\"], \"source\": lowest_item[\"website\"], \"product\": lowest_item[\"product\"], \"message\": \"Lowest price found.\"}\n    else:\n        return {\"lowest_price\": \"N/A\", \"source\": \"N/A\", \"message\": \"Could not determine lowest price.\"}"
        }
      ]
    }
    ```

  #### Step 3: Add and Select the Server
  - Click "Add Server" to create the MCP server
  - Select this new server from the dropdown list

  #### Step 4: Connection
  - Connect the output of this `MCP Tools` component to the `Tools` input of your `Agent (LLM)` component

### 6. External Websites

- **Representation**: This is not a Langflow component but an external entity that the `Web Scraping Tool` interacts with. In your Langflow diagram, you would simply show the connection from the `Web Scraping Tool` to this conceptual external source.

## Building the Flow in Langflow v1.5.13

1.  **Start a New Project**:
    - Click the "New Project" button in Langflow
    - Give your project a descriptive name like "Price Comparison Agent"

2.  **Add Basic Components**:
    - Drag and drop `Chat Input` component onto your canvas
    - Drag and drop `Chat Output` component onto your canvas
    - Place them on the left and right sides respectively

3.  **Add Agent Component**:
    - In Langflow v1.5.13, search for and add the `Agent` component (or `Tool Calling Agent` if available)
    - Configure it with:
      - **Model Provider**: Select `OpenAI` from the dropdown
      - **API Key**: Enter your OpenAI API key
      - **Model Name**: Choose `gpt-4-turbo` or `gpt-3.5-turbo`
      - **System Message**: Enter enhanced instructions (see below):
      ```
      You are a price comparison assistant that helps users find the best deals.

      You have access to the following tools:
      1. web_scraper: Use this to extract prices from websites. Always provide both the product name and full website URL.
      2. data_processor: Use this to clean price data obtained from web scraping.
      3. price_comparer: Use this to find the lowest price from processed data.

      When asked about prices, ALWAYS follow this exact sequence:
      1. Use web_scraper to gather price data
      2. Process the data with data_processor
      3. Compare prices with price_comparer
      4. Report the lowest price and source to the user

      Never make up prices - only report what you find using your tools.
      ```

4.  **Add MCP Tools Components**:
    - Search for and add three `MCP Tools` components to the canvas
    - Position them in a row between the Chat Input and Agent components
    - Label them descriptively as "Web Scraper", "Data Processor", and "Price Comparer"

5.  **Configure Each MCP Tool**:
    - Click on each MCP Tools component to open its configuration panel
    - Click "Add MCP Server" to open the configuration dialog
    - Select the "JSON" tab (important for our configuration)
    - Carefully paste the appropriate JSON configuration for each tool (from the sections above)
    - Remember to use `"transport": "json"` not `"type": "json"` in each configuration
    - After adding, select the server from the dropdown that appears in each MCP Tools component

6.  **Create Connections**:
    - Connect `Chat Input` output to the `Agent` component's input
    - Connect all three `MCP Tools` outputs to the `Tools` input of your `Agent` component
      (Langflow will allow multiple connections into the same input)
    - Connect the `Response` output of the `Agent` component to the `Chat Output`

7.  **Save and Test the Flow**:
    - Click the "Save" button to save your flow
    - Click the "Chat" button to open the testing interface
    - Test with: "What tools do you have available?" to verify tool connections
    - Then test with a real query like: "Find the price of Sony WH-1000XM5 on amazon.com"

8.  **Debugging Issues**:
    - If you get "No valid MCP server found" errors:
      - Validate the JSON in an external JSON validator
      - Use `"transport": "json"` not `"type": "json"`
      - Try simplifying the JSON to isolate the issue
    - If tools aren't showing up:
      - Check all connections are properly established
      - Verify the logs panel for any Python errors

## How the Agent Orchestrates the MCP Tools in Langflow

When a user provides input (e.g., "Find the price of DJI Mavic Pro 4 on Amazon and BestBuy"), the agent flow executes through these steps:

1. **User Input Processing**:
   - The query enters through the `Chat Input` component
   - It's passed to the `Agent (LLM)` component

2. **Agent Planning**:
   - The LLM analyzes the request and identifies this as a price comparison task
   - It plans to use the three tools in sequence (based on system instructions)
   - The agent formulates appropriate parameters for each tool call

3. **Web Scraping Execution**:
   ```
   Tool: web_scraper
   Params: {
     "product_name": "DJI Mavic Pro 4",
     "website_url": "https://www.amazon.com/DJI-Mavic-Pro-4"
   }
   ```
   - The MCP server processes the request using BeautifulSoup
   - Returns structured data about the product and price
   - The agent repeats this for the second website

4. **Data Processing Stage**:
   ```
   Tool: data_processor
   Params: {
     "raw_data": [
       {"product": "DJI Mavic Pro 4", "website": "https://www.amazon.com/...", "price": "$1,599.99", "success": true},
       {"product": "DJI Mavic Pro 4", "website": "https://www.bestbuy.com/...", "price": "$1,499.99", "success": true}
     ]
   }
   ```
   - The data processor cleans and standardizes the raw price data
   - Converts strings like "$1,599.99" to numeric values (1599.99)

5. **Price Comparison**:
   ```
   Tool: price_comparer
   Params: {
     "processed_data": [
       {"product": "DJI Mavic Pro 4", "website": "https://www.amazon.com/...", "price": 1599.99},
       {"product": "DJI Mavic Pro 4", "website": "https://www.bestbuy.com/...", "price": 1499.99}
     ]
   }
   ```
   - The price comparison tool identifies the lowest price
   - Returns the best deal with source information

6. **Result Synthesis**:
   - The agent formulates a clear response highlighting the findings
   - The response includes the lowest price, the source, and any relevant notes
   - This information is passed to the `Chat Output` component and displayed to the user

All these interactions happen through the MCP (Model Context Protocol), which standardizes how LLMs communicate with external tools. Langflow visualizes this process in its interface, making it easy to debug and optimize.

## Testing in Langflow

After building your flow, you can test it directly within Langflow's playground:

1. **Save Your Flow**: Make sure to save your flow by clicking the "Save" button.

2. **Test the Agent**: Click on the "Chat" button to open the chat interface.

3. **Verify Tool Registration**: First, ask the agent "What tools do you have access to?" to confirm all three MCP tools are properly registered.

4. **Test with Sample Queries**: Try queries like:
   - "What's the lowest price for a DJI Mavic Pro 4?"
   - "Find the best price for an iPhone 15 Pro"
   - "Compare prices for Sony WH-1000XM5 headphones"

5. **Observe Tool Usage**: Watch how the agent:
   - Uses the web scraper tool to gather price data
   - Processes the raw data with the data processor tool
   - Identifies the lowest price with the price comparer tool

6. **Debug Issues**: If the agent isn't using tools correctly:
   - Check the "Logs" panel for error messages
   - Verify your JSON configurations for syntax errors
   - Make sure all connections between components are correct
   - Ensure your system prompt clearly instructs the agent on using the tools

This setup provides a powerful and flexible way to build complex agentic applications by modularizing functionality into MCP-backed tools, all orchestrated by an intelligent LLM within Langflow.

## Common Troubleshooting

1. **"No valid MCP server found"**:
   - Validate your JSON syntax using a JSON validator (like [JSONLint](https://jsonlint.com/))
   - Ensure all required fields are present (name, transport, tools)
   - Use "transport": "json" instead of "type": "json" (this is critical in Langflow v1.5.13)
   - Check that the function parameters and code are properly escaped
   - Remove any extra spaces, newlines, or quotes that might break the JSON
   - Try pasting the JSON in small chunks and validating each part

2. **Agent doesn't use the tools**:
   - Make sure all MCP Tools components are properly connected to the Agent's Tools input
   - Check that the system prompt explicitly mentions the available tools
   - Try simpler queries that clearly require tool usage
   - Verify the agent can see the tools by asking "What tools do you have available?"
   - Add explicit instructions in the system prompt like "When asked about prices, always use your web_scraper tool"

3. **Execution errors**:
   - Check the Logs panel for Python errors in your code
   - Verify that required libraries (requests, BeautifulSoup) are installed in your Langflow environment
   - Test tools individually before combining them
   - Add more error handling and logging in your Python code
   - Try simpler versions of the tools first to isolate issues

## Advanced Tips for Langflow v1.5.13

1. **Installing Required Packages**:
   - Langflow needs access to any Python libraries used in your MCP tools
   - Install required packages in your Langflow environment:
     ```bash
     # For local installations
     pip install requests beautifulsoup4

     # For Docker installations
     docker exec -it langflow-container pip install requests beautifulsoup4
     ```
   - Restart Langflow after installing new packages

   Alternatively, if using Langflow Desktop, you may need to create a custom environment:
   ```bash
   # Create a virtual environment for Langflow
   python -m venv langflow_env
   source langflow_env/bin/activate  # On Windows: langflow_env\Scripts\activate
   pip install langflow requests beautifulsoup4
   langflow run
   ```

2. **JSON Schema Validation**:
   - The parameter schema is critical for the agent to understand how to use your tools
   - Include clear descriptions for each parameter
   - Use appropriate types ("string", "number", "array", "object")
   - Always include "required" fields to guide the agent

3. **Testing Strategy**:
   - Test each MCP tool individually before connecting to the agent
   - Use the "Response" output of each MCP tool to verify it works
   - Start with simple test cases (e.g., scrape a single known website)
   - Add complexity gradually as each component works

4. **Practical Examples**:
   - For web scraping testing, use websites with consistent price elements like:
     - Amazon product pages (using `.a-price` class)
     - BestBuy product pages (using `.priceView-customer-price` class)
     - Target product pages (using `.styles__CurrentPriceValue` class)
   - Test queries:
     - "Find the price of iPhone 15 Pro on apple.com"
     - "Compare prices for Sony WH-1000XM5 on bestbuy.com and amazon.com"

5. **Agent System Instructions**:
   For optimal tool use, enhance your agent instructions:

   ```
   You are a price comparison assistant that helps users find the best deals.

   You have access to the following tools:
   1. web_scraper: Use this to extract prices from websites. Always provide both the product name and full website URL.
   2. data_processor: Use this to clean price data obtained from web scraping.
   3. price_comparer: Use this to find the lowest price from processed data.

   When asked about prices:
   - ALWAYS use the web_scraper tool first to gather price data
   - ALWAYS process the data with data_processor
   - ALWAYS compare prices with price_comparer
   - ALWAYS show the full process and reasoning

   Never make up prices - only report what you find using your tools.
   ```
