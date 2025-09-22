#!/usr/bin/env python3
"""
Improved Genesis Dealerships Google Maps Scraper
Uses a more direct approach to scrape Genesis dealership information
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright
import time

class GenesisImprovedScraper:
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
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_maps_initial.png')
                print("Initial screenshot saved: genesis_maps_initial.png")
                
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
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_maps_after_search.png')
                print("After search screenshot saved: genesis_maps_after_search.png")
                
                # Wait for results to load
                print("Waiting for results to load...")
                await page.wait_for_timeout(8000)
                
                # Extract dealerships
                await self.extract_dealerships_from_maps(page)
                
                # Take final screenshot
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_maps_final.png')
                print("Final screenshot saved: genesis_maps_final.png")
                
            except Exception as e:
                print(f"Error during scraping: {e}")
                await page.screenshot(path='/Users/kimseanpardo/autodealerships/genesis_maps_error.png')
                print("Error screenshot saved: genesis_maps_error.png")
            
            finally:
                await browser.close()
    
    async def extract_dealerships_from_maps(self, page):
        """Extract dealerships from Google Maps results"""
        try:
            # Wait for the results panel to appear
            await page.wait_for_selector('[role="main"]', timeout=10000)
            
            # Look for individual result items
            result_selectors = [
                '[data-result-index]',
                '[jsaction*="click"]',
                'div[role="article"]',
                '.Nv2PK',
                '.THOPZb',
                '.VkpGBb'
            ]
            
            results = []
            for selector in result_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    results = elements
                    print(f"Found {len(elements)} results using selector: {selector}")
                    break
            
            if not results:
                print("No results found with any selector")
                return
            
            print(f"Processing {len(results)} potential dealership results...")
            
            for i, result in enumerate(results[:20]):  # Limit to first 20 results
                try:
                    dealership_data = await self.extract_dealership_from_result(page, result, i)
                    if dealership_data and dealership_data.get('name'):
                        self.dealerships.append(dealership_data)
                        print(f"Extracted dealership {len(self.dealerships)}: {dealership_data['name']}")
                except Exception as e:
                    print(f"Error extracting result {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_dealerships_from_maps: {e}")
    
    async def extract_dealership_from_result(self, page, element, index):
        """Extract data from a single result element"""
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
                'category': 'Genesis Dealership'
            }
            
            # Get all text content from the element
            text_content = await element.inner_text()
            
            # Extract name - look for the main heading
            name_selectors = ['h3', '[role="heading"]', '.fontHeadlineSmall', '.fontHeadlineMedium']
            for selector in name_selectors:
                name_element = await element.query_selector(selector)
                if name_element:
                    dealership_data['name'] = await name_element.inner_text()
                    break
            
            # If no name found, try to extract from text content
            if not dealership_data['name']:
                lines = text_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and not line.isdigit():
                        dealership_data['name'] = line
                        break
            
            # Extract address
            address_patterns = [
                r'\d+.*(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Way|Ln|Lane)',
                r'.*,\s*[A-Z]{2}\s+\d{5}',
                r'.*,\s*[A-Z]{2}'
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, text_content)
                if match:
                    dealership_data['address'] = match.group(0).strip()
                    break
            
            # Extract phone
            phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phone_match = re.search(phone_pattern, text_content)
            if phone_match:
                dealership_data['phone'] = phone_match.group(0)
            
            # Extract rating
            rating_pattern = r'(\d+\.?\d*)\s*stars?'
            rating_match = re.search(rating_pattern, text_content)
            if rating_match:
                dealership_data['rating'] = rating_match.group(1)
            
            # Extract reviews count
            reviews_pattern = r'(\d+)\s*reviews?'
            reviews_match = re.search(reviews_pattern, text_content)
            if reviews_match:
                dealership_data['reviews_count'] = reviews_match.group(1)
            
            # Look for website links
            website_element = await element.query_selector('a[href*="http"]')
            if website_element:
                href = await website_element.get_attribute('href')
                if href and not href.startswith('https://www.google.com'):
                    dealership_data['website'] = href
            
            # Only return if we have at least a name
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
    scraper = GenesisImprovedScraper()
    
    print("Starting improved Genesis dealerships scraper...")
    
    await scraper.scrape_dealerships()
    
    if scraper.dealerships:
        print(f"\nSuccessfully scraped {len(scraper.dealerships)} Genesis dealerships")
        filename = scraper.save_results()
        
        # Print summary
        print("\nDealership Summary:")
        for i, dealer in enumerate(scraper.dealerships, 1):
            print(f"{i}. {dealer.get('name', 'Unknown')} - {dealer.get('address', 'No address')}")
    else:
        print("No dealerships were scraped. Check the screenshots for debugging.")

if __name__ == "__main__":
    asyncio.run(main())
