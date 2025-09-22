#!/usr/bin/env python3
"""
Kia Proper Dealer Scraper
Scrapes Kia dealership data by using the zip code search form on the website
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
    "84001",  # Salt Lake City
    "83701",  # Boise
    "89501",  # Reno
    "90210",  # Beverly Hills
    "92601",  # Santa Ana
    "92101",  # San Diego
    "92801",  # Anaheim
    "90001",  # Los Angeles
    "91301",  # Van Nuys
    "91401",  # Sherman Oaks
    "91501",  # Burbank
    "91601",  # North Hollywood
    "91701",  # Pomona
    "91801",  # Alhambra
    "91901",  # Chula Vista
    "92001",  # Oceanside
    "92201",  # Indio
    "92301",  # Adelanto
    "92401",  # San Bernardino
    "92501",  # Riverside
    "93001",  # Ventura
    "93101",  # Santa Barbara
    "93201",  # Visalia
    "93301",  # Bakersfield
    "93401",  # San Luis Obispo
    "93501",  # Lancaster
    "93601",  # Fresno
    "93701",  # Fresno
    "93901",  # Salinas
    "94001",  # San Mateo
    "94101",  # San Francisco
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
    "96701",  # Honolulu
    "96801",  # Honolulu
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

class KiaProperScraper:
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
        """Search for dealers using the zip code form on the website"""
        try:
            print(f"Navigating to Kia dealer locator...")
            # Navigate to the main dealer locator page
            await page.goto("https://www.kia.com/us/en/find-a-dealer/", wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # Take screenshot for debugging
            await page.screenshot(path=f"kia_initial_{zip_code}.png")
            
            # Find the zip code input form
            print(f"Looking for zip code input...")
            zip_input = await page.wait_for_selector('#zip-input', timeout=10000)
            
            if zip_input:
                print(f"Found zip input, entering {zip_code}...")
                await zip_input.click()
                await zip_input.fill("")  # Clear first
                await page.wait_for_timeout(500)
                
                # Type the zip code
                await zip_input.type(zip_code)
                await page.wait_for_timeout(1000)
                
                print(f"ZIP code {zip_code} entered")
                
                # Take screenshot after typing
                await page.screenshot(path=f"kia_after_typing_{zip_code}.png")
                
                # Submit the form
                print("Submitting form...")
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
            
            # Look for dealer list items using the specific class from the HTML you provided
            dealer_elements = await page.query_selector_all('.dealer-list-item')
            
            if not dealer_elements:
                # Try alternative selectors
                dealer_elements = await page.query_selector_all('[class*="dealer-list-item"]')
            
            print(f"Found {len(dealer_elements)} dealer elements for ZIP {zip_code}")
            
            for i, element in enumerate(dealer_elements):
                try:
                    # Extract dealer information using the specific structure
                    dealer_info = {
                        'zip_searched': zip_code,
                        'name': await self.extract_text_safely(element, [
                            '.dealer-info__name',
                            'a[href*="kia"]',
                            'a[href*="dealer"]'
                        ]),
                        'address': await self.extract_dealer_address(element),
                        'phone': await self.extract_text_safely(element, [
                            '.dealer-info__phone',
                            'a[href^="tel:"]'
                        ]),
                        'website': await self.extract_href_safely(element, [
                            '.dealer-info__name',
                            'a[href*="kia"]',
                            'a[href*="dealer"]'
                        ]),
                        'distance': await self.extract_text_safely(element, [
                            '.dealer-info__distance',
                            'a[href*="maps"]'
                        ]),
                        'features': await self.extract_dealer_features(element),
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    # Only add if we have meaningful information
                    if dealer_info['name']:
                        dealers.append(dealer_info)
                        print(f"Extracted dealer: {dealer_info['name']}")
                    
                except Exception as e:
                    print(f"Error extracting dealer {i}: {e}")
                    continue
            
            print(f"Extracted {len(dealers)} dealers for ZIP {zip_code}")
            return dealers
            
        except Exception as e:
            print(f"Error extracting dealers: {e}")
            return dealers
    
    async def extract_dealer_address(self, element):
        """Extract dealer address from the specific structure"""
        try:
            # Get the address link
            address_link = await element.query_selector('.dealer-info__address')
            if address_link:
                # Get street line
                street = await self.extract_text_safely(address_link, ['.dealer-info__street-line'])
                # Get city
                city = await self.extract_text_safely(address_link, ['.dealer-info__city'])
                # Get state
                state = await self.extract_text_safely(address_link, ['.dealer-info__state'])
                # Get zip
                zip_code = await self.extract_text_safely(address_link, ['.dealer-info__zipcode'])
                
                # Combine into full address
                address_parts = [street, city, state, zip_code]
                address = ' '.join([part for part in address_parts if part])
                return address
        except:
            pass
        return ""
    
    async def extract_dealer_features(self, element):
        """Extract dealer features"""
        try:
            features = []
            feature_elements = await element.query_selector_all('.dealer-list-item__feature')
            for feature_elem in feature_elements:
                feature_text = await self.extract_text_safely(feature_elem, ['.feature-name'])
                if feature_text:
                    features.append(feature_text)
            return features
        except:
            return []
    
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
            "search_method": "website_form_interaction",
            "source_url": "https://www.kia.com/us/en/find-a-dealer/",
            "dealers": self.dealer_data
        }
        
        async with aiofiles.open(self.output_file, 'w') as f:
            await f.write(json.dumps(results, indent=2))
        
        print(f"Results saved to: {self.output_file}")

async def main():
    """Main function to run the Kia dealer scraper"""
    scraper = KiaProperScraper()
    await scraper.collect_dealers()

if __name__ == "__main__":
    asyncio.run(main())
