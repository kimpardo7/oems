#!/usr/bin/env python3
"""
Fast Honda Dealer Collection Script
Uses strategic ZIP codes to efficiently collect Honda dealerships
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Set
import aiofiles
import re

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

class FastHondaDealerCollector:
    def __init__(self):
        self.dealers: Set[str] = set()  # Use dealer IDs to avoid duplicates
        self.dealer_data: List[Dict] = []
        self.output_file = f"data/honda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
    async def collect_dealers(self):
        """Collect dealers using strategic ZIP codes"""
        print(f"Starting Honda dealer collection with {len(ZIP_CODES)} strategic ZIP codes...")
        
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            for i, zip_code in enumerate(ZIP_CODES, 1):
                print(f"Processing ZIP {i}/{len(ZIP_CODES)}: {zip_code}")
                
                try:
                    page = await browser.new_page()
                    
                    # Navigate to Honda dealer locator
                    await page.goto("https://automobiles.honda.com/tools/dealership-locator")
                    await page.wait_for_load_state("networkidle")
                    
                    # Accept cookies if present
                    try:
                        await page.click("text=Accept All")
                        await asyncio.sleep(1)
                    except:
                        pass
                    
                    # Find and fill search box
                    search_box = await page.wait_for_selector('input[placeholder*="search"], input[placeholder*="Search"], input[type="search"]', timeout=5000)
                    if search_box:
                        await search_box.fill(zip_code)
                        await search_box.press("Enter")
                        await asyncio.sleep(3)
                        
                        # Extract dealer data
                        dealers = await self.extract_dealers_from_page(page)
                        await self.process_dealers(dealers, zip_code)
                    
                    await page.close()
                    await asyncio.sleep(1)  # Brief pause between searches
                    
                except Exception as e:
                    print(f"Error processing ZIP {zip_code}: {e}")
                    continue
            
            await browser.close()
        
        # Save results
        await self.save_results()
        print(f"Collection complete! Found {len(self.dealer_data)} unique dealers.")
    
    async def extract_dealers_from_page(self, page):
        """Extract dealer information from the current page"""
        dealers = []
        
        try:
            # Look for dealer elements
            dealer_elements = await page.query_selector_all('h3')
            
            for element in dealer_elements:
                dealer_name = await element.text_content()
                if dealer_name and "Honda" in dealer_name:
                    dealer_name = dealer_name.strip()
                    # Remove numbering using regex
                    dealer_name = re.sub(r'^\d+\s+', '', dealer_name)
                    
                    # Get parent container
                    parent = await element.query_selector('xpath=..')
                    if not parent:
                        continue
                    
                    # Extract dealer info
                    dealer = {
                        "name": dealer_name,
                        "address": "",
                        "phone": "",
                        "website": "",
                        "dealer_id": "",
                        "distance": ""
                    }
                    
                    # Get address
                    address_link = await parent.query_selector('a[href*="bing.com/maps"]')
                    if address_link:
                        dealer["address"] = await address_link.text_content()
                    
                    # Get phone
                    phone_link = await parent.query_selector('a[href^="tel:"]')
                    if phone_link:
                        dealer["phone"] = await phone_link.text_content()
                    
                    # Get dealer ID
                    quote_link = await parent.query_selector('a[href*="dealerid="]')
                    if quote_link:
                        href = await quote_link.get_attribute('href')
                        if href:
                            match = re.search(r'dealerid=(\d+)', href)
                            if match:
                                dealer["dealer_id"] = match.group(1)
                    
                    # Get distance
                    distance_elem = await parent.query_selector('strong')
                    if distance_elem:
                        dealer["distance"] = await distance_elem.text_content()
                    
                    dealers.append(dealer)
            
        except Exception as e:
            print(f"Error extracting dealers: {e}")
        
        return dealers
    
    async def process_dealers(self, dealers: List[Dict], zip_code: str):
        """Process and deduplicate dealers"""
        for dealer in dealers:
            dealer_id = dealer.get("dealer_id") or dealer.get("name", "")
            if dealer_id and dealer_id not in self.dealers:
                self.dealers.add(dealer_id)
                dealer["source_zip"] = zip_code
                dealer["collected_at"] = datetime.now().isoformat()
                self.dealer_data.append(dealer)
    
    async def save_results(self):
        """Save results to JSON file"""
        results = {
            "brand": "Honda",
            "total_dealers": len(self.dealer_data),
            "collection_date": datetime.now().isoformat(),
            "dealers": self.dealer_data
        }
        
        async with aiofiles.open(self.output_file, 'w') as f:
            await f.write(json.dumps(results, indent=2))
        
        print(f"Results saved to: {self.output_file}")

async def main():
    collector = FastHondaDealerCollector()
    await collector.collect_dealers()

if __name__ == "__main__":
    asyncio.run(main())
