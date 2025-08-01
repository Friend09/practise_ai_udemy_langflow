# Implementing the Price Comparison Agent in Langflow

This document provides guidance on how to implement the Price Comparison Agent, as depicted in the architecture diagram, within Langflow. This agent demonstrates how an LLM can orchestrate multiple Model Context Protocol (MCP) tools to achieve a complex goal.

## Overview of the Langflow Agent Flow

As clarified, the entire flow is an agentic workflow, with MCP serving as the communication protocol for the LLM to interact with external tools. In Langflow, the `Agent` component acts as the central orchestrator, leveraging various `Tool` components (which can be backed by MCP servers) to perform specific tasks.

## Components and Their Configuration in Langflow

Here’s a breakdown of the components you would use in Langflow to build this agent:

### 1. Chatbot (Input/Output)

*   **Langflow Component**: `Chat Input` and `Chat Output`
*   **Purpose**: These components handle the user interface, allowing the user to provide a query (e.g., "lowest price for dji mavic pro 4") and receive the final answer.
*   **Configuration**: Simply drag and drop these components onto your canvas. The `Chat Input` will connect to the `Agent (LLM)` component, and the `Agent (LLM)` component will connect to the `Chat Output`.

### 2. Agent (LLM)

*   **Langflow Component**: `Agent`
*   **Purpose**: This is the core of your agent. It uses an LLM (e.g., OpenAI GPT models) to understand the user's intent, reason about the necessary steps, select the appropriate tools, and synthesize the final response.
*   **Configuration**:
    *   **Model Provider**: Select your desired LLM provider (e.g., `OpenAI`).
    *   **Model Name**: Choose a suitable model (e.g., `gpt-4-turbo`, `gpt-3.5-turbo`).
    *   **API Key**: Provide your API key for the chosen LLM.
    *   **Agent Instructions**: Provide clear instructions to the LLM about its role. For example:
        ```
        You are a helpful price comparison assistant. Your goal is to find the lowest price for a given product across multiple websites. You have access to tools for web scraping, data processing, and price comparison. When asked for a product price, use your tools to find and compare prices, then report the lowest price and its source.
        ```
    *   **Tools**: This is the crucial part. You will connect the outputs of your MCP Tool components (described below) to the `Tools` input of this `Agent` component. This tells the LLM which external capabilities it has access to.

### 3. Web Scraping Tool (MCP Server)

*   **Langflow Component**: `MCP Tool` (or a custom component if you build your own web scraper directly in Langflow)
*   **Purpose**: This tool is responsible for visiting specified websites and extracting product price information. It acts as an MCP server, exposing a function like `scrape_product_price(product_name: str, website_url: str) -> dict`.
*   **Configuration (if using `MCP Tool` component)**:
    *   **Tool Name**: `web_scraper`
    *   **Function Name**: `scrape_product_price`
    *   **Code**: This would contain the Python code for your web scraping logic. In a real scenario, this might involve libraries like `BeautifulSoup` or `Scrapy`. For a simplified example, it could return mock data.
        ```python
        import requests
        from bs4 import BeautifulSoup

        def scrape_product_price(product_name: str, website_url: str) -> dict:
            """Scrapes the price of a product from a given website."""
            # This is a simplified example. Real web scraping is more complex.
            print(f"Attempting to scrape {product_name} from {website_url}")
            try:
                response = requests.get(website_url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                # Example: Look for a price element (this will vary greatly by website)
                price_element = soup.find(class_="price") # Placeholder
                price = price_element.text.strip() if price_element else "N/A"
                return {"product": product_name, "website": website_url, "price": price, "success": True}
            except Exception as e:
                return {"product": product_name, "website": website_url, "error": str(e), "success": False}
        ```
    *   **Connection**: Connect the output of this `MCP Tool` component to the `Tools` input of your `Agent (LLM)` component.

### 4. Data Processing Tool (MCP Server)

*   **Langflow Component**: `MCP Tool`
*   **Purpose**: This tool takes the raw, potentially messy, scraped data and processes it into a clean, standardized format that the LLM or other tools can easily use. It might handle currency conversion, data type normalization, or error filtering. It exposes a function like `process_scraped_data(raw_data: list) -> list`.
*   **Configuration (if using `MCP Tool` component)**:
    *   **Tool Name**: `data_processor`
    *   **Function Name**: `process_scraped_data`
    *   **Code**: Python code to clean and normalize the data.
        ```python
        def process_scraped_data(raw_data: list) -> list:
            """Processes raw scraped product data into a standardized format."""
            processed_results = []
            for item in raw_data:
                if item.get("success"):
                    try:
                        price_str = item.get("price", "0").replace("$", "").replace(",", "")
                        price = float(price_str)
                        processed_results.append({
                            "product": item.get("product"),
                            "website": item.get("website"),
                            "price": price
                        })
                    except ValueError:
                        print(f"Could not convert price: {item.get("price")}")
                        continue
            return processed_results
        ```
    *   **Connection**: Connect the output of this `MCP Tool` component to the `Tools` input of your `Agent (LLM)` component.

### 5. Price Comparison Tool (MCP Server)

*   **Langflow Component**: `MCP Tool`
*   **Purpose**: This tool takes the processed product data and identifies the lowest price, along with its source. It exposes a function like `find_lowest_price(processed_data: list) -> dict`.
*   **Configuration (if using `MCP Tool` component)**:
    *   **Tool Name**: `price_comparer`
    *   **Function Name**: `find_lowest_price`
    *   **Code**: Python code to compare prices.
        ```python
        def find_lowest_price(processed_data: list) -> dict:
            """Finds the lowest price from a list of processed product data."""
            if not processed_data:
                return {"lowest_price": "N/A", "source": "N/A", "message": "No valid data to compare."}

            lowest_item = None
            for item in processed_data:
                if lowest_item is None or item["price"] < lowest_item["price"]:
                    lowest_item = item
            
            if lowest_item:
                return {"lowest_price": lowest_item["price"], "source": lowest_item["website"], "product": lowest_item["product"], "message": "Lowest price found."}
            else:
                return {"lowest_price": "N/A", "source": "N/A", "message": "Could not determine lowest price."}
        ```
    *   **Connection**: Connect the output of this `MCP Tool` component to the `Tools` input of your `Agent (LLM)` component.

### 6. External Websites

*   **Representation**: This is not a Langflow component but an external entity that the `Web Scraping Tool` interacts with. In your Langflow diagram, you would simply show the connection from the `Web Scraping Tool` to this conceptual external source.

## Building the Flow in Langflow

1.  **Start a New Project**: As described in the previous guide, create a new project in Langflow.
2.  **Add `Chat Input` and `Chat Output`**: Place these on the canvas.
3.  **Add `Agent` Component**: Drag and drop the `Agent` component. Configure it with your LLM provider, API key, and agent instructions.
4.  **Add `MCP Tool` Components**: Add three `MCP Tool` components for `Web Scraping`, `Data Processing`, and `Price Comparison`. Configure each with its respective `Tool Name`, `Function Name`, and `Code`.
5.  **Connect Components**:
    *   Connect `Chat Input` to the `Input` of the `Agent` component.
    *   Connect the outputs of the `Web Scraping Tool`, `Data Processing Tool`, and `Price Comparison Tool` to the `Tools` input of the `Agent` component.
    *   Connect the `Response` output of the `Agent` component to the `Chat Output`.

## How the Agent Orchestrates the MCP Tools

When a user provides input (e.g., "dji mavic pro 4"), the `Agent (LLM)` component will:

1.  **Receive Input**: The LLM processes the user's request.
2.  **Plan**: Based on its instructions and available tools, the LLM determines that it needs to scrape websites for prices.
3.  **Call Web Scraping Tool**: The LLM invokes the `web_scraper` tool (specifically, its `scrape_product_price` function), providing the product name and a list of website URLs (which it might generate or retrieve from another source, or you could hardcode a few for demonstration).
4.  **Receive Raw Data**: The `web_scraper` MCP server performs the scraping and returns the raw data to the LLM.
5.  **Call Data Processing Tool**: The LLM then recognizes that the raw data needs processing. It invokes the `data_processor` tool (its `process_scraped_data` function), passing the raw data.
6.  **Receive Processed Data**: The `data_processor` MCP server cleans and standardizes the data, returning it to the LLM.
7.  **Call Price Comparison Tool**: With the clean data, the LLM calls the `price_comparer` tool (its `find_lowest_price` function) to identify the best deal.
8.  **Receive Final Result**: The `price_comparer` MCP server returns the lowest price and its source to the LLM.
9.  **Generate Output**: The LLM synthesizes this information into a user-friendly response and sends it to the `Chat Output` component, which is then displayed to the user.

## Testing in Langflow

After building your flow, you can test it directly within Langflow's playground. Enter a query in the chat interface, and observe the execution path and the responses from each component. Langflow's visual debugger will help you see how the LLM calls each tool and processes the information.

This setup provides a powerful and flexible way to build complex agentic applications by modularizing functionality into MCP-backed tools, all orchestrated by an intelligent LLM within Langflow.


