#!/usr/bin/env python3
"""
Test script for the Serper Web Search MCP Server.
This script tests the basic functionality of the Serper MCP server.
"""

import asyncio
import sys
import os

# Add the mcp_servers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp_servers'))

from serper_web_search_mcp_server import SerperWebSearchAnalyzer

async def test_serper_search():
    """Test the Serper web search functionality."""

    print("Testing Serper Web Search MCP Server...")
    print("=" * 50)

    # Initialize the analyzer
    analyzer = SerperWebSearchAnalyzer()

    # Test 1: Basic product search
    print("\n1. Testing basic product search for 'iPhone 15'...")
    try:
        # Access the registered tools
        search_tool = None
        for tool in analyzer.mcp.tools:
            if tool.name == "search_products":
                search_tool = tool
                break

        if search_tool:
            result = await search_tool.func("iPhone 15", max_results=5, include_price_sites_only=True)
            print(f"Success: Found {result.get('total_results', 0)} results")
            print(f"Sample result domains: {[r.get('domain') for r in result.get('results', [])[:3]]}")
        else:
            print("Error: search_products tool not found")

    except Exception as e:
        print(f"Error in basic search test: {e}")

    # Test 2: Product search with specifications
    print("\n2. Testing product search with specifications...")
    try:
        spec_tool = None
        for tool in analyzer.mcp.tools:
            if tool.name == "search_product_with_specifications":
                spec_tool = tool
                break

        if spec_tool:
            result = await spec_tool.func("MacBook Pro", specifications="16GB RAM M3", max_results=5)
            print(f"Success: Found {result.get('total_results', 0)} total results")
            print(f"E-commerce results: {len(result.get('ecommerce_results', []))}")
            print(f"Informational results: {len(result.get('informational_results', []))}")
        else:
            print("Error: search_product_with_specifications tool not found")

    except Exception as e:
        print(f"Error in specifications search test: {e}")

    # Test 3: Get URLs for comparison
    print("\n3. Testing URL collection for price comparison...")
    try:
        url_tool = None
        for tool in analyzer.mcp.tools:
            if tool.name == "get_product_urls_for_comparison":
                url_tool = tool
                break

        if url_tool:
            result = await url_tool.func("Sony WH-1000XM5", target_sites=["amazon.com", "bestbuy.com"])
            print(f"Success: Found URLs across {result.get('sites_with_results', 0)} sites")
            print(f"Total URLs: {result.get('total_urls_found', 0)}")
            for site, urls in result.get('urls_by_site', {}).items():
                print(f"  {site}: {len(urls)} URLs")
        else:
            print("Error: get_product_urls_for_comparison tool not found")

    except Exception as e:
        print(f"Error in URL comparison test: {e}")

    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_serper_search())
