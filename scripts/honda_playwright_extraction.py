#!/usr/bin/env python3
"""
Honda Dealer Extraction using Playwright
Works with existing browser session to change ZIP codes and extract dealer information
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Set
import aiofiles
from playwright.async_api import async_playwright

# Test with a smaller set of ZIP codes first
TEST_ZIP_CODES = [
    "90210",  # Beverly Hills, CA
    "10001",  # New York, NY
    "60601",  # Chicago, IL
    "33101",  # Miami, FL
    "75201",  # Dallas, TX
    "94101",  # San Francisco, CA
    "98101",  # Seattle, WA
    "20001",  # Washington, DC
    "19102",  # Philadelphia, PA
    "02101"   # Boston, MA
]

async def extract_dealers_from_page(page) -> List[Dict]:
    """Extract dealer information from the current page"""
    dealers = []
    
    try:
        # Wait for the page to load and look for dealer elements
        await page.wait_for_timeout(3000)
        
        # Look for dealer cards - these are the elements containing dealer info
        dealer_cards = await page.query_selector_all('h3')
        
        print(f"Found {len(dealer_cards)} potential dealer elements")
        
        for i, card in enumerate(dealer_cards):
            try:
                # Get the dealer name from the h3 element
                dealer_name = await card.text_content()
                if not dealer_name or len(dealer_name.strip()) < 3:
                    continue
                
                print(f"Processing dealer {i+1}: {dealer_name}")
                
                # Find the parent container for this dealer
                parent = await card.query_selector('xpath=..')
                if not parent:
                    continue
                
                # Look for address information
                address_elements = await parent.query_selector_all('a[href*="bing.com/maps"]')
                address = ""
                if address_elements:
                    address = await address_elements[0].text_content()
                
                # Look for phone number
                phone_elements = await parent.query_selector_all('a[href^="tel:"]')
                phone = ""
                if phone_elements:
                    phone = await phone_elements[0].text_content()
                
                # Look for website
                website_elements = await parent.query_selector_all('a[href*="http"][href*="honda"]')
                website = ""
                if website_elements:
                    website = await website_elements[0].get_attribute('href')
                
                # Parse address
                street = ""
                city = ""
                state = ""
                zip_code = ""
                
                if address:
                    # Address format: "6001 Van Nuys Blvd Van Nuys, CA 91401"
                    parts = address.split(',')
                    if len(parts) >= 2:
                        street = parts[0].strip()
                        city_state_zip = parts[1].strip()
                        city_state_parts = city_state_zip.split()
                        if len(city_state_parts) >= 2:
                            state = city_state_parts[-1]
                            zip_code = city_state_parts[-2] if len(city_state_parts) > 2 else ""
                            city = " ".join(city_state_parts[:-2])
                
                dealer_info = {
                    "Dealer": dealer_name.strip(),
                    "Website": website,
                    "Phone": phone.strip() if phone else "",
                    "Email": "",  # Not available on the page
                    "Street": street,
                    "City": city,
                    "State": state,
                    "ZIP": zip_code
                }
                
                dealers.append(dealer_info)
                print(f"  Extracted: {dealer_name} - {city}, {state}")
                
            except Exception as e:
                print(f"Error processing dealer {i+1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting dealers: {e}")
    
    return dealers

async def change_zip_and_search(page, zipcode: str) -> List[Dict]:
    """Change ZIP code in existing page and search for dealers"""
    try:
        print(f"\nChanging ZIP to {zipcode}...")
        
        # Find the search input field that's already on the page
        search_input = await page.query_selector('input[type="text"], input[placeholder*="Search"], input[aria-label*="Search"]')
        
        if not search_input:
            print(f"Could not find search input for ZIP {zipcode}")
            return []
        
        # Clear the existing value and enter new ZIP
        await search_input.click()
        await search_input.fill("")  # Clear first
        await search_input.fill(zipcode)
        
        # Press Enter to search
        await search_input.press('Enter')
        
        # Wait for results to load
        await page.wait_for_timeout(5000)
        
        # Extract dealers from the page
        dealers = await extract_dealers_from_page(page)
        
        print(f"Found {len(dealers)} dealers for ZIP {zipcode}")
        return dealers
        
    except Exception as e:
        print(f"Error changing ZIP to {zipcode}: {e}")
        return []

async def main():
    """Main function to collect Honda dealers using existing browser session"""
    print("Starting Honda dealer collection with existing browser session...")
    
    all_dealers = []
    unique_dealers = set()
    
    # Connect to existing browser session
    async with async_playwright() as p:
        # Connect to existing browser (you'll need to start it manually)
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = await browser.new_page()
        
        # Navigate to Honda dealer locator
        await page.goto('https://automobiles.honda.com/tools/dealership-locator')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)
        
        for i, zipcode in enumerate(TEST_ZIP_CODES, 1):
            print(f"\n--- Processing ZIP {i}/{len(TEST_ZIP_CODES)}: {zipcode} ---")
            
            dealers = await change_zip_and_search(page, zipcode)
            
            for dealer in dealers:
                # Create a unique key for each dealer
                dealer_key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}_{dealer['State']}"
                
                if dealer_key not in unique_dealers:
                    unique_dealers.add(dealer_key)
                    all_dealers.append(dealer)
            
            # Add delay between searches
            await asyncio.sleep(3)
        
        await browser.close()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save simple format like Toyota
    simple_results = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "honda_playwright_extraction",
        "dealers": all_dealers
    }
    
    async with aiofiles.open("data/honda.json", 'w') as f:
        await f.write(json.dumps(simple_results, indent=2))
    
    # Save detailed results
    detailed_results = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "honda_playwright_extraction",
        "timestamp": timestamp,
        "dealers": all_dealers
    }
    
    async with aiofiles.open(f"data/honda_dealers_{timestamp}.json", 'w') as f:
        await f.write(json.dumps(detailed_results, indent=2))
    
    print(f"\nCollection complete!")
    print(f"Total ZIP codes tested: {len(TEST_ZIP_CODES)}")
    print(f"Unique dealers found: {len(all_dealers)}")
    print(f"Results saved to: data/honda.json")
    print(f"Detailed results saved to: data/honda_dealers_{timestamp}.json")

if __name__ == "__main__":
    asyncio.run(main())
