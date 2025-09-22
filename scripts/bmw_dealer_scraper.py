#!/usr/bin/env python3
"""
BMW Dealer Scraper - Full Production Version
Extract BMW dealers using Playwright by searching multiple ZIP codes
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict, Set

# ZIP codes to search - covering major US cities and regions
ZIP_CODES_TO_SEARCH = [
    # Major Cities
    "10001", "10002", "10003", "10004", "10005",  # NYC
    "90210", "90211", "90212", "90213", "90214",  # Beverly Hills
    "33101", "33102", "33103", "33104", "33105",  # Miami
    "60601", "60602", "60603", "60604", "60605",  # Chicago
    "75201", "75202", "75203", "75204", "75205",  # Dallas
    "77001", "77002", "77003", "77004", "77005",  # Houston
    "85001", "85002", "85003", "85004", "85005",  # Phoenix
    "98101", "98102", "98103", "98104", "98105",  # Seattle
    "30301", "30302", "30303", "30304", "30305",  # Atlanta
    "19102", "19103", "19104", "19105", "19106",  # Philadelphia
    "02101", "02102", "02103", "02104", "02105",  # Boston
    "80201", "80202", "80203", "80204", "80205",  # Denver
    "94101", "94102", "94103", "94104", "94105",  # San Francisco
    "92101", "92102", "92103", "92104", "92105",  # San Diego
    "89101", "89102", "89103", "89104", "89105",  # Las Vegas
    "48201", "48202", "48203", "48204", "48205",  # Detroit
    "43201", "43202", "43203", "43204", "43205",  # Columbus
    "28201", "28202", "28203", "28204", "28205",  # Charlotte
    "37201", "37202", "37203", "37204", "37205",  # Nashville
    "63101", "63102", "63103", "63104", "63105",  # St. Louis
    "64101", "64102", "64103", "64104", "64105",  # Kansas City
    "33701", "33702", "33703", "33704", "33705",  # St. Petersburg
    "55401", "55402", "55403", "55404", "55405",  # Minneapolis
    "84101", "84102", "84103", "84104", "84105",  # Salt Lake City
    "70112", "70113", "70114", "70115", "70116",  # New Orleans
    "73101", "73102", "73103", "73104", "73105",  # Oklahoma City
    "72201", "72202", "72203", "72204", "72205",  # Little Rock
    "36101", "36102", "36103", "36104", "36105",  # Montgomery
    "70112", "70113", "70114", "70115", "70116",  # New Orleans
    "70112", "70113", "70114", "70115", "70116",  # New Orleans
]

async def extract_dealers_from_page(page):
    """Extract dealer information from the current BMW page"""
    dealers = []
    
    try:
        # Wait for results to load
        await page.wait_for_timeout(3000)
        
        # Check if there are any dealer results
        dealer_list = await page.query_selector('.filterable-list-view__dealer-list')
        
        if not dealer_list:
            print("No dealer list found on page")
            return dealers
        
        # Extract all dealer list items
        dealer_items = await page.query_selector_all('.filterable-list-view__dealer')
        
        print(f"Found {len(dealer_items)} dealer items on page")
        
        for item in dealer_items:
            try:
                # Extract dealer name
                name_elem = await item.query_selector('.filterable-list-view__dealer-name')
                name = await name_elem.text_content() if name_elem else "Unknown"
                
                # Extract dealer location (contains distance, address, city, state, zip)
                location_elem = await item.query_selector('.filterable-list-view__dealer-location')
                location_text = await location_elem.text_content() if location_elem else ""
                
                # Parse location text to extract address components
                lines = location_text.split('\n') if location_text else []
                
                street = ""
                city = ""
                state = ""
                zip_code = ""
                
                if len(lines) >= 2:
                    # First line contains distance and street
                    first_line = lines[0].strip()
                    if '•' in first_line:
                        street = first_line.split('•')[1].strip()
                    else:
                        street = first_line
                    
                    # Second line contains city, state, zip
                    second_line = lines[1].strip()
                    parts = second_line.split(',')
                    if len(parts) >= 2:
                        city = parts[0].strip()
                        state_zip = parts[1].strip().split()
                        if len(state_zip) >= 2:
                            state = state_zip[0]
                            zip_code = state_zip[1]
                
                # Check for M Performance Center certification
                m_center_elem = await item.query_selector('.filterable-list-view__m-center')
                m_center = "Yes" if m_center_elem else "No"
                
                # Try to extract phone number (might be in a separate element)
                phone_elem = await item.query_selector('a[href^="tel:"]')
                phone = await phone_elem.get_attribute('href').replace('tel:', '') if phone_elem else ""
                
                # Try to extract website (might be in a separate element)
                website_elem = await item.query_selector('a[href*="http"]:not([href^="tel:"])')
                website = await website_elem.get_attribute('href') if website_elem else ""
                
                dealer = {
                    "Dealer": name.strip(),
                    "Website": website.strip(),
                    "Phone": phone.strip(),
                    "Email": "",
                    "Street": street,
                    "City": city,
                    "State": state,
                    "ZIP": zip_code,
                    "M_Performance_Center": m_center
                }
                
                dealers.append(dealer)
                print(f"  Extracted: {name} - {city}, {state}")
                
            except Exception as e:
                print(f"  Error extracting dealer item: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting dealers from page: {e}")
    
    return dealers

async def search_dealers_for_zip(page, zip_code):
    """Search for dealers using a specific ZIP code"""
    print(f"\n🔍 Searching for BMW dealers in ZIP code: {zip_code}")
    
    try:
        # Navigate to BMW dealer locator
        await page.goto("https://www.bmwusa.com/dealer-locator.html", wait_until='domcontentloaded')
        print("✅ Navigated to BMW dealer locator")
        
        # Wait for page to fully load
        await page.wait_for_timeout(5000)
        
        # Look for the location search input field
        search_input = await page.query_selector('#location-search')
        
        if not search_input:
            print("❌ Could not find location search input field")
            return []
        
        print("✅ Found search input")
        
        # Clear and fill the search input with proper typing
        await search_input.click()
        await search_input.fill("")  # Clear first
        await page.wait_for_timeout(500)
        
        # Type character by character to trigger validation
        for char in zip_code:
            await search_input.type(char, delay=100)
            await page.wait_for_timeout(200)
        
        print(f"✅ ZIP code {zip_code} entered")
        
        # Wait for validation to complete
        await page.wait_for_timeout(2000)
        
        # Look for the search button
        search_button = await page.query_selector('button[name="location-search-submit"]')
        
        if search_button:
            is_disabled = await search_button.get_attribute('disabled')
            
            if not is_disabled:
                await search_button.click()
                print("✅ Search button clicked")
            else:
                print("⚠️ Search button is disabled, trying Enter key")
                await search_input.press('Enter')
        else:
            await search_input.press('Enter')
            print("✅ Pressed Enter to search")
        
        # Wait for results to load
        await page.wait_for_timeout(8000)
        
        # Extract dealers from the page
        dealers = await extract_dealers_from_page(page)
        
        print(f"✅ Found {len(dealers)} dealers for ZIP {zip_code}")
        return dealers
        
    except Exception as e:
        print(f"❌ Error searching ZIP {zip_code}: {e}")
        return []

async def main():
    """Main function to extract BMW dealers"""
    print("🚗 Starting BMW dealer extraction with Playwright...")
    print(f"📋 Will search {len(ZIP_CODES_TO_SEARCH)} ZIP codes")
    
    all_dealers = []
    seen_dealers = set()
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Show browser for debugging
            slow_mo=500     # Slow down for better reliability
        )
        
        page = await browser.new_page()
        
        # Set viewport
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            for i, zip_code in enumerate(ZIP_CODES_TO_SEARCH, 1):
                print(f"\n{'='*50}")
                print(f"Processing ZIP {zip_code} ({i}/{len(ZIP_CODES_TO_SEARCH)})")
                print(f"{'='*50}")
                
                dealers = await search_dealers_for_zip(page, zip_code)
                
                # Add unique dealers
                new_dealers = 0
                for dealer in dealers:
                    key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
                    if key not in seen_dealers:
                        seen_dealers.add(key)
                        all_dealers.append(dealer)
                        new_dealers += 1
                
                print(f"📊 Added {new_dealers} new unique dealers (Total: {len(all_dealers)})")
                
                # Wait between searches to avoid rate limiting
                await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
        
        finally:
            await browser.close()
    
    # Create JSON output
    bmw_data = {
        "oem": "BMW",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "playwright_extraction",
        "zip_codes_searched": len(ZIP_CODES_TO_SEARCH),
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    # Save to file
    with open("data/bmw_dealers.json", "w") as f:
        json.dump(bmw_data, f, indent=2)
    
    print(f"\n🎉 Extraction complete!")
    print(f"📊 Total unique dealers found: {len(all_dealers)}")
    print(f"🔍 ZIP codes searched: {len(ZIP_CODES_TO_SEARCH)}")
    print(f"💾 Data saved to: data/bmw_dealers.json")
    
    # Print summary by state
    state_counts = {}
    m_center_counts = {"Yes": 0, "No": 0}
    
    for dealer in all_dealers:
        state = dealer['State']
        state_counts[state] = state_counts.get(state, 0) + 1
        
        m_center = dealer.get('M_Performance_Center', 'No')
        m_center_counts[m_center] = m_center_counts.get(m_center, 0) + 1
    
    print(f"\n📈 Dealers by state:")
    for state, count in sorted(state_counts.items()):
        print(f"  {state}: {count} dealers")
    
    print(f"\n🏆 M Performance Centers:")
    for status, count in m_center_counts.items():
        print(f"  {status}: {count} dealers")

if __name__ == "__main__":
    asyncio.run(main())
