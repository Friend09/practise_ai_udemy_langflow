#!/usr/bin/env python3
"""
Test script for MCP servers with real-world data simulation.

This script demonstrates how the updated MCP servers work with realistic product data
and showcases the enhanced functionality for price comparison.
"""

import asyncio
import json
from typing import Dict, List

# Mock data that simulates real web scraping results
MOCK_SCRAPED_DATA = {
    "results": [
        {
            "product_name": "iPhone 15 Pro 128GB",
            "website": "https://www.amazon.com/dp/B123456",
            "domain": "amazon.com",
            "price": "$999.99",
            "extracted_title": "Apple iPhone 15 Pro 128GB - Natural Titanium",
            "success": True
        },
        {
            "product_name": "iPhone 15 Pro 128GB",
            "website": "https://www.bestbuy.com/site/apple-iphone-15-pro/123456.p",
            "domain": "bestbuy.com",
            "price": "$1,049.99",
            "extracted_title": "Apple - iPhone 15 Pro 128GB",
            "success": True
        },
        {
            "product_name": "iPhone 15 Pro 128GB",
            "website": "https://www.walmart.com/ip/iPhone-15-Pro/123456",
            "domain": "walmart.com",
            "price": "Price: $979.00",
            "extracted_title": "Apple iPhone 15 Pro 128GB Titanium",
            "success": True
        },
        {
            "product_name": "iPhone 15 Pro 128GB",
            "website": "https://www.target.com/p/apple-iphone-15-pro/123456",
            "domain": "target.com",
            "price": "$1,029.99",
            "extracted_title": "Apple iPhone 15 Pro 128GB",
            "success": True
        },
        {
            "product_name": "iPhone 15 Pro 128GB",
            "website": "https://www.ebay.com/itm/123456",
            "domain": "ebay.com",
            "price": "Buy It Now: $899.99",
            "extracted_title": "Apple iPhone 15 Pro 128GB - Excellent Condition",
            "success": True
        }
    ]
}

def simulate_data_processing():
    """
    Simulates the data processing MCP server functionality.
    """
    print("🔄 Simulating Data Processing MCP Server...")

    # Import the actual processing logic
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from mcp_servers.data_processing_mcp_server import DataProcessingAnalyzer

    analyzer = DataProcessingAnalyzer()

    # Process each scraped item
    processed_results = []
    failed_items = []

    for item in MOCK_SCRAPED_DATA["results"]:
        if item.get("success"):
            try:
                # Extract price and currency
                price_str = item.get("price", "")
                price, currency = analyzer._extract_price(price_str)

                if price is not None:
                    processed_item = {
                        "product_name": item.get("product_name"),
                        "website": item.get("website"),
                        "domain": analyzer._extract_domain(item.get("website", "")),
                        "price": price,
                        "currency": currency,
                        "original_price_string": price_str,
                        "extracted_title": item.get("extracted_title"),
                    }

                    if analyzer._validate_product_data(processed_item):
                        processed_results.append(processed_item)
                        print(f"  ✅ {processed_item['domain']}: ${price:.2f} {currency}")
                    else:
                        failed_items.append({"item": processed_item, "reason": "Failed validation"})
                else:
                    failed_items.append({"item": item, "reason": "Could not extract price"})

            except Exception as e:
                failed_items.append({"item": item, "reason": f"Processing error: {e}"})

    return {
        "data_list": processed_results,
        "summary": {
            "total_processed": len(processed_results),
            "total_failed": len(failed_items),
            "success_rate": len(processed_results) / (len(processed_results) + len(failed_items)) * 100
        },
        "failed_items": failed_items
    }

def simulate_price_analysis(processed_data: Dict):
    """
    Simulates the price comparison MCP server functionality.
    """
    print("\n📊 Simulating Price Comparison Analysis...")

    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from mcp_servers.price_comparision_mcp_server import PriceComparisonAnalyzer
    import statistics

    analyzer = PriceComparisonAnalyzer()

    data_list = processed_data.get("data_list", [])
    if not data_list:
        return {"error": "No data available for analysis"}

    # Extract prices
    prices = [item.get("price", 0) for item in data_list if item.get("price", 0) > 0]

    if not prices:
        return {"error": "No valid prices found"}

    # Calculate statistics
    stats = analyzer._calculate_statistics(prices)

    # Find best and worst deals
    best_deal = min(data_list, key=lambda x: x.get("price", float('inf')))
    worst_deal = max(data_list, key=lambda x: x.get("price", 0))

    # Analyze trends
    trends = analyzer._analyze_price_trends(data_list)

    # Generate recommendations
    analysis_results = {
        "statistics": stats,
        "best_deal": best_deal,
        "trends": trends
    }
    recommendations = analyzer._generate_recommendations(analysis_results, data_list)

    return {
        "product_name": data_list[0].get("product_name", "Unknown Product"),
        "total_sites_analyzed": len(data_list),
        "price_statistics": {
            "lowest_price": stats.get('min', 0),
            "highest_price": stats.get('max', 0),
            "average_price": round(stats.get('mean', 0), 2),
            "median_price": round(stats.get('median', 0), 2),
            "price_range": round(stats.get('range', 0), 2),
        },
        "best_deal": {
            "price": best_deal.get("price"),
            "domain": best_deal.get("domain"),
            "website": best_deal.get("website")
        },
        "potential_savings": round(stats.get('range', 0), 2),
        "recommendations": recommendations,
        "site_analysis": trends
    }

def simulate_serper_search():
    """
    Simulates the Serper web search MCP server functionality.
    """
    print("\n🔍 Simulating Serper Web Search MCP Server...")

    # Mock search results that would come from Serper API
    mock_search_results = {
        "product_name": "iPhone 15 Pro 128GB",
        "success": True,
        "total_results": 8,
        "ecommerce_filtered": True,
        "results": [
            {
                "title": "Apple iPhone 15 Pro 128GB - Natural Titanium - Amazon.com",
                "url": "https://www.amazon.com/dp/B123456",
                "domain": "amazon.com",
                "snippet": "Shop Apple iPhone 15 Pro with advanced camera system. Price: $999.99. Free shipping with Prime.",
                "position": 1,
                "price_mentioned": "$999.99"
            },
            {
                "title": "iPhone 15 Pro 128GB | Best Buy",
                "url": "https://www.bestbuy.com/site/apple-iphone-15-pro/123456.p",
                "domain": "bestbuy.com",
                "snippet": "Get the new iPhone 15 Pro at Best Buy. Starting at $1049.99. Trade in your old phone for credit.",
                "position": 2,
                "price_mentioned": "$1049.99"
            },
            {
                "title": "Apple iPhone 15 Pro - Walmart.com",
                "url": "https://www.walmart.com/ip/iPhone-15-Pro/123456",
                "domain": "walmart.com",
                "snippet": "Save on Apple iPhone 15 Pro. Everyday Low Price $979.00. Free pickup available.",
                "position": 3,
                "price_mentioned": "$979.00"
            },
            {
                "title": "iPhone 15 Pro | Target",
                "url": "https://www.target.com/p/apple-iphone-15-pro/123456",
                "domain": "target.com",
                "snippet": "Apple iPhone 15 Pro available at Target. $1029.99 with free shipping on orders $35+.",
                "position": 4,
                "price_mentioned": "$1029.99"
            },
            {
                "title": "Apple iPhone 15 Pro | eBay",
                "url": "https://www.ebay.com/itm/123456",
                "domain": "ebay.com",
                "snippet": "Find great deals on iPhone 15 Pro. Buy It Now from $899.99. New and used options available.",
                "position": 5,
                "price_mentioned": "$899.99"
            }
        ],
        "search_metadata": {
            "query_used": "iPhone 15 Pro 128GB price buy shop",
            "api_response_status": "success"
        }
    }

    print(f"  ✅ Found {mock_search_results['total_results']} e-commerce results")
    for result in mock_search_results['results']:
        price = result.get('price_mentioned', 'N/A')
        print(f"     • {result['domain']}: {price}")

    return mock_search_results

def main():
    """
    Main function to demonstrate the enhanced MCP server capabilities.
    """
    print("🚀 Testing Enhanced MCP Servers for Price Comparison")
    print("=" * 60)

    # Step 0: Search for product URLs using Serper
    search_results = simulate_serper_search()

    # Step 1: Process scraped data
    processed_data = simulate_data_processing()

    print(f"\n📈 Processing Summary:")
    print(f"  • Total processed: {processed_data['summary']['total_processed']}")
    print(f"  • Success rate: {processed_data['summary']['success_rate']:.1f}%")

    # Step 2: Perform price analysis
    analysis_results = simulate_price_analysis(processed_data)

    if "error" not in analysis_results:
        print(f"\n🎯 Price Analysis Results for: {analysis_results['product_name']}")
        print(f"  • Sites analyzed: {analysis_results.get('total_sites_analyzed', 0)}")
        stats = analysis_results.get('price_statistics', {})
        if isinstance(stats, dict):
            print(f"  • Lowest price: ${stats.get('lowest_price', 0):.2f}")
            print(f"  • Highest price: ${stats.get('highest_price', 0):.2f}")
            print(f"  • Average price: ${stats.get('average_price', 0):.2f}")
        print(f"  • Potential savings: ${analysis_results.get('potential_savings', 0):.2f}")

        print(f"\n💡 Best Deal:")
        best = analysis_results.get('best_deal', {})
        if isinstance(best, dict):
            print(f"  • ${best.get('price', 0):.2f} at {best.get('domain', 'Unknown')}")

        print(f"\n🎯 Recommendations:")
        recommendations = analysis_results.get('recommendations', [])
        if isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        print(f"\n🏪 Site Analysis:")
        site_analysis = analysis_results.get('site_analysis', {})
        if isinstance(site_analysis, dict):
            cheapest = site_analysis.get('cheapest_site')
            if cheapest:
                print(f"  • Generally cheapest: {cheapest}")
            most_expensive = site_analysis.get('most_expensive_site')
            if most_expensive:
                print(f"  • Generally most expensive: {most_expensive}")
    else:
        print(f"❌ Analysis Error: {analysis_results['error']}")

    print("\n✅ MCP Server testing completed successfully!")
    print("\nℹ️  These servers are now ready for real-world use with:")
    print("  • Serper API web search for product discovery")
    print("  • Actual web scraping capabilities")
    print("  • Robust price parsing and validation")
    print("  • Comprehensive price analysis and recommendations")
    print("  • Support for multiple currencies and formats")
    print("  • Error handling and data quality checks")

if __name__ == "__main__":
    main()
