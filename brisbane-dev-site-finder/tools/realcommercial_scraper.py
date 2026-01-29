"""
RealCommercial.com.au Web Scraper with AI Parsing

This tool scrapes property listings from RealCommercial.com.au and uses
OpenAI to extract structured data from the HTML content.
"""

import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import openai


class RealCommercialScraper:
    """Scraper for RealCommercial.com.au with AI-powered data extraction."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the scraper.

        Args:
            openai_api_key: OpenAI API key (or from environment)
        """
        self.base_url = "https://www.realcommercial.com.au"
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key required")

        # Set up OpenAI client
        openai.api_key = self.api_key

        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def search_brisbane_development_sites(
        self,
        suburbs: Optional[List[str]] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_land_area: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for development sites in Brisbane.

        Args:
            suburbs: List of Brisbane suburbs to search
            min_price: Minimum price in AUD
            max_price: Maximum price in AUD
            min_land_area: Minimum land area in sqm

        Returns:
            List of property listings with structured data
        """
        # Build search URL
        search_params = {
            'state': 'qld',
            'region': 'brisbane-region',
            'type': 'sale',
            'category': 'land-development'
        }

        if suburbs:
            search_params['suburbs'] = ','.join(suburbs)
        if min_price:
            search_params['price-min'] = min_price
        if max_price:
            search_params['price-max'] = max_price
        if min_land_area:
            search_params['landarea-min'] = min_land_area

        # Construct search URL
        search_url = f"{self.base_url}/for-sale"
        query_string = "&".join([f"{k}={v}" for k, v in search_params.items()])
        full_url = f"{search_url}?{query_string}"

        print(f"🔍 Searching: {full_url}")

        try:
            # Fetch the search results page
            response = requests.get(full_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract property listing URLs
            listing_urls = self._extract_listing_urls(soup)

            print(f"✅ Found {len(listing_urls)} listings")

            # Scrape details for each listing
            properties = []
            for i, url in enumerate(listing_urls[:10], 1):  # Limit to first 10 for now
                print(f"📄 Scraping listing {i}/{min(10, len(listing_urls))}...")

                property_data = self._scrape_property_details(url)
                if property_data:
                    properties.append(property_data)

                # Be polite - rate limit
                time.sleep(2)

            return properties

        except Exception as e:
            print(f"❌ Error scraping RealCommercial: {e}")
            return []

    def _extract_listing_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract property listing URLs from search results page."""
        urls = []

        # Find all property listing cards
        # Note: CSS selectors may need updating if website changes
        property_cards = soup.find_all('a', class_=lambda x: x and 'property-card' in str(x).lower())

        if not property_cards:
            # Try alternative selectors
            property_cards = soup.find_all('a', href=lambda x: x and '/property-' in str(x))

        for card in property_cards:
            href = card.get('href')
            if href:
                # Make absolute URL
                if href.startswith('/'):
                    href = self.base_url + href
                if href not in urls:
                    urls.append(href)

        return urls

    def _scrape_property_details(self, url: str) -> Optional[Dict]:
        """
        Scrape details from a property listing page using AI.

        Args:
            url: Property listing URL

        Returns:
            Structured property data
        """
        try:
            # Fetch the property page
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get the main content
            # Remove script and style tags
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text_content = soup.get_text(separator='\n', strip=True)

            # Limit to first 8000 characters to stay within token limits
            text_content = text_content[:8000]

            # Use AI to extract structured data
            property_data = self._extract_with_ai(text_content, url)

            return property_data

        except Exception as e:
            print(f"⚠️  Error scraping {url}: {e}")
            return None

    def _extract_with_ai(self, html_text: str, url: str) -> Dict:
        """
        Use OpenAI to extract structured data from scraped content.

        Args:
            html_text: Scraped text content
            url: Original URL

        Returns:
            Structured property data
        """
        prompt = f"""
Extract property information from this RealCommercial.com.au listing and return it as JSON.

Focus on extracting:
- address (full street address)
- suburb
- price (convert to number, no $ or commas)
- land_area_sqm (land area in square meters, convert hectares if needed)
- zone (zoning classification if mentioned)
- property_type (Land, Commercial, Industrial, etc.)
- description (brief description)
- existing_improvements (what's currently on the site)
- current_rental_income_pa (if mentioned, convert to number)
- frontage_m (frontage in meters if mentioned)
- agent (agent name)
- contact (phone number)

Return ONLY valid JSON, no other text. If information is not available, use null.

Property Listing Content:
{html_text}

Return JSON format:
{{
  "address": "...",
  "suburb": "...",
  "price": 0,
  "land_area_sqm": 0,
  "zone": "...",
  "property_type": "...",
  "description": "...",
  "existing_improvements": "...",
  "current_rental_income_pa": 0,
  "frontage_m": 0,
  "agent": "...",
  "contact": "..."
}}
"""

        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper and faster model
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Extract property data and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=1000
            )

            # Parse the response
            ai_response = response.choices[0].message.content.strip()

            # Try to parse JSON
            # Remove markdown code blocks if present
            if ai_response.startswith('```'):
                ai_response = ai_response.split('```')[1]
                if ai_response.startswith('json'):
                    ai_response = ai_response[4:]

            property_data = json.loads(ai_response)

            # Add metadata
            property_data['listing_url'] = url
            property_data['scraped_date'] = datetime.now().strftime("%Y-%m-%d")
            property_data['development_potential'] = True
            property_data['listing_id'] = url.split('/')[-1][:10]  # Use part of URL as ID

            return property_data

        except Exception as e:
            print(f"⚠️  AI extraction error: {e}")
            return {
                "listing_url": url,
                "error": str(e),
                "scraped_date": datetime.now().strftime("%Y-%m-%d")
            }


def main():
    """Test the scraper."""
    print("=" * 70)
    print("RealCommercial.com.au Development Site Scraper")
    print("=" * 70)
    print()

    try:
        scraper = RealCommercialScraper()

        # Search for large development sites in Brisbane
        properties = scraper.search_brisbane_development_sites(
            suburbs=['Brisbane City', 'Fortitude Valley', 'South Brisbane'],
            min_land_area=2000,
            max_price=50000000
        )

        # Display results
        print(f"\n✅ Successfully scraped {len(properties)} properties\n")

        for i, prop in enumerate(properties, 1):
            print(f"{i}. {prop.get('address', 'Unknown address')}")
            print(f"   Price: ${prop.get('price', 0):,}")
            print(f"   Land Area: {prop.get('land_area_sqm', 0)} sqm")
            print(f"   URL: {prop.get('listing_url', 'N/A')}")
            print()

        # Save to file
        output_file = f"data/realcommercial_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("data", exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(properties, f, indent=2)

        print(f"💾 Results saved to: {output_file}")

    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")


if __name__ == "__main__":
    main()
