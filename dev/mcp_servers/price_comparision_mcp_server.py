# mcp server - price comparison
import sys
import json
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class PriceAnalysis:
    """
    Represents the results of price comparison analysis.
    """
    lowest_price: float
    highest_price: float
    average_price: float
    median_price: float
    price_range: float
    total_savings: float
    best_deal: Dict[str, Any]
    all_prices: List[Dict[str, Any]]
    analysis_timestamp: str
    product_name: str
    total_sites_analyzed: int

class PriceComparisonAnalyzer:
    def __init__(self):
        """
        Initializes the PriceComparisonAnalyzer with comprehensive analysis capabilities.
        """
        self.mcp = FastMCP("price_comparison_analyzer")
        print("Price Comparison MCP Server initialized", file=sys.stderr)
        self._register_tools()

    def _calculate_statistics(self, prices: List[float]) -> Dict[str, float]:
        """
        Calculates statistical measures for price data.
        
        Args:
            prices: List of price values
            
        Returns:
            Dictionary containing statistical measures
        """
        if not prices:
            return {}
            
        return {
            'min': min(prices),
            'max': max(prices),
            'mean': statistics.mean(prices),
            'median': statistics.median(prices),
            'range': max(prices) - min(prices),
            'std_dev': statistics.stdev(prices) if len(prices) > 1 else 0.0
        }
    
    def _analyze_price_trends(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes price trends and patterns.
        
        Args:
            price_data: List of price data dictionaries
            
        Returns:
            Analysis results including trends and insights
        """
        if not price_data:
            return {}
        
        # Group by domain for analysis
        domain_prices = {}
        for item in price_data:
            domain = item.get('domain', 'unknown')
            price = item.get('price', 0)
            if domain not in domain_prices:
                domain_prices[domain] = []
            domain_prices[domain].append(price)
        
        # Calculate average price per domain
        domain_averages = {
            domain: statistics.mean(prices) 
            for domain, prices in domain_prices.items()
        }
        
        return {
            'domain_price_averages': domain_averages,
            'most_expensive_site': max(domain_averages, key=domain_averages.get) if domain_averages else None,
            'cheapest_site': min(domain_averages, key=domain_averages.get) if domain_averages else None,
            'price_variation_by_site': domain_prices
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any], price_data: List[Dict[str, Any]]) -> List[str]:
        """
        Generates purchasing recommendations based on price analysis.
        
        Args:
            analysis: Price analysis results
            price_data: Original price data
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not price_data:
            return recommendations
            
        stats = analysis.get('statistics', {})
        best_deal = analysis.get('best_deal', {})
        
        # Basic recommendation
        if best_deal:
            domain = best_deal.get('domain', 'Unknown site')
            price = best_deal.get('price', 0)
            recommendations.append(f"Best deal: ${price:.2f} at {domain}")
        
        # Savings recommendation
        if stats.get('range', 0) > 0:
            savings = stats.get('range', 0)
            recommendations.append(f"You could save ${savings:.2f} by choosing the cheapest option")
        
        # Price spread analysis
        mean_price = stats.get('mean', 0)
        std_dev = stats.get('std_dev', 0)
        
        if std_dev / mean_price > 0.2 if mean_price > 0 else False:  # High price variation
            recommendations.append("Prices vary significantly across sites - comparison shopping recommended")
        
        # Site-specific recommendations
        trends = analysis.get('trends', {})
        cheapest_site = trends.get('cheapest_site')
        if cheapest_site:
            recommendations.append(f"{cheapest_site} tends to have lower prices for this type of product")
        
        return recommendations
    
    def _register_tools(self):
        """
        Registers comprehensive price analysis tools with the MCP server.
        """
        @self.mcp.tool()
        async def find_lowest_price(processed_data: dict) -> dict:
            """
            Find the lowest price for a given product with basic analysis.
            
            Args:
                processed_data: Dictionary containing processed product data
                
            Returns:
                Dictionary with lowest price information and basic comparison
            """
            print("Finding the lowest price", file=sys.stderr)

            data_list = processed_data.get("data_list", [])
            if not data_list:
                return {
                    "lowest_price": "N/A",
                    "source": "N/A",
                    "message": "No valid data found",
                    "all_prices": []
                }

            lowest_item = None
            all_prices = []

            for item in data_list:
                price = item.get("price", 0)
                all_prices.append({
                    "website": item.get("website"),
                    "domain": item.get("domain"),
                    "price": price,
                    "original_price_string": item.get("original_price_string"),
                    "currency": item.get("currency", "USD")
                })

                if lowest_item is None or price < lowest_item["price"]:
                    lowest_item = item

            if lowest_item:
                result = {
                    "lowest_price": lowest_item["price"],
                    "source": lowest_item.get("domain", "Unknown"),
                    "website_url": lowest_item.get("website", ""),
                    "product_name": lowest_item.get("product_name"),
                    "currency": lowest_item.get("currency", "USD"),
                    "message": "Lowest price found",
                    "all_prices": all_prices,
                    "total_options": len(all_prices)
                }
                print(f"Lowest price found: ${result['lowest_price']:.2f} at {result['source']}", file=sys.stderr)
                return result
            else:
                return {
                    "lowest_price": "N/A",
                    "source": "N/A",
                    "message": "Could not determine lowest price",
                    "all_prices": all_prices
                }
        
        @self.mcp.tool()
        async def comprehensive_price_analysis(processed_data: dict) -> dict:
            """
            Performs comprehensive price analysis including statistics, trends, and recommendations.
            
            Args:
                processed_data: Dictionary containing processed product data
                
            Returns:
                Comprehensive analysis results with statistics and recommendations
            """
            print("Performing comprehensive price analysis", file=sys.stderr)
            
            data_list = processed_data.get("data_list", [])
            if not data_list:
                return {
                    "error": "No valid data found for analysis",
                    "data_available": False
                }
            
            # Extract prices and prepare data
            prices = [item.get("price", 0) for item in data_list if item.get("price", 0) > 0]
            
            if not prices:
                return {
                    "error": "No valid prices found in data",
                    "data_available": False
                }
            
            # Calculate statistics
            stats = self._calculate_statistics(prices)
            
            # Find best deal
            best_deal = min(data_list, key=lambda x: x.get("price", float('inf')))
            worst_deal = max(data_list, key=lambda x: x.get("price", 0))
            
            # Analyze trends
            trends = self._analyze_price_trends(data_list)
            
            # Prepare analysis results
            analysis_results = {
                "statistics": stats,
                "best_deal": {
                    "price": best_deal.get("price"),
                    "domain": best_deal.get("domain"),
                    "website": best_deal.get("website"),
                    "currency": best_deal.get("currency", "USD")
                },
                "worst_deal": {
                    "price": worst_deal.get("price"),
                    "domain": worst_deal.get("domain"),
                    "website": worst_deal.get("website")
                },
                "trends": trends
            }
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis_results, data_list)
            
            # Prepare all price data for reference
            all_prices = [{
                "domain": item.get("domain"),
                "website": item.get("website"),
                "price": item.get("price"),
                "currency": item.get("currency", "USD"),
                "original_price_string": item.get("original_price_string")
            } for item in data_list]
            
            final_analysis = {
                "product_name": data_list[0].get("product_name", "Unknown Product"),
                "analysis_timestamp": datetime.now().isoformat(),
                "total_sites_analyzed": len(data_list),
                "valid_prices_found": len(prices),
                "price_statistics": {
                    "lowest_price": stats.get('min', 0),
                    "highest_price": stats.get('max', 0),
                    "average_price": round(stats.get('mean', 0), 2),
                    "median_price": round(stats.get('median', 0), 2),
                    "price_range": round(stats.get('range', 0), 2),
                    "standard_deviation": round(stats.get('std_dev', 0), 2)
                },
                "best_deal": analysis_results["best_deal"],
                "potential_savings": round(stats.get('range', 0), 2),
                "recommendations": recommendations,
                "site_analysis": trends,
                "all_prices": all_prices,
                "data_available": True
            }
            
            print(f"Analysis complete: {len(prices)} prices analyzed, best deal: ${stats.get('min', 0):.2f}", file=sys.stderr)
            return final_analysis
        
        @self.mcp.tool()
        async def compare_specific_sites(processed_data: dict, site_domains: list) -> dict:
            """
            Compares prices between specific websites/domains.
            
            Args:
                processed_data: Dictionary containing processed product data
                site_domains: List of domain names to compare
                
            Returns:
                Comparison results for specified sites
            """
            print(f"Comparing prices across specified sites: {site_domains}", file=sys.stderr)
            
            data_list = processed_data.get("data_list", [])
            if not data_list:
                return {
                    "error": "No data available for comparison",
                    "requested_sites": site_domains
                }
            
            # Filter data for requested sites
            site_data = {}
            for domain in site_domains:
                matching_items = [
                    item for item in data_list 
                    if domain.lower() in item.get("domain", "").lower()
                ]
                if matching_items:
                    # Take the best price if multiple entries for same site
                    best_item = min(matching_items, key=lambda x: x.get("price", float('inf')))
                    site_data[domain] = best_item
                else:
                    site_data[domain] = None
            
            # Generate comparison
            comparison_results = {
                "requested_comparison": site_domains,
                "site_prices": {},
                "best_among_requested": None,
                "price_differences": {},
                "sites_found": 0,
                "sites_missing": []
            }
            
            valid_sites = {}
            for domain, data in site_data.items():
                if data:
                    comparison_results["site_prices"][domain] = {
                        "price": data.get("price"),
                        "currency": data.get("currency", "USD"),
                        "website": data.get("website"),
                        "original_price_string": data.get("original_price_string")
                    }
                    valid_sites[domain] = data.get("price", 0)
                    comparison_results["sites_found"] += 1
                else:
                    comparison_results["sites_missing"].append(domain)
            
            if valid_sites:
                best_site = min(valid_sites, key=valid_sites.get)
                comparison_results["best_among_requested"] = {
                    "domain": best_site,
                    "price": valid_sites[best_site],
                    "currency": site_data[best_site].get("currency", "USD")
                }
                
                # Calculate price differences from cheapest
                cheapest_price = valid_sites[best_site]
                for domain, price in valid_sites.items():
                    comparison_results["price_differences"][domain] = {
                        "difference": round(price - cheapest_price, 2),
                        "percentage_more": round((price - cheapest_price) / cheapest_price * 100, 1) if cheapest_price > 0 else 0
                    }
            
            print(f"Site comparison complete: {comparison_results['sites_found']} of {len(site_domains)} sites found", file=sys.stderr)
            return comparison_results

    def run(self):
        """
        Runs the MCP server using stdio transport with error handling.
        """
        try:
            print("Starting Price Comparison MCP Server...", file=sys.stderr)
            self.mcp.run(transport="stdio")
        except Exception as e:
            print(f"Error starting Price Comparison MCP Server: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    server = PriceComparisonAnalyzer()
    server.run()
