#!/usr/bin/env python3
"""
Extract Honda Dealers from Website
Uses browser automation to extract dealer information from the Honda dealer locator
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Set
import aiofiles
from playwright.async_api import async_playwright

# ZIP codes covering major US regions
ZIP_CODES = [
    # Northeast
    "10001", "02101", "19102", "20001", "21201", "02108", "10002", "19103", "20002", "21202",
    "02109", "10003", "19104", "20003", "21203", "02110", "10004", "19105", "20004", "21204",
    "02111", "10005", "19106", "20005", "21205", "02112", "10006", "19107", "20006", "21206",
    
    # Southeast
    "33101", "32801", "28201", "37201", "38101", "33102", "32802", "28202", "37202", "38102",
    "33103", "32803", "28203", "37203", "38103", "33104", "32804", "28204", "37204", "38104",
    "33105", "32805", "28205", "37205", "38105", "33106", "32806", "28206", "37206", "38106",
    
    # Midwest
    "60601", "53201", "46201", "44101", "48201", "60602", "53202", "46202", "44102", "48202",
    "60603", "53203", "46203", "44103", "48203", "60604", "53204", "46204", "44104", "48204",
    "60605", "53205", "46205", "44105", "48205", "60606", "53206", "46206", "44106", "48206",
    
    # Southwest
    "75201", "77001", "73101", "85001", "89101", "75202", "77002", "73102", "85002", "89102",
    "75203", "77003", "73103", "85003", "89103", "75204", "77004", "73104", "85004", "89104",
    "75205", "77005", "73105", "85005", "89105", "75206", "77006", "73106", "85006", "89106",
    
    # West Coast
    "90210", "94101", "98101", "97201", "95801", "90211", "94102", "98102", "97202", "95802",
    "90212", "94103", "98103", "97203", "95803", "90213", "94104", "98104", "97204", "95804",
    "90214", "94105", "98105", "97205", "95805", "90215", "94106", "98106", "97206", "95806"
]

async def extract_dealers_from_page(page, zipcode: str) -> List[Dict]:
    """Extract dealer information from the current page"""
    dealers = []
    
    try:
        # Wait for dealer results to load
        await page.wait_for_selector('[data-testid="dealer-card"], .dealer-card, [class*="dealer"]', timeout=10000)
        
        # Extract dealer information
        dealer_elements = await page.query_selector_all('[data-testid="dealer-card"], .dealer-card, [class*="dealer"]')
        
        for element in dealer_elements:
            try:
                # Extract dealer name
                name_element = await element.query_selector('h3, [class*="dealer-name"], [class*="name"]')
                name = await name_element.text_content() if name_element else "Unknown"
                
                # Extract address
                address_element = await element.query_selector('[class*="address"], [class*="location"]')
                address = await address_element.text_content() if address_element else ""
                
                # Extract phone
                phone_element = await element.query_selector('a[href^="tel:"], [class*="phone"]')
                phone = await phone_element.text_content() if phone_element else ""
                
                # Extract website
                website_element = await element.query_selector('a[href*="http"], [class*="website"]')
                website = await website_element.get_attribute('href') if website_element else ""
                
                # Parse address components
                address_parts = address.split(',') if address else []
                street = address_parts[0].strip() if len(address_parts) > 0 else ""
                city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ""
                
                city_state_parts = city_state_zip.split() if city_state_zip else []
                if len(city_state_parts) >= 2:
                    state = city_state_parts[-1]
                    zip_code = city_state_parts[-2] if len(city_state_parts) > 2 else ""
                    city = " ".join(city_state_parts[:-2])
                else:
                    state = ""
                    zip_code = ""
                    city = ""
                
                dealer_info = {
                    "Dealer": name,
                    "Website": website,
                    "Phone": phone,
                    "Email": "",  # Not available on the page
                    "Street": street,
                    "City": city,
                    "State": state,
                    "ZIP": zip_code
                }
                
                dealers.append(dealer_info)
                
            except Exception as e:
                print(f"Error extracting dealer info: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting dealers for ZIP {zipcode}: {e}")
    
    return dealers

async def search_dealers_for_zip(page, zipcode: str) -> List[Dict]:
    """Search for dealers using a specific ZIP code"""
    try:
        # Navigate to the dealer locator
        await page.goto('https://automobiles.honda.com/tools/dealership-locator')
        await page.wait_for_load_state('networkidle')
        
        # Find and fill the search box
        search_box = await page.query_selector('input[placeholder*="Search"], input[aria-label*="Search"], input[name*="search"]')
        if search_box:
            await search_box.fill(zipcode)
            await search_box.press('Enter')
            
            # Wait for results to load
            await page.wait_for_timeout(3000)
            
            # Extract dealers from the page
            dealers = await extract_dealers_from_page(page, zipcode)
            return dealers
        else:
            print(f"Could not find search box for ZIP {zipcode}")
            return []
            
    except Exception as e:
        print(f"Error searching for ZIP {zipcode}: {e}")
        return []

async def main():
    """Main function to collect all Honda dealers"""
    print("Starting Honda dealer collection from website...")
    
    all_dealers = []
    unique_dealers = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set user agent to avoid detection
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        for i, zipcode in enumerate(ZIP_CODES, 1):
            print(f"Progress: {i}/{len(ZIP_CODES)} - ZIP: {zipcode}")
            
            dealers = await search_dealers_for_zip(page, zipcode)
            
            for dealer in dealers:
                # Create a unique key for each dealer
                dealer_key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}_{dealer['State']}"
                
                if dealer_key not in unique_dealers:
                    unique_dealers.add(dealer_key)
                    all_dealers.append(dealer)
            
            print(f"  Found {len(dealers)} dealers for ZIP {zipcode}")
            
            # Add delay to avoid overwhelming the server
            await asyncio.sleep(2)
        
        await browser.close()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    detailed_results = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "honda_website_extraction",
        "timestamp": timestamp,
        "dealers": all_dealers
    }
    
    async with aiofiles.open(f"data/honda_dealers_{timestamp}.json", 'w') as f:
        await f.write(json.dumps(detailed_results, indent=2))
    
    # Save simple format like Toyota
    simple_results = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "honda_website_extraction",
        "dealers": all_dealers
    }
    
    async with aiofiles.open("data/honda.json", 'w') as f:
        await f.write(json.dumps(simple_results, indent=2))
    
    print(f"\nCollection complete!")
    print(f"Total ZIP codes tested: {len(ZIP_CODES)}")
    print(f"Unique dealers found: {len(all_dealers)}")
    print(f"Results saved to: data/honda_dealers_{timestamp}.json")
    print(f"Simple format saved to: data/honda.json")

if __name__ == "__main__":
    asyncio.run(main())
