# Project: practise_ai_udemy_langflow

This project implements various Model Context Protocol (MCP) servers for AI-powered workflows, focusing on price comparison and web data processing.

## Serper Web Search MCP Server

The Serper Web Search MCP Server provides web search capabilities using the Serper API, allowing for product discovery across the internet. This server is a critical component of the price comparison pipeline.

### Features

- **Product Search**: Search for products across e-commerce websites using Google Search via Serper API
- **E-commerce Filtering**: Automatically filters results to focus on shopping sites
- **Price Extraction**: Attempts to extract price information from search snippets
- **Site-specific Targeting**: Search specific e-commerce sites for comparison

### MCP Tools

1. **`search_products`**

   - Searches for products and returns e-commerce results
   - Parameters:
     - `product_name` (str): Name of the product to search for
     - `max_results` (int, default=10): Maximum number of results to return
     - `include_price_sites_only` (bool, default=True): Filter for e-commerce sites only

2. **`search_product_with_specifications`**

   - Searches for products with specific features or specifications
   - Parameters:
     - `product_name` (str): Name of the product to search for
     - `specifications` (str, default=""): Additional specifications or features
     - `max_results` (int, default=15): Maximum number of results to return

3. **`get_product_urls_for_comparison`**
   - Gets product URLs organized by e-commerce site for price comparison
   - Parameters:
     - `product_name` (str): Name of the product to search for
     - `target_sites` (Optional[List[str]]): Specific sites to target

### Integration

The Serper web search server integrates with other MCP servers in the price comparison pipeline:

1. **Serper Web Search** → Find product URLs
2. **Web Scraping** → Extract detailed product data from URLs
3. **Data Processing** → Clean and standardize the scraped data
4. **Price Comparison** → Analyze and compare prices

### API Configuration

- **Environment Variable**: `SERPER_APIKEY` or `SERPER_API_KEY`
- **Setup**:
  - Create a `.env` file with your API key: `SERPER_APIKEY=your_actual_api_key_here`
  - Or set as environment variable: `export SERPER_APIKEY=your_actual_api_key_here`

### Running the Server

```bash
python /path/to/serper_web_search_mcp_server.py
```

## Project Structure

- `/dev/mcp_servers/` - Contains all MCP server implementations
- `/data/` - Data storage directory
- `/notebooks/` - Jupyter notebooks for testing and demonstrations
- `/notes/` - Documentation and notes on implementations
