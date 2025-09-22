#!/usr/bin/env python3
"""
Comprehensive Infiniti Dealer Scraper

This script navigates to the Infiniti retailer locator website and searches for dealers
using various zip codes across the US to capture all available dealers. It captures
GraphQL responses and consolidates the data into a comprehensive JSON file.

Features:
- Searches multiple zip codes covering major US regions
- Captures GraphQL API responses from network requests
- Deduplicates dealer data
- Saves comprehensive results to JSON
- Handles errors gracefully with retries
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Set
import logging

from playwright.async_api import async_playwright, Page, Browser
import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('infiniti_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Comprehensive list of zip codes covering major US regions with 250-mile radius
ZIP_CODES = [
    # West Coast
    "90210",  # Beverly Hills, CA
    "94102",  # San Francisco, CA
    "98101",  # Seattle, WA
    "97201",  # Portland, OR
    "92101",  # San Diego, CA
    "95814",  # Sacramento, CA
    "85001",  # Phoenix, AZ
    "89101",  # Las Vegas, NV
    "84101",  # Salt Lake City, UT
    "80201",  # Denver, CO
    
    # Southwest
    "75201",  # Dallas, TX
    "77001",  # Houston, TX
    "78201",  # San Antonio, TX
    "73301",  # Austin, TX
    "85001",  # Phoenix, AZ (already included)
    
    # Midwest
    "60601",  # Chicago, IL
    "55401",  # Minneapolis, MN
    "53201",  # Milwaukee, WI
    "44101",  # Cleveland, OH
    "45201",  # Cincinnati, OH
    "43201",  # Columbus, OH
    "48201",  # Detroit, MI
    "46201",  # Indianapolis, IN
    "63101",  # St. Louis, MO
    "64101",  # Kansas City, MO
    
    # Northeast
    "10001",  # New York, NY
    "19101",  # Philadelphia, PA
    "02101",  # Boston, MA
    "21201",  # Baltimore, MD
    "20001",  # Washington, DC
    "30301",  # Atlanta, GA (technically Southeast but covers Northeast overlap)
    
    # Southeast
    "30301",  # Atlanta, GA
    "33101",  # Miami, FL
    "32801",  # Orlando, FL
    "33601",  # Tampa, FL
    "28201",  # Charlotte, NC
    "27601",  # Raleigh, NC
    "29401",  # Charleston, SC
    "37201",  # Nashville, TN
    "38101",  # Memphis, TN
    "70112",  # New Orleans, LA
    "72201",  # Little Rock, AR
    
    # Additional coverage for gaps
    "87101",  # Albuquerque, NM
    "73101",  # Oklahoma City, OK
    "68101",  # Omaha, NE
    "57101",  # Sioux Falls, SD
    "58501",  # Bismarck, ND
    "59101",  # Billings, MT
    "83701",  # Boise, ID
    "99701",  # Fairbanks, AK
    "96801",  # Honolulu, HI
]

class InfinitiDealerScraper:
    def __init__(self):
        self.all_dealers: Dict[str, dict] = {}
        self.network_requests: List[dict] = []
        self.session = None
        
    async def setup_browser(self) -> tuple[Browser, Page]:
        """Initialize browser and page with network monitoring"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Set up network request interception
        async def handle_request(request):
            if "graphql.nissanusa.com" in request.url:
                logger.info(f"Intercepted GraphQL request: {request.url}")
        
        async def handle_response(response):
            if "graphql.nissanusa.com" in response.url:
                try:
                    response_data = await response.json()
                    self.network_requests.append({
                        "url": response.url,
                        "status": response.status,
                        "data": response_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    logger.info(f"Captured GraphQL response with {len(response_data.get('data', {}).get('getDealersByLatLng', []))} dealers")
                except Exception as e:
                    logger.error(f"Error parsing GraphQL response: {e}")
        
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        return browser, page
    
    async def search_dealers(self, page: Page, zip_code: str) -> bool:
        """Search for dealers using a specific zip code"""
        try:
            logger.info(f"Searching for dealers near zip code: {zip_code}")
            
            # Navigate to the dealer locator page
            await page.goto("https://www.infinitiusa.com/locate-infiniti-retailer.html", 
                           wait_until="networkidle")
            await page.wait_for_timeout(2000)  # Wait for page to fully load
            
            # Clear any existing text and enter the zip code
            search_box = page.get_by_role('textbox', name='Enter a Location')
            await search_box.clear()
            await search_box.fill(zip_code)
            
            # Click the search button
            search_button = page.get_by_role('button', name='Search')
            await search_button.click()
            
            # Wait for results to load
            await page.wait_for_timeout(3000)
            
            # Check if results are displayed
            try:
                results_text = await page.locator("text=Results").first.text_content()
                if "Results" in results_text:
                    logger.info(f"Found results for zip {zip_code}: {results_text}")
                    return True
                else:
                    logger.warning(f"No results found for zip {zip_code}")
                    return False
            except Exception as e:
                logger.warning(f"Could not determine results for zip {zip_code}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error searching dealers for zip {zip_code}: {e}")
            return False
    
    async def extract_dealer_data_from_page(self, page: Page) -> List[dict]:
        """Extract dealer data from the current page"""
        dealers = []
        try:
            # Look for dealer cards in the results
            dealer_cards = await page.locator('[data-testid="dealer-card"], .dealer-card, [class*="dealer"]').all()
            
            for card in dealer_cards:
                try:
                    # Extract dealer information
                    dealer_data = {}
                    
                    # Try to get dealer name
                    name_element = await card.locator('h3, h2, [class*="name"], [class*="title"]').first
                    if await name_element.count() > 0:
                        dealer_data['name'] = await name_element.text_content()
                    
                    # Try to get address
                    address_element = await card.locator('[class*="address"], [class*="location"]').first
                    if await address_element.count() > 0:
                        dealer_data['address'] = await address_element.text_content()
                    
                    # Try to get phone
                    phone_element = await card.locator('[class*="phone"], a[href^="tel:"]').first
                    if await phone_element.count() > 0:
                        dealer_data['phone'] = await phone_element.text_content()
                    
                    # Try to get website
                    website_element = await card.locator('a[href*="infiniti"]').first
                    if await website_element.count() > 0:
                        dealer_data['website'] = await website_element.get_attribute('href')
                    
                    if dealer_data:
                        dealers.append(dealer_data)
                        
                except Exception as e:
                    logger.debug(f"Error extracting dealer data from card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting dealer data from page: {e}")
            
        return dealers
    
    async def consolidate_dealer_data(self):
        """Consolidate dealer data from all GraphQL responses"""
        logger.info("Consolidating dealer data from GraphQL responses...")
        
        for request in self.network_requests:
            try:
                data = request.get('data', {})
                dealers = data.get('data', {}).get('getDealersByLatLng', [])
                
                for dealer in dealers:
                    dealer_id = dealer.get('id')
                    if dealer_id and dealer_id not in self.all_dealers:
                        self.all_dealers[dealer_id] = dealer
                        
            except Exception as e:
                logger.error(f"Error processing network request: {e}")
        
        logger.info(f"Consolidated {len(self.all_dealers)} unique dealers")
    
    async def run_comprehensive_search(self):
        """Run comprehensive dealer search across all zip codes"""
        logger.info("Starting comprehensive Infiniti dealer search...")
        
        browser, page = await self.setup_browser()
        
        try:
            successful_searches = 0
            failed_searches = 0
            
            for i, zip_code in enumerate(ZIP_CODES, 1):
                logger.info(f"Processing zip code {i}/{len(ZIP_CODES)}: {zip_code}")
                
                success = await self.search_dealers(page, zip_code)
                if success:
                    successful_searches += 1
                else:
                    failed_searches += 1
                
                # Small delay between searches to be respectful
                await page.wait_for_timeout(1000)
                
                # Log progress every 10 searches
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(ZIP_CODES)} zip codes processed. "
                              f"Successful: {successful_searches}, Failed: {failed_searches}")
            
            logger.info(f"Search completed. Successful: {successful_searches}, Failed: {failed_searches}")
            
            # Consolidate all dealer data
            await self.consolidate_dealer_data()
            
        finally:
            await browser.close()
    
    def save_results(self, filename: str = None):
        """Save consolidated dealer data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infiniti_comprehensive_dealers_{timestamp}.json"
        
        # Prepare final data structure
        final_data = {
            "metadata": {
                "total_dealers": len(self.all_dealers),
                "search_timestamp": datetime.now().isoformat(),
                "zip_codes_searched": len(ZIP_CODES),
                "network_requests_captured": len(self.network_requests)
            },
            "dealers": list(self.all_dealers.values()),
            "network_requests": self.network_requests
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filename}")
        logger.info(f"Total unique dealers found: {len(self.all_dealers)}")
        
        return filename

async def main():
    """Main function to run the comprehensive dealer search"""
    scraper = InfinitiDealerScraper()
    
    try:
        await scraper.run_comprehensive_search()
        filename = scraper.save_results()
        
        print(f"\n✅ Comprehensive Infiniti dealer search completed!")
        print(f"📄 Results saved to: {filename}")
        print(f"🏪 Total unique dealers found: {len(scraper.all_dealers)}")
        print(f"🌐 Zip codes searched: {len(ZIP_CODES)}")
        print(f"📡 GraphQL requests captured: {len(scraper.network_requests)}")
        
    except Exception as e:
        logger.error(f"Fatal error during scraping: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
