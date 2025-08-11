import sys
import json
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
import re
import time
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import random
from dataclasses import dataclass

@dataclass
class WebsiteConfig:
    """
    Configuration for scraping a specific website.
    """
    domain: str
    price_selectors: List[str]
    title_selectors: List[str]
    currency_symbol: str = "$"
    rate_limit: float = 1.0  # seconds between requests
    headers: Optional[Dict[str, str]] = None

class WebScrapingAnalyzer:
    """
    WebScrapingAnalyzer provides a server for scraping product prices from multiple websites.

    This class initializes a FastMCP server with tools for scraping product prices from real websites.
    It includes support for multiple website configurations, rate limiting, error handling, and
    robust price extraction.

    Methods:
        __init__(): Initializes the FastMCP server and registers scraping tools.
        _register_tools(): Registers scraping tools with the MCP server.
        _get_website_config(): Returns configuration for supported websites.
        _make_request(): Makes HTTP request with proper headers and error handling.
        _extract_price(): Extracts price from HTML using CSS selectors.
        _extract_product_title(): Extracts product title from HTML.
        run(): Starts the MCP server and handles fatal errors gracefully.
    """
    def __init__(self):
        """
        Initializes the WebScrapingAnalyzer with MCP server and website configurations.
        """
        self.mcp = FastMCP("web_scraping_analyzer")
        print("Web Scraping MCP Server initialized", file=sys.stderr)
        self.session = requests.Session()
        self._setup_session()
        self.website_configs = self._get_website_configs()
        self._register_tools()
    
    def _setup_session(self):
        """
        Configure the requests session with common headers and settings.
        """
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.session.timeout = 30

    def _get_website_configs(self) -> Dict[str, WebsiteConfig]:
        """
        Returns configuration for supported websites.
        """
        return {
            'amazon.com': WebsiteConfig(
                domain='amazon.com',
                price_selectors=['.a-price-whole', '.a-offscreen', '.a-price .a-offscreen', 'span.a-price-symbol + span'],
                title_selectors=['#productTitle', 'h1.a-size-large']
            ),
            'ebay.com': WebsiteConfig(
                domain='ebay.com', 
                price_selectors=['.u-flL.conduit', '.display-price', '.notranslate'],
                title_selectors=['h1#x-title-label-lbl', '.x-item-title-label']
            ),
            'walmart.com': WebsiteConfig(
                domain='walmart.com',
                price_selectors=['[data-automation-id="product-price"]', '.price-current', 'span[data-automation-id="product-price"]'],
                title_selectors=['h1[data-automation-id="product-title"]', 'h1.heading']
            ),
            'target.com': WebsiteConfig(
                domain='target.com',
                price_selectors=['[data-test="product-price"]', '.Price__StyledH3-sc', 'span[data-test="product-price"]'],
                title_selectors=['[data-test="product-title"]', 'h1.ProductTitle']
            )
        }
    
    def _make_request(self, url: str, config: WebsiteConfig) -> Optional[requests.Response]:
        """
        Makes HTTP request with proper headers and error handling.
        """
        try:
            # Apply rate limiting
            time.sleep(config.rate_limit + random.uniform(0, 0.5))  # Add some jitter
            
            # Use custom headers if provided
            headers = config.headers or {}
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {url}: {e}", file=sys.stderr)
            return None
    
    def _extract_price(self, soup: BeautifulSoup, config: WebsiteConfig) -> Optional[str]:
        """
        Extracts price from HTML using CSS selectors.
        """
        for selector in config.price_selectors:
            try:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    # Clean up price text
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        return f"{config.currency_symbol}{price_match.group()}"
            except Exception as e:
                print(f"Error extracting price with selector {selector}: {e}", file=sys.stderr)
                continue
        return None
    
    def _extract_product_title(self, soup: BeautifulSoup, config: WebsiteConfig) -> Optional[str]:
        """
        Extracts product title from HTML.
        """
        for selector in config.title_selectors:
            try:
                title_element = soup.select_one(selector)
                if title_element:
                    return title_element.get_text(strip=True)
            except Exception as e:
                print(f"Error extracting title with selector {selector}: {e}", file=sys.stderr)
                continue
        return None
    
    def _register_tools(self):
        """
        Registers scraping tools with the MCP server.
        """
        @self.mcp.tool()
        async def scrape_product_price(product_name: str, website_urls: list) -> dict:
            """
            Scrapes the price of a product from multiple websites using real web scraping.
            
            Args:
                product_name: Name of the product to search for
                website_urls: List of product page URLs to scrape
            
            Returns:
                Dictionary containing scraping results for each URL
            """
            print(f"Scraping {product_name} from {len(website_urls)} websites", file=sys.stderr)
            results = []

            for url in website_urls:
                try:
                    print(f"Attempting to scrape {url}", file=sys.stderr)
                    
                    # Determine website configuration
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc.lower().replace('www.', '')
                    
                    config = None
                    for supported_domain, website_config in self.website_configs.items():
                        if supported_domain in domain:
                            config = website_config
                            break
                    
                    if not config:
                        # Use generic configuration for unsupported sites
                        config = WebsiteConfig(
                            domain=domain,
                            price_selectors=['.price', '[class*="price"]', '[id*="price"]', 'span:contains("$")', 'div:contains("$")'],
                            title_selectors=['h1', 'title', '.title', '[class*="title"]']
                        )
                    
                    # Make request
                    response = self._make_request(url, config)
                    if not response:
                        results.append({
                            "product_name": product_name,
                            "website": url,
                            "error": "Failed to fetch webpage",
                            "success": False
                        })
                        continue
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract price and title
                    price = self._extract_price(soup, config)
                    title = self._extract_product_title(soup, config)
                    
                    if price:
                        results.append({
                            "product_name": product_name,
                            "extracted_title": title or "N/A",
                            "website": url,
                            "price": price,
                            "domain": domain,
                            "success": True
                        })
                        print(f"Successfully scraped {url}: {price}", file=sys.stderr)
                    else:
                        results.append({
                            "product_name": product_name,
                            "website": url,
                            "error": "Price not found on page",
                            "success": False
                        })
                        print(f"Price not found on {url}", file=sys.stderr)
                        
                except Exception as e:
                    print(f"Error scraping {url}: {e}", file=sys.stderr)
                    results.append({
                        "product_name": product_name,
                        "website": url,
                        "error": str(e),
                        "success": False
                    })

            print(f"Scraped {len([r for r in results if r['success']])} successful results out of {len(results)} total", file=sys.stderr)
            return {"results": results}
        
        @self.mcp.tool()
        async def search_product_urls(product_name: str, max_results: int = 5) -> dict:
            """
            Searches for product URLs across multiple e-commerce sites.
            Note: This is a basic implementation. For production use, consider using official APIs.
            
            Args:
                product_name: Name of the product to search for
                max_results: Maximum number of URLs to return per site
                
            Returns:
                Dictionary containing found product URLs
            """
            print(f"Searching for {product_name} URLs", file=sys.stderr)
            
            search_engines = {
                "Amazon": f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}",
                "eBay": f"https://www.ebay.com/sch/i.html?_nkw={product_name.replace(' ', '+')}",
                "Walmart": f"https://www.walmart.com/search?q={product_name.replace(' ', '+')}",
            }
            
            found_urls = {}
            
            for site_name, search_url in search_engines.items():
                try:
                    print(f"Searching on {site_name}", file=sys.stderr)
                    time.sleep(1)  # Rate limiting
                    
                    response = self.session.get(search_url)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract product links (simplified - in production you'd want more sophisticated selectors)
                    product_links = []
                    if 'amazon' in search_url:
                        links = soup.select('h2.a-size-mini a')[:max_results]
                        product_links = [urljoin('https://www.amazon.com', link.get('href')) for link in links if link.get('href')]
                    elif 'ebay' in search_url:
                        links = soup.select('a.s-item__link')[:max_results] 
                        product_links = [link.get('href') for link in links if link.get('href')]
                    elif 'walmart' in search_url:
                        links = soup.select('a[data-testid="product-title"]')[:max_results]
                        product_links = [urljoin('https://www.walmart.com', link.get('href')) for link in links if link.get('href')]
                    
                    found_urls[site_name] = product_links
                    print(f"Found {len(product_links)} URLs on {site_name}", file=sys.stderr)
                    
                except Exception as e:
                    print(f"Error searching on {site_name}: {e}", file=sys.stderr)
                    found_urls[site_name] = []
            
            total_urls = sum(len(urls) for urls in found_urls.values())
            print(f"Found {total_urls} total URLs across all sites", file=sys.stderr)
            
            return {
                "product_name": product_name,
                "found_urls": found_urls,
                "total_count": total_urls
            }

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
