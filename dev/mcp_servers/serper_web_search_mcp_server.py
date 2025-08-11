import requests
import json
import sys
import time
import os
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file", file=sys.stderr)
except ImportError:
    print("python-dotenv not installed, using system environment variables only", file=sys.stderr)
except Exception as e:
    print(f"Error loading .env file: {e}", file=sys.stderr)

@dataclass
class SearchResult:
    """
    Represents a search result from Serper API.
    """
    title: str
    url: str
    snippet: str
    domain: str
    position: int
    price: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

class SerperWebSearchAnalyzer:
    """
    SerperWebSearchAnalyzer provides a server for searching products using Serper API.

    This class initializes a FastMCP server with tools for searching products across the web
    using Google Search via Serper API. It includes support for product-specific searches,
    price extraction, and result filtering.

    Methods:
        __init__(): Initializes the FastMCP server and registers search tools.
        _register_tools(): Registers search tools with the MCP server.
        _make_search_request(): Makes API request to Serper with proper error handling.
        _extract_domain(): Extracts domain from URL.
        _filter_ecommerce_results(): Filters results to focus on e-commerce sites.
        _parse_search_results(): Parses and structures search results.
        run(): Starts the MCP server and handles fatal errors gracefully.
    """

    def __init__(self):
        """
        Initializes the SerperWebSearchAnalyzer with MCP server and API configuration.
        """
        self.mcp = FastMCP("serper_web_search_analyzer")
        print("Serper Web Search MCP Server initialized", file=sys.stderr)

        # Serper API configuration - read from environment variables
        self.api_key = os.getenv('SERPER_APIKEY') or os.getenv('SERPER_API_KEY')
        if not self.api_key:
            print("ERROR: SERPER_APIKEY or SERPER_API_KEY environment variable not found!", file=sys.stderr)
            print("Please set your Serper API key in the .env file or environment", file=sys.stderr)
            sys.exit(1)

        self.base_url = "https://google.serper.dev/search"
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }        # Common e-commerce domains for filtering
        self.ecommerce_domains = {
            'amazon.com', 'ebay.com', 'walmart.com', 'target.com',
            'bestbuy.com', 'newegg.com', 'etsy.com', 'shopify.com',
            'alibaba.com', 'aliexpress.com', 'costco.com', 'homedepot.com',
            'lowes.com', 'wayfair.com', 'overstock.com', 'zappos.com'
        }

        self._register_tools()

    def _extract_domain(self, url: str) -> str:
        """
        Extracts domain name from URL.

        Args:
            url: Full URL

        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace('www.', '')
        except Exception:
            return 'unknown'

    def _make_search_request(self, query: str, num_results: int = 10, country: str = "us") -> Optional[Dict[str, Any]]:
        """
        Makes API request to Serper with proper error handling.

        Args:
            query: Search query
            num_results: Number of results to return
            country: Country code for localized results

        Returns:
            API response data or None if failed
        """
        try:
            payload = json.dumps({
                "q": query,
                "num": num_results,
                "gl": country
            })

            print(f"Making Serper API request for query: {query}", file=sys.stderr)
            response = requests.post(self.base_url, headers=self.headers, data=payload, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Serper API request failed: {e}", file=sys.stderr)
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse Serper API response: {e}", file=sys.stderr)
            return None

    def _filter_ecommerce_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters results to focus on e-commerce sites.

        Args:
            results: List of search results

        Returns:
            Filtered list containing only e-commerce results
        """
        ecommerce_results = []

        for result in results:
            url = result.get('link', '')
            domain = self._extract_domain(url)

            # Check if domain is in our e-commerce list
            if any(ecom_domain in domain for ecom_domain in self.ecommerce_domains):
                ecommerce_results.append(result)
            # Also include results that mention price-related keywords
            elif any(keyword in result.get('snippet', '').lower() for keyword in ['price', 'buy', 'shop', 'store', '$']):
                ecommerce_results.append(result)

        return ecommerce_results

    def _parse_search_results(self, api_response: Dict[str, Any], filter_ecommerce: bool = True) -> List[SearchResult]:
        """
        Parses and structures search results from Serper API response.

        Args:
            api_response: Raw API response from Serper
            filter_ecommerce: Whether to filter for e-commerce sites only

        Returns:
            List of structured SearchResult objects
        """
        results = []
        organic_results = api_response.get('organic', [])

        if filter_ecommerce:
            organic_results = self._filter_ecommerce_results(organic_results)

        for i, result in enumerate(organic_results):
            try:
                search_result = SearchResult(
                    title=result.get('title', ''),
                    url=result.get('link', ''),
                    snippet=result.get('snippet', ''),
                    domain=self._extract_domain(result.get('link', '')),
                    position=result.get('position', i + 1)
                )

                # Try to extract price from snippet if available
                snippet = result.get('snippet', '')
                if '$' in snippet:
                    # Simple price extraction - could be enhanced
                    import re
                    price_match = re.search(r'\$[\d,]+\.?\d*', snippet)
                    if price_match:
                        search_result.price = price_match.group()

                results.append(search_result)

            except Exception as e:
                print(f"Error parsing search result: {e}", file=sys.stderr)
                continue

        return results

    def _register_tools(self):
        """
        Registers search tools with the MCP server.
        """

        @self.mcp.tool()
        async def search_products(product_name: str, max_results: int = 10, include_price_sites_only: bool = True) -> dict:
            """
            Searches for products using Serper API and returns e-commerce results.

            Args:
                product_name: Name of the product to search for
                max_results: Maximum number of results to return (default: 10)
                include_price_sites_only: Whether to filter for e-commerce sites only (default: True)

            Returns:
                Dictionary containing search results with product information and URLs
            """
            print(f"Searching for product: {product_name}", file=sys.stderr)

            # Enhance search query for better product results
            enhanced_query = f"{product_name} price buy shop"

            # Make API request
            api_response = self._make_search_request(enhanced_query, num_results=max_results)

            if not api_response:
                return {
                    "product_name": product_name,
                    "success": False,
                    "error": "Failed to get search results from Serper API",
                    "results": []
                }

            # Parse results
            search_results = self._parse_search_results(api_response, include_price_sites_only)

            # Convert to dictionary format
            results_data = []
            for result in search_results:
                result_dict = {
                    "title": result.title,
                    "url": result.url,
                    "domain": result.domain,
                    "snippet": result.snippet,
                    "position": result.position
                }

                if result.price:
                    result_dict["price_mentioned"] = result.price

                results_data.append(result_dict)

            print(f"Found {len(results_data)} relevant results for {product_name}", file=sys.stderr)

            return {
                "product_name": product_name,
                "success": True,
                "total_results": len(results_data),
                "ecommerce_filtered": include_price_sites_only,
                "results": results_data,
                "search_metadata": {
                    "query_used": enhanced_query,
                    "api_response_status": "success" if api_response else "failed"
                }
            }

        @self.mcp.tool()
        async def search_product_with_specifications(product_name: str, specifications: str = "", max_results: int = 15) -> dict:
            """
            Searches for products with specific specifications or features.

            Args:
                product_name: Name of the product to search for
                specifications: Additional specifications or features (e.g., "16GB RAM", "black color")
                max_results: Maximum number of results to return (default: 15)

            Returns:
                Dictionary containing detailed search results for specified product
            """
            print(f"Searching for {product_name} with specifications: {specifications}", file=sys.stderr)

            # Build comprehensive search query
            if specifications:
                search_query = f"{product_name} {specifications} buy price shop"
            else:
                search_query = f"{product_name} buy price shop"

            # Make API request
            api_response = self._make_search_request(search_query, num_results=max_results)

            if not api_response:
                return {
                    "product_name": product_name,
                    "specifications": specifications,
                    "success": False,
                    "error": "Failed to get search results from Serper API",
                    "results": []
                }

            # Parse all results (not just e-commerce)
            search_results = self._parse_search_results(api_response, filter_ecommerce=False)

            # Separate e-commerce and informational results
            ecommerce_results = []
            info_results = []

            for result in search_results:
                result_dict = {
                    "title": result.title,
                    "url": result.url,
                    "domain": result.domain,
                    "snippet": result.snippet,
                    "position": result.position
                }

                if result.price:
                    result_dict["price_mentioned"] = result.price

                # Categorize results
                if any(ecom_domain in result.domain for ecom_domain in self.ecommerce_domains):
                    ecommerce_results.append(result_dict)
                else:
                    info_results.append(result_dict)

            print(f"Found {len(ecommerce_results)} e-commerce and {len(info_results)} informational results", file=sys.stderr)

            return {
                "product_name": product_name,
                "specifications": specifications,
                "success": True,
                "total_results": len(search_results),
                "ecommerce_results": ecommerce_results,
                "informational_results": info_results,
                "search_metadata": {
                    "query_used": search_query,
                    "ecommerce_count": len(ecommerce_results),
                    "info_count": len(info_results)
                }
            }

        @self.mcp.tool()
        async def get_product_urls_for_comparison(product_name: str, target_sites: Optional[List[str]] = None) -> dict:
            """
            Gets product URLs specifically for price comparison from major e-commerce sites.

            Args:
                product_name: Name of the product to search for
                target_sites: Optional list of specific sites to target (e.g., ["amazon.com", "walmart.com"])

            Returns:
                Dictionary containing URLs organized by e-commerce site for easy price comparison
            """
            print(f"Getting comparison URLs for: {product_name}", file=sys.stderr)

            # Default target sites if none specified
            if not target_sites:
                target_sites = ["amazon.com", "walmart.com", "target.com", "bestbuy.com", "ebay.com"]

            # Search for product
            search_query = f"{product_name} site:({' OR site:'.join(target_sites)})"
            api_response = self._make_search_request(search_query, num_results=20)

            if not api_response:
                return {
                    "product_name": product_name,
                    "target_sites": target_sites,
                    "success": False,
                    "error": "Failed to get search results from Serper API",
                    "urls_by_site": {}
                }

            # Parse and organize results by site
            search_results = self._parse_search_results(api_response, filter_ecommerce=True)
            urls_by_site = {site: [] for site in target_sites}

            for result in search_results:
                for site in target_sites:
                    if site in result.domain:
                        urls_by_site[site].append({
                            "url": result.url,
                            "title": result.title,
                            "snippet": result.snippet,
                            "price_mentioned": result.price
                        })
                        break

            # Remove empty sites
            urls_by_site = {site: urls for site, urls in urls_by_site.items() if urls}

            total_urls = sum(len(urls) for urls in urls_by_site.values())
            print(f"Found {total_urls} URLs across {len(urls_by_site)} sites", file=sys.stderr)

            return {
                "product_name": product_name,
                "target_sites": target_sites,
                "success": True,
                "total_urls_found": total_urls,
                "sites_with_results": len(urls_by_site),
                "urls_by_site": urls_by_site,
                "search_metadata": {
                    "query_used": search_query
                }
            }

    def run(self):
        """
        Runs the MCP server using stdio transport with error handling.
        """
        try:
            print("Starting Serper Web Search MCP Server...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Fatal Error in Serper Web Search MCP Server: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    # Entry point for running the SerperWebSearchAnalyzer server
    analyzer = SerperWebSearchAnalyzer()
    analyzer.run()
