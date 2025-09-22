#!/usr/bin/env python3
"""
Test script for Infiniti dealer scraper

This script tests the basic functionality with a few zip codes to validate
the approach before running the comprehensive search.
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

# Test zip codes
TEST_ZIP_CODES = [
    "90210",  # Beverly Hills, CA
    "10001",  # New York, NY
    "60601",  # Chicago, IL
]

class InfinitiTestScraper:
    def __init__(self):
        self.network_requests = []
        self.all_dealers = {}
        
    async def setup_browser(self):
        """Initialize browser with network monitoring"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Monitor network requests
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
                    print(f"✅ Captured GraphQL response with {len(response_data.get('data', {}).get('getDealersByLatLng', []))} dealers")
                except Exception as e:
                    print(f"❌ Error parsing GraphQL response: {e}")
        
        page.on("response", handle_response)
        return browser, page
    
    async def search_dealers(self, page, zip_code):
        """Search for dealers using a specific zip code"""
        try:
            print(f"🔍 Searching for dealers near {zip_code}...")
            
            # Navigate to the dealer locator page
            await page.goto("https://www.infinitiusa.com/locate-infiniti-retailer.html", 
                           wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # Clear and enter zip code
            search_box = page.get_by_role('textbox', name='Enter a Location')
            await search_box.clear()
            await search_box.fill(zip_code)
            
            # Click search button
            search_button = page.get_by_role('button', name='Search')
            await search_button.click()
            
            # Wait for results
            await page.wait_for_timeout(4000)
            
            # Check for results
            try:
                results_element = page.locator("text=Results").first
                if await results_element.count() > 0:
                    results_text = await results_element.text_content()
                    print(f"✅ Found results for {zip_code}: {results_text}")
                    return True
                else:
                    print(f"⚠️  No results found for {zip_code}")
                    return False
            except Exception as e:
                print(f"⚠️  Could not determine results for {zip_code}: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error searching dealers for {zip_code}: {e}")
            return False
    
    async def consolidate_dealers(self):
        """Consolidate dealers from all GraphQL responses"""
        print("🔄 Consolidating dealer data...")
        
        for request in self.network_requests:
            try:
                data = request.get('data', {})
                dealers = data.get('data', {}).get('getDealersByLatLng', [])
                
                for dealer in dealers:
                    dealer_id = dealer.get('id')
                    if dealer_id and dealer_id not in self.all_dealers:
                        self.all_dealers[dealer_id] = dealer
                        
            except Exception as e:
                print(f"❌ Error processing network request: {e}")
        
        print(f"✅ Consolidated {len(self.all_dealers)} unique dealers")
    
    async def run_test(self):
        """Run test with a few zip codes"""
        print("🚀 Starting Infiniti dealer scraper test...")
        
        browser, page = await self.setup_browser()
        
        try:
            for i, zip_code in enumerate(TEST_ZIP_CODES, 1):
                print(f"\n📍 Processing {i}/{len(TEST_ZIP_CODES)}: {zip_code}")
                await self.search_dealers(page, zip_code)
                await page.wait_for_timeout(2000)  # Wait between searches
            
            # Consolidate results
            await self.consolidate_dealers()
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infiniti_test_results_{timestamp}.json"
            
            final_data = {
                "metadata": {
                    "total_dealers": len(self.all_dealers),
                    "test_timestamp": datetime.now().isoformat(),
                    "zip_codes_tested": TEST_ZIP_CODES,
                    "network_requests_captured": len(self.network_requests)
                },
                "dealers": list(self.all_dealers.values()),
                "network_requests": self.network_requests
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Test completed!")
            print(f"📄 Results saved to: {filename}")
            print(f"🏪 Unique dealers found: {len(self.all_dealers)}")
            print(f"📡 GraphQL requests captured: {len(self.network_requests)}")
            
        finally:
            await browser.close()

async def main():
    scraper = InfinitiTestScraper()
    await scraper.run_test()

if __name__ == "__main__":
    asyncio.run(main())
