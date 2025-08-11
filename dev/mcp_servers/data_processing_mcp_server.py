import sys
import json
import re
from mcp.server.fastmcp import FastMCP
from typing import Optional
from dataclasses import dataclass
import unicodedata

@dataclass
class ProcessedProduct:
    """
    Represents a processed product with standardized data.
    """
    product_name: str
    website: str
    domain: str
    price: float
    currency: str
    original_price_string: str
    extracted_title: Optional[str] = None
    availability: Optional[str] = None
    shipping_info: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None

class DataProcessingAnalyzer:
    """
    DataProcessingAnalyzer sets up an MCP server to process scraped product data.
    
    This class provides sophisticated data processing capabilities including:
    - Robust price parsing from various formats
    - Currency detection and normalization
    - Data validation and quality checks
    - Product information standardization
    - Error handling and reporting
    
    It registers tools for data processing and runs the server using stdio transport.
    """

    def __init__(self):
        """
        Initializes the DataProcessingAnalyzer, sets up the MCP server,
        and registers the data processing tools.
        """
        self.mcp = FastMCP("data_processing_analyzer")
        print("Data Processing MCP Server initialized", file=sys.stderr)
        self.currency_symbols = {
            '$': 'USD',
            '€': 'EUR', 
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR',
            'C$': 'CAD',
            'A$': 'AUD',
            'CHF': 'CHF',
            'kr': 'SEK'
        }
        self._register_tools()

    def _extract_price(self, price_str: str) -> tuple[Optional[float], Optional[str]]:
        """
        Extracts price and currency from price string with robust parsing.
        
        Args:
            price_str: Raw price string from website
            
        Returns:
            Tuple of (price_float, currency_code)
        """
        if not price_str:
            return None, None
            
        # Normalize unicode characters
        price_str = unicodedata.normalize('NFKD', price_str)
        
        # Detect currency
        currency = 'USD'  # Default
        for symbol, code in self.currency_symbols.items():
            if symbol in price_str:
                currency = code
                break
        
        # Clean price string for number extraction
        # Remove currency symbols and common words
        cleaned = re.sub(r'[^\d.,\s]', ' ', price_str)
        cleaned = re.sub(r'\b(price|cost|each|per|from|starting|at)\b', ' ', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        # Try different number formats
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*\.\d{2})',  # 1,234.56 format
            r'(\d+\.\d{2})',                 # 123.45 format  
            r'(\d+,\d{2})',                  # 123,45 European format
            r'(\d{1,3}(?:,\d{3})+)',         # 1,234 format (no decimals)
            r'(\d+)'                         # Integer format
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, cleaned)
            if matches:
                try:
                    # Take the first (usually highest/main) price found
                    price_match = matches[0]
                    
                    # Handle different decimal separators
                    if ',' in price_match and '.' not in price_match:
                        # European format (123,45)
                        price_float = float(price_match.replace(',', '.'))
                    else:
                        # US format (123.45 or 1,234.56)
                        price_float = float(price_match.replace(',', ''))
                    
                    return price_float, currency
                except ValueError:
                    continue
        
        return None, None
    
    def _validate_product_data(self, data: dict) -> bool:
        """
        Validates that product data meets minimum quality standards.
        
        Args:
            data: Product data dictionary
            
        Returns:
            True if data is valid, False otherwise
        """
        required_fields = ['product_name', 'website', 'price']
        
        # Check required fields exist
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validate price is reasonable
        price = data.get('price', 0)
        if not isinstance(price, (int, float)) or price <= 0 or price > 1000000:
            return False
        
        # Validate URL format
        website = data.get('website', '')
        if not website.startswith(('http://', 'https://')):
            return False
            
        return True
    
    def _extract_domain(self, url: str) -> str:
        """
        Extracts domain name from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace('www.', '')
        except Exception:
            return 'unknown'
    
    def _register_tools(self):
        """
        Registers the data processing tools with the MCP server.
        """

        @self.mcp.tool()
        async def process_scraped_data(raw_data: dict) -> dict:
            """
            Processes raw scraped product data into a standardized format.

            Args:
                raw_data (dict): Dictionary containing scraped product data from web scraping.

            Returns:
                dict: Dictionary with processed, validated, and standardized product data.
            """
            print("Processing scraped data", file=sys.stderr)
            processed_results = []
            failed_items = []

            # Iterate over each item in the scraped results
            for item in raw_data.get("results", []):
                if item.get("success"):
                    try:
                        # Extract price and currency
                        price_str = item.get("price", "")
                        price, currency = self._extract_price(price_str)
                        
                        if price is None:
                            failed_items.append({
                                "item": item,
                                "reason": "Could not extract valid price",
                                "price_string": price_str
                            })
                            continue
                        
                        # Create processed item
                        processed_item = {
                            "product_name": item.get("product_name", item.get("product", "Unknown Product")),
                            "website": item.get("website", ""),
                            "domain": self._extract_domain(item.get("website", "")),
                            "price": price,
                            "currency": currency,
                            "original_price_string": price_str,
                            "extracted_title": item.get("extracted_title"),
                        }
                        
                        # Validate the processed data
                        if self._validate_product_data(processed_item):
                            processed_results.append(processed_item)
                            print(f"Processed: {processed_item['domain']} - {currency}{price}", file=sys.stderr)
                        else:
                            failed_items.append({
                                "item": processed_item,
                                "reason": "Failed validation checks"
                            })
                            
                    except Exception as e:
                        print(f"Error processing item: {e}", file=sys.stderr)
                        failed_items.append({
                            "item": item,
                            "reason": f"Processing error: {str(e)}"
                        })
                else:
                    failed_items.append({
                        "item": item,
                        "reason": "Original scraping failed"
                    })

            print(f"Processed {len(processed_results)} valid results, {len(failed_items)} failed", file=sys.stderr)
            
            return {
                "data_list": processed_results,
                "summary": {
                    "total_processed": len(processed_results),
                    "total_failed": len(failed_items),
                    "success_rate": len(processed_results) / (len(processed_results) + len(failed_items)) * 100 if processed_results or failed_items else 0
                },
                "failed_items": failed_items
            }
        
        @self.mcp.tool()
        async def validate_product_data(product_data: dict) -> dict:
            """
            Validates individual product data for quality and completeness.
            
            Args:
                product_data: Single product data dictionary
                
            Returns:
                Validation results with issues found
            """
            print("Validating product data", file=sys.stderr)
            
            issues = []
            warnings = []
            
            # Check required fields
            required_fields = ['product_name', 'website', 'price']
            for field in required_fields:
                if field not in product_data or not product_data[field]:
                    issues.append(f"Missing required field: {field}")
            
            # Validate price
            price = product_data.get('price')
            if price is not None:
                if not isinstance(price, (int, float)):
                    issues.append("Price must be a number")
                elif price <= 0:
                    issues.append("Price must be positive")
                elif price > 100000:
                    warnings.append("Price seems unusually high")
            
            # Check URL format
            website = product_data.get('website', '')
            if website and not website.startswith(('http://', 'https://')):
                issues.append("Website must be a valid URL")
            
            # Check currency format
            currency = product_data.get('currency', '')
            if currency and currency not in self.currency_symbols.values():
                warnings.append(f"Unrecognized currency: {currency}")
            
            is_valid = len(issues) == 0
            
            return {
                "is_valid": is_valid,
                "issues": issues,
                "warnings": warnings,
                "data": product_data
            }
        
        @self.mcp.tool()
        async def normalize_currencies(product_list: list, target_currency: str = "USD") -> dict:
            """
            Normalizes all prices to a target currency (mock implementation).
            
            Args:
                product_list: List of products with price data
                target_currency: Target currency code (default: USD)
                
            Returns:
                Products with normalized prices
            """
            print(f"Normalizing currencies to {target_currency}", file=sys.stderr)
            
            # Mock exchange rates (in production, you'd use a real API)
            exchange_rates = {
                'USD': 1.0,
                'EUR': 1.08,
                'GBP': 1.26,
                'JPY': 0.0067,
                'CAD': 0.74,
                'AUD': 0.65
            }
            
            normalized_products = []
            
            for product in product_list:
                try:
                    original_currency = product.get('currency', 'USD')
                    original_price = product.get('price', 0)
                    
                    if original_currency == target_currency:
                        normalized_price = original_price
                    else:
                        # Convert to USD first, then to target currency
                        usd_price = original_price / exchange_rates.get(original_currency, 1.0)
                        normalized_price = usd_price * exchange_rates.get(target_currency, 1.0)
                    
                    normalized_product = product.copy()
                    normalized_product.update({
                        'normalized_price': round(normalized_price, 2),
                        'original_price': original_price,
                        'original_currency': original_currency,
                        'target_currency': target_currency
                    })
                    
                    normalized_products.append(normalized_product)
                    
                except Exception as e:
                    print(f"Error normalizing currency for {product}: {e}", file=sys.stderr)
                    continue
            
            return {
                "normalized_products": normalized_products,
                "target_currency": target_currency,
                "exchange_rates_used": exchange_rates
            }

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
