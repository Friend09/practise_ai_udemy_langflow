import sys
import json
import re
from mcp.server.fastmcp import FastMCP

class DataProcessingAnalyzer:
    """
    DataProcessingAnalyzer sets up an MCP server to process scraped product data.
    It registers tools for data processing and runs the server using stdio transport.
    """

    def __init__(self):
        """
        Initializes the DataProcessingAnalyzer, sets up the MCP server,
        and registers the data processing tools.
        """
        self.mcp = FastMCP("data_processing_analyzer")
        print("Data Processing MCP Server initialized", file=sys.stderr)
        self._register_tools()

    def _register_tools(self):
        """
        Registers the data processing tool with the MCP server.
        """

        @self.mcp.tool()
        async def process_scraped_data(raw_data: dict) -> dict:
            """
            Processes raw scraped product data into a standardized format.

            Args:
                raw_data (dict): Dictionary containing scraped product data.

            Returns:
                dict: Dictionary with processed product data.
            """
            print("Processing scraped data", file=sys.stderr)
            processed_results = []

            # Iterate over each item in the scraped results
            for item in raw_data.get("results", []):
                if item.get("success"):
                    try:
                        # Extract numeric price from string
                        price_str = item.get("price", "0")
                        # Remove $ and commas, then extract the numeric value
                        price_match = re.search(r'[\d,]+\.?\d*', price_str.replace("$", "").replace(",", ""))
                        price = float(price_match.group()) if price_match else 0.0

                        # Append processed item to results
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
        """
        Runs the MCP server using stdio transport.
        Handles fatal errors gracefully.
        """
        try:
            print("Running Data Processing MCP Server...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in MCP Server: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    # Entry point for running the DataProcessingAnalyzer server
    analyzer = DataProcessingAnalyzer()
    analyzer.run()
