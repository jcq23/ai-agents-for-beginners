# RealCommercial.com.au Scraper

This tool scrapes property listings from RealCommercial.com.au and uses OpenAI to extract structured data - **no paid API required!**

## How It Works

1. **Web Scraping**: Uses Python requests + BeautifulSoup to fetch HTML from RealCommercial.com.au
2. **AI Parsing**: Uses OpenAI (gpt-4o-mini) to extract structured data from the HTML
3. **Cost**: ~$0.001-0.01 per property (much cheaper than commercial real estate APIs!)

## Setup

### 1. Install Additional Dependencies

```bash
pip install beautifulsoup4 lxml
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

### 2. Ensure OpenAI API Key is Set

Your `.env` file should already have:
```
OPENAI_API_KEY=sk-your-key-here
```

## Usage

### Quick Test

Run the scraper directly:

```bash
python tools/realcommercial_scraper.py
```

This will:
- Search for Brisbane development sites (2000+ sqm, under $50M)
- Scrape the first 10 listings
- Extract structured data using AI
- Save results to `data/realcommercial_results_[timestamp].json`

### Custom Search

Use in your Python code:

```python
from tools.realcommercial_scraper import RealCommercialScraper

# Initialize
scraper = RealCommercialScraper()

# Search for properties
properties = scraper.search_brisbane_development_sites(
    suburbs=['Brisbane City', 'Fortitude Valley', 'Newstead'],
    min_land_area=2000,      # 2000+ sqm
    max_price=50000000,      # Under $50M
    min_price=10000000       # Over $10M
)

# Use the results
for prop in properties:
    print(f"{prop['address']}: ${prop['price']:,}")
    print(f"Land: {prop['land_area_sqm']} sqm")
    print(f"URL: {prop['listing_url']}")
```

## Integration with Alert System

To integrate with the existing alert system, replace the demo data in `property_listing_tool.py`:

```python
def _generate_sample_listings(self) -> List[Dict]:
    """Get real listings from RealCommercial.com.au"""
    from tools.realcommercial_scraper import RealCommercialScraper

    scraper = RealCommercialScraper()

    # Scrape real listings
    properties = scraper.search_brisbane_development_sites(
        suburbs=['Brisbane City', 'Fortitude Valley', 'South Brisbane',
                 'Newstead', 'Bowen Hills', 'West End'],
        min_land_area=2000,
        max_price=50000000
    )

    return properties
```

## Rate Limiting & Ethics

**Important:**
- The scraper includes a 2-second delay between requests (polite scraping)
- Limited to 10 listings per search by default (adjust as needed)
- Uses a browser user-agent to identify as a legitimate visitor
- Only scrapes publicly available data

**Best Practices:**
- Don't scrape too frequently (once per hour is plenty for alerts)
- Cache results to minimize requests
- Be respectful of RealCommercial's servers

## Cost Comparison

| Method | Setup Cost | Per Property | Notes |
|--------|------------|--------------|-------|
| **RealCommercial API** | Contact for pricing | Unknown | Enterprise only |
| **Domain API** | $500-2000/mo | ~$0.10-0.50 | Requires subscription |
| **CoreLogic API** | $2000+/mo | Varies | Enterprise only |
| **This Scraper** | $0 | ~$0.001-0.01 | OpenAI API cost only |

## Troubleshooting

### Website Changed Layout

If scraping stops working:
1. Check the CSS selectors in `_extract_listing_urls()`
2. Update the selectors based on current HTML structure
3. Website changes happen - this is normal for scrapers

### AI Extraction Errors

If OpenAI can't parse the data:
1. Check the prompt in `_extract_with_ai()`
2. Increase `max_tokens` if response is cut off
3. Try adding more context/examples to the prompt

### Rate Limiting

If you get blocked:
1. Increase the delay between requests (currently 2 seconds)
2. Add random delays: `time.sleep(random.uniform(2, 5))`
3. Use rotating user agents
4. Consider using a proxy service

## Legal Considerations

This scraper:
- ✅ Only accesses publicly available data
- ✅ Respects robots.txt (check before commercial use)
- ✅ Includes rate limiting to avoid overload
- ✅ Identifies with a user-agent
- ⚠️ Should not be used to republish data without permission
- ⚠️ Check RealCommercial's Terms of Service for your use case

**Disclaimer**: Web scraping is for personal research only. For commercial use, consult legal advice and consider official APIs.

## Advanced: Selenium for JavaScript Sites

If the site requires JavaScript rendering:

```bash
pip install selenium webdriver-manager
```

See commented code in the scraper for Selenium implementation.
