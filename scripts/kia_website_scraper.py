#!/usr/bin/env python3
"""
Kia Website Dealer Scraper
Scrapes Kia dealership data by interacting with their website
"""

import asyncio
import json
import time
import random
from datetime import datetime
from typing import List, Dict, Set
import aiofiles
from playwright.async_api import async_playwright

# Strategic ZIP codes covering major population centers
ZIP_CODES = [
    # Major cities - one per major metro area
    "10001",  # NYC
    "02101",  # Boston
    "19102",  # Philadelphia
    "20001",  # DC
    "21201",  # Baltimore
    "33101",  # Miami
    "32801",  # Orlando
    "28201",  # Charlotte
    "37201",  # Nashville
    "38101",  # Memphis
    "60601",  # Chicago
    "53201",  # Milwaukee
    "46201",  # Indianapolis
    "63101",  # St Louis
    "75201",  # Dallas
    "77001",  # Houston
    "78201",  # San Antonio
    "85001",  # Phoenix
    "73101",  # Oklahoma City
    "94101",  # San Francisco
    "95801",  # Sacramento
    "97201",  # Portland
    "98101",  # Seattle
    "44101",  # Cleveland
    "48201",  # Detroit
    "55401",  # Minneapolis
    "80201",  # Denver
    "89101",  # Las Vegas
    "87101",  # Albuquerque
    "80101",  # Denver suburbs
    "84001",  # Salt Lake City
    "83701",  # Boise
    "89501",  # Reno
    "95801",  # Sacramento
    "95601",  # Davis
    "94501",  # Oakland
    "95101",  # San Jose
    "90210",  # Beverly Hills
    "92601",  # Santa Ana
    "92101",  # San Diego
    "92801",  # Anaheim
    "91701",  # Pomona
    "90001",  # Los Angeles
    "91301",  # Van Nuys
    "91401",  # Sherman Oaks
    "91501",  # Burbank
    "91601",  # North Hollywood
    "91701",  # Pomona
    "91801",  # Alhambra
    "91901",  # Chula Vista
    "92001",  # Oceanside
    "92101",  # San Diego
    "92201",  # Indio
    "92301",  # Adelanto
    "92401",  # San Bernardino
    "92501",  # Riverside
    "92601",  # Santa Ana
    "92701",  # Santa Ana
    "92801",  # Anaheim
    "92901",  # Anaheim
    "93001",  # Ventura
    "93101",  # Santa Barbara
    "93201",  # Visalia
    "93301",  # Bakersfield
    "93401",  # San Luis Obispo
    "93501",  # Lancaster
    "93601",  # Fresno
    "93701",  # Fresno
    "93801",  # Fresno
    "93901",  # Salinas
    "94001",  # San Mateo
    "94101",  # San Francisco
    "94201",  # Sacramento
    "94301",  # Palo Alto
    "94401",  # San Mateo
    "94501",  # Oakland
    "94601",  # Oakland
    "94701",  # Berkeley
    "94801",  # Richmond
    "94901",  # San Rafael
    "95001",  # San Jose
    "95101",  # San Jose
    "95201",  # Stockton
    "95301",  # Modesto
    "95401",  # Santa Rosa
    "95501",  # Eureka
    "95601",  # Davis
    "95701",  # Sacramento
    "95801",  # Sacramento
    "95901",  # Chico
    "96001",  # Redding
    "96101",  # Reno
    "96201",  # APO
    "96301",  # APO
    "96401",  # APO
    "96501",  # APO
    "96601",  # APO
    "96701",  # Honolulu
    "96801",  # Honolulu
    "96901",  # Guam
    "97001",  # Portland
    "97101",  # Portland
    "97201",  # Portland
    "97301",  # Salem
    "97401",  # Eugene
    "97501",  # Medford
    "97601",  # Klamath Falls
    "97701",  # Bend
    "97801",  # Pendleton
    "97901",  # Ontario
    "98001",  # Seattle
    "98101",  # Seattle
    "98201",  # Everett
    "98301",  # Tacoma
    "98401",  # Tacoma
    "98501",  # Olympia
    "98601",  # Vancouver
    "98701",  # APO
    "98801",  # Wenatchee
    "98901",  # Yakima
    "99001",  # Spokane
    "99101",  # Colville
    "99201",  # Spokane
    "99301",  # Kennewick
    "99401",  # Clarkston
    "99501",  # Anchorage
    "99601",  # Anchorage
    "99701",  # Fairbanks
    "99801",  # Juneau
    "99901",  # Ketchikan
]

class KiaWebsiteScraper:
    def __init__(self):
        self.dealers: Set[str] = set()  # Use dealer IDs to avoid duplicates
        self.dealer_data: List[Dict] = []
        self.output_file = f"kia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    async def collect_dealers(self):
        """Collect dealers using strategic ZIP codes"""
        print(f"Starting Kia dealer collection with {len(ZIP_CODES)} strategic ZIP codes...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=1000)
            
            for i, zip_code in enumerate(ZIP_CODES, 1):
                print(f"Processing ZIP {i}/{len(ZIP_CODES)}: {zip_code}")
                
                try:
                    page = await browser.new_page()
                    await page.set_viewport_size({"width": 1280, "height": 720})
                    
                    dealers = await self.search_dealers_by_zip(zip_code, page)
                    await self.process_dealers(dealers, zip_code)
                    await page.close()
                    
                    # Random delay between requests
                    await asyncio.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    print(f"Error processing ZIP {zip_code}: {e}")
                    continue
            
            await browser.close()
        
        # Save results
        await self.save_results()
        print(f"Collection complete! Found {len(self.dealer_data)} unique dealers.")
    
    async def search_dealers_by_zip(self, zip_code: str, page) -> List[Dict]:
        """Search for dealers using Kia's website"""
        try:
            print(f"Navigating to Kia dealer locator...")
            # Navigate to the main dealer locator page
            await page.goto("https://www.kia.com/us/en/find-a-dealer/", wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # Take screenshot for debugging
            await page.screenshot(path=f"kia_initial_{zip_code}.png")
            
            # Find and fill the zip code input
            print(f"Looking for zip code input...")
            zip_input = await page.wait_for_selector('input[placeholder*="zip"], input[placeholder*="Zip"], input[name*="zip"], input[id*="zip"]', timeout=10000)
            
            if zip_input:
                print(f"Found zip input, entering {zip_code}...")
                await zip_input.click()
                await zip_input.fill("")  # Clear first
                await page.wait_for_timeout(500)
                
                # Type character by character to trigger validation
                for char in zip_code:
                    await zip_input.type(char, delay=100)
                    await page.wait_for_timeout(200)
                
                print(f"ZIP code {zip_code} entered")
                
                # Wait for validation
                await page.wait_for_timeout(2000)
                
                # Take screenshot after typing
                await page.screenshot(path=f"kia_after_typing_{zip_code}.png")
                
                # Look for search button
                print("Looking for search button...")
                search_button = await page.query_selector('button[type="submit"], button:has-text("Search"), button:has-text("Find"), input[type="submit"]')
                
                if search_button:
                    print("Clicking search button...")
                    await search_button.click()
                else:
                    print("No search button found, trying Enter key...")
                    await zip_input.press('Enter')
                
                print("Waiting for results...")
                await page.wait_for_timeout(5000)
                
                # Take screenshot of results
                await page.screenshot(path=f"kia_results_{zip_code}.png")
                
                # Extract dealer information
                dealers = await self.extract_dealers_from_page(page, zip_code)
                return dealers
            else:
                print("No zip input found")
                return []
                    
        except Exception as e:
            print(f"Error searching ZIP {zip_code}: {e}")
            await page.screenshot(path=f"kia_error_{zip_code}.png")
            return []
    
    async def extract_dealers_from_page(self, page, zip_code: str) -> List[Dict]:
        """Extract dealer information from the current page"""
        dealers = []
        
        try:
            print("Extracting dealer information...")
            
            # Wait for results to load
            await page.wait_for_timeout(2000)
            
            # Look for dealer elements with multiple selectors
            dealer_selectors = [
                '[class*="dealer"]',
                '[class*="result"]', 
                '[class*="card"]',
                '[class*="location"]',
                '[class*="store"]',
                'div[class*="dealer"]',
                'div[class*="result"]',
                'div[class*="card"]'
            ]
            
            dealer_elements = None
            for selector in dealer_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        dealer_elements = elements
                        print(f"Found {len(elements)} dealers using selector: {selector}")
                        break
                except:
                    continue
            
            if not dealer_elements:
                print("No dealer elements found with standard selectors, trying text-based search...")
                # Try to find any div that contains "Kia" text
                dealer_elements = await page.query_selector_all('div')
                dealer_elements = [elem for elem in dealer_elements if 'kia' in (await elem.text_content() or '').lower()]
                print(f"Found {len(dealer_elements)} potential dealer elements by text content")
            
            # Extract information from each dealer element
            for i, element in enumerate(dealer_elements):
                try:
                    # Get the full text content to analyze
                    full_text = await element.text_content() or ""
                    
                    # Skip if the element doesn't seem to contain dealer info
                    if not any(keyword in full_text.lower() for keyword in ['kia', 'dealer', 'address', 'phone', 'miles']):
                        continue
                    
                    # Extract dealer information
                    dealer_info = {
                        'zip_searched': zip_code,
                        'name': await self.extract_text_safely(element, [
                            'h1', 'h2', 'h3', 'h4', '.dealer-name', '.result-name', 
                            '.card-name', '[class*="name"]', 'a[href*="kia"]', 'strong'
                        ]),
                        'address': await self.extract_text_safely(element, [
                            '.address', '.dealer-address', '.result-address',
                            '.card-address', '[class*="address"]', 'a[href*="maps"]'
                        ]),
                        'phone': await self.extract_text_safely(element, [
                            '.phone', '.dealer-phone', '.result-phone',
                            '.card-phone', '[class*="phone"]', 'a[href^="tel:"]'
                        ]),
                        'website': await self.extract_href_safely(element, [
                            'a[href*="kia"]', 'a[href*="dealer"]', 
                            '.website-link', '[class*="website"]'
                        ]),
                        'distance': await self.extract_text_safely(element, [
                            '.distance', '.miles', '[class*="distance"]', 
                            '[class*="miles"]', 'strong'
                        ]),
                        'full_text': full_text[:200] + "..." if len(full_text) > 200 else full_text,
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    # Only add if we have meaningful information
                    if dealer_info['name'] or dealer_info['address'] or 'kia' in full_text.lower():
                        dealers.append(dealer_info)
                        print(f"Extracted dealer: {dealer_info['name'] or 'Unknown'}")
                    
                except Exception as e:
                    print(f"Error extracting dealer {i}: {e}")
                    continue
            
            print(f"Extracted {len(dealers)} dealers for ZIP {zip_code}")
            return dealers
            
        except Exception as e:
            print(f"Error extracting dealers: {e}")
            return dealers
    
    async def extract_text_safely(self, element, selectors):
        """Safely extract text from element using multiple selectors"""
        for selector in selectors:
            try:
                sub_element = await element.query_selector(selector)
                if sub_element:
                    text = await sub_element.text_content()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return ""
    
    async def extract_href_safely(self, element, selectors):
        """Safely extract href from element using multiple selectors"""
        for selector in selectors:
            try:
                sub_element = await element.query_selector(selector)
                if sub_element:
                    href = await sub_element.get_attribute('href')
                    if href:
                        return href
            except:
                continue
        return ""
    
    async def process_dealers(self, dealers: List[Dict], zip_code: str):
        """Process and deduplicate dealers"""
        for dealer in dealers:
            # Create unique identifier
            dealer_id = dealer.get("name", "") + "-" + dealer.get("address", "")
            if dealer_id and dealer_id not in self.dealers:
                self.dealers.add(dealer_id)
                self.dealer_data.append(dealer)
    
    async def save_results(self):
        """Save results to JSON file"""
        results = {
            "brand": "Kia",
            "total_dealers": len(self.dealer_data),
            "collection_date": datetime.now().isoformat(),
            "search_method": "website_interaction",
            "source_url": "https://www.kia.com/us/en/find-a-dealer/",
            "dealers": self.dealer_data
        }
        
        async with aiofiles.open(self.output_file, 'w') as f:
            await f.write(json.dumps(results, indent=2))
        
        print(f"Results saved to: {self.output_file}")

async def main():
    """Main function to run the Kia dealer scraper"""
    scraper = KiaWebsiteScraper()
    await scraper.collect_dealers()

if __name__ == "__main__":
    asyncio.run(main())
