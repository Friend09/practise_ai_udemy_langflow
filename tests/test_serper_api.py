#!/usr/bin/env python3
"""
Simple test to verify the Serper API connection works.
"""

import requests
import json
import os

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"Error loading .env file: {e}")

def test_serper_api():
    """Test the basic Serper API functionality."""

    print("Testing Serper API connection...")

    # Get API key from environment
    api_key = os.getenv('SERPER_APIKEY') or os.getenv('SERPER_API_KEY')
    if not api_key:
        print("❌ ERROR: SERPER_APIKEY or SERPER_API_KEY environment variable not found!")
        print("Please set your Serper API key in the .env file or environment")
        return False

    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": "iPhone 15 Pro price buy",
        "num": 5
    })

    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        print(f"Making request to Serper API...")
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()

        data = response.json()

        print("✅ API connection successful!")
        print(f"Found {len(data.get('organic', []))} organic results")

        # Show first few results
        for i, result in enumerate(data.get('organic', [])[:3], 1):
            title = result.get('title', 'No title')
            link = result.get('link', 'No link')
            snippet = result.get('snippet', 'No snippet')
            print(f"\n{i}. {title}")
            print(f"   URL: {link}")
            print(f"   Snippet: {snippet[:100]}...")

        return True

    except requests.exceptions.Timeout:
        print("❌ Request timed out - check your internet connection")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse response: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_serper_api()
