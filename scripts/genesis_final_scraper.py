#!/usr/bin/env python3
"""
Final Genesis Dealerships Google Maps Scraper
Based on the actual HTML structure from the Google Maps results
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright
import time

class GenesisFinalScraper:
    def __init__(self):
        self.dealerships = []
        
    async def scrape_dealerships(self):
        """Main method to scrape Genesis dealerships from Google Maps"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                # Navigate to Google Maps directly
                print("Navigating to Google Maps...")
                await page.goto("https://www.google.com/maps", wait_until='networkidle')
                await page.wait_for_timeout(2000)
                
                # Take initial screenshot
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_final_initial.png')
                print("Initial screenshot saved: genesis_final_initial.png")
                
                # Search for Genesis dealerships
                print("Searching for Genesis dealerships...")
                search_box = await page.query_selector('input[aria-label="Search Google Maps"]')
                if search_box:
                    await search_box.fill("Genesis dealerships in USA")
                    await search_box.press('Enter')
                    await page.wait_for_timeout(5000)
                else:
                    print("Search box not found, trying alternative approach...")
                    # Try alternative search box selectors
                    search_selectors = [
                        'input[placeholder*="Search"]',
                        'input[type="search"]',
                        'input[name="q"]',
                        '#searchboxinput'
                    ]
                    
                    for selector in search_selectors:
                        search_box = await page.query_selector(selector)
                        if search_box:
                            await search_box.fill("Genesis dealerships in USA")
                            await search_box.press('Enter')
                            await page.wait_for_timeout(5000)
                            break
                
                # Take screenshot after search
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_final_after_search.png')
                print("After search screenshot saved: genesis_final_after_search.png")
                
                # Wait for results to load
                print("Waiting for results to load...")
                await page.wait_for_timeout(8000)
                
                # Extract dealerships using the specific selectors from the HTML
                await self.extract_dealerships_from_maps(page)
                
                # Take final screenshot
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_final_results.png')
                print("Final screenshot saved: genesis_final_results.png")
                
            except Exception as e:
                print(f"Error during scraping: {e}")
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_final_error.png')
                print("Error screenshot saved: genesis_final_error.png")
            
            finally:
                await browser.close()
    
    async def extract_dealerships_from_maps(self, page):
        """Extract dealerships from Google Maps results using specific selectors"""
        try:
            # Wait for the results panel to appear
            await page.wait_for_selector('[role="main"]', timeout=10000)
            
            # Look for the specific result containers based on the HTML structure
            result_containers = await page.query_selector_all('div[jscontroller="AtSb"]')
            
            print(f"Found {len(result_containers)} result containers")
            
            for i, container in enumerate(result_containers):
                try:
                    dealership_data = await self.extract_dealership_from_container(page, container, i)
                    if dealership_data and dealership_data.get('name'):
                        self.dealerships.append(dealership_data)
                        print(f"Extracted dealership {len(self.dealerships)}: {dealership_data['name']}")
                except Exception as e:
                    print(f"Error extracting container {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_dealerships_from_maps: {e}")
    
    async def extract_dealership_from_container(self, page, container, index):
        """Extract data from a single dealership container"""
        try:
            dealership_data = {
                'index': index,
                'name': '',
                'address': '',
                'phone': '',
                'rating': '',
                'reviews_count': '',
                'website': '',
                'hours': '',
                'status': '',
                'category': 'Genesis Dealership',
                'latitude': '',
                'longitude': ''
            }
            
            # Extract coordinates from hidden data
            coords_element = await container.query_selector('.rllt__mi')
            if coords_element:
                lat = await coords_element.get_attribute('data-lat')
                lng = await coords_element.get_attribute('data-lng')
                if lat and lng:
                    dealership_data['latitude'] = lat
                    dealership_data['longitude'] = lng
            
            # Extract name from the heading
            name_element = await container.query_selector('.OSrXXb')
            if name_element:
                dealership_data['name'] = await name_element.inner_text()
            
            # Extract address and phone from the details
            details_element = await container.query_selector('.rllt__details')
            if details_element:
                details_text = await details_element.inner_text()
                lines = details_text.split('\n')
                
                # Parse the lines to extract address and phone
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip the name line (already extracted)
                    if line == dealership_data['name']:
                        continue
                    
                    # Check if it's a phone number
                    if re.match(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', line):
                        dealership_data['phone'] = line
                    # Check if it's an address (contains city, state pattern)
                    elif re.search(r'[A-Za-z\s]+,\s*[A-Z]{2}', line):
                        dealership_data['address'] = line
                    # Check if it's hours/status
                    elif any(word in line.lower() for word in ['open', 'closed', 'closes', 'opens']):
                        dealership_data['status'] = line
                        dealership_data['hours'] = line
            
            # Extract website URL
            website_element = await container.query_selector('a[href*="http"]:not([href*="google.com"])')
            if website_element:
                href = await website_element.get_attribute('href')
                if href and not href.startswith('https://www.google.com'):
                    dealership_data['website'] = href
            
            # Only return if we have at least a name and it contains "Genesis"
            if dealership_data['name'] and 'genesis' in dealership_data['name'].lower():
                return dealership_data
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting dealership data: {e}")
            return None
    
    def save_results(self):
        """Save the scraped results to a JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/Users/kimseanpardo/autodealerships/data/genesis_dealers_{timestamp}.json"
        
        results = {
            'scrape_date': datetime.now().isoformat(),
            'total_dealerships': len(self.dealerships),
            'dealerships': self.dealerships
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {filename}")
        return filename

async def main():
    """Main function to run the scraper"""
    scraper = GenesisFinalScraper()
    
    print("Starting final Genesis dealerships scraper...")
    
    await scraper.scrape_dealerships()
    
    if scraper.dealerships:
        print(f"\nSuccessfully scraped {len(scraper.dealerships)} Genesis dealerships")
        filename = scraper.save_results()
        
        # Print summary
        print("\nDealership Summary:")
        for i, dealer in enumerate(scraper.dealerships, 1):
            print(f"{i}. {dealer.get('name', 'Unknown')} - {dealer.get('address', 'No address')} - {dealer.get('phone', 'No phone')}")
    else:
        print("No dealerships were scraped. Check the screenshots for debugging.")

if __name__ == "__main__":
    asyncio.run(main())
