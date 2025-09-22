#!/usr/bin/env python3
"""
Extract BMW dealers using Playwright
Navigate to BMW dealer locator and extract dealers from multiple ZIP codes
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict, Set

# ZIP codes to search - covering major US cities
ZIP_CODES_TO_SEARCH = [
    # Major Cities - Start with a few to test
    "10001", "10002", "10003",  # NYC
    "90210", "90211", "90212",  # Beverly Hills
    "33101", "33102", "33103",  # Miami
    "60601", "60602", "60603",  # Chicago
    "75201", "75202", "75203",  # Dallas
    "77001", "77002", "77003",  # Houston
    "85001", "85002", "85003",  # Phoenix
    "98101", "98102", "98103",  # Seattle
    "30301", "30302", "30303",  # Atlanta
    "19102", "19103", "19104",  # Philadelphia
    "02101", "02102", "02103",  # Boston
    "80201", "80202", "80203",  # Denver
    "94101", "94102", "94103",  # San Francisco
    "92101", "92102", "92103",  # San Diego
    "89101", "89102", "89103",  # Las Vegas
    "48201", "48202", "48203",  # Detroit
    "43201", "43202", "43203",  # Columbus
    "28201", "28202", "28203",  # Charlotte
    "37201", "37202", "37203",  # Nashville
]

async def extract_dealers_from_page(page):
    """Extract dealer information from the current BMW page"""
    dealers = []
    
    try:
        # Wait for dealer results to load - BMW uses specific selectors
        await page.wait_for_selector('.filterable-list-view__dealer-list', timeout=10000)
        
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
                # Format: "5.29 mi  • 1045 SE 3rd St\nBend, OR 97702"
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
        # Try alternative selectors
        try:
            # Look for any dealer-like elements
            dealer_elements = await page.query_selector_all('[class*="dealer"], [class*="dealership"]')
            print(f"Found {len(dealer_elements)} alternative dealer elements")
            
            for elem in dealer_elements:
                text = await elem.text_content()
                if text and len(text.strip()) > 10:
                    print(f"  Found dealer text: {text[:100]}...")
                    
        except Exception as e2:
            print(f"Alternative extraction also failed: {e2}")
    
    return dealers

async def search_dealers_for_zip(page, zip_code):
    """Search for dealers using a specific ZIP code"""
    print(f"\n🔍 Searching for BMW dealers in ZIP code: {zip_code}")
    
    try:
        # Navigate to BMW dealer locator
        await page.goto("https://www.bmwusa.com/dealer-locator.html")
        print("✅ Navigated to BMW dealer locator")
        
        # Wait for page to load
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)
        
        # Look for the location search input field
        search_input = await page.query_selector('#location-search')
        
        if not search_input:
            print("❌ Could not find location search input field")
            return []
        
        # Clear and fill the search input
        await search_input.click()
        await search_input.fill("")
        await search_input.type(zip_code)
        print(f"✅ Entered ZIP code: {zip_code}")
        
        # Wait a moment for the input to be processed
        await page.wait_for_timeout(1000)
        
        # Look for the search button
        search_button = await page.query_selector('button[name="location-search-submit"]')
        
        if search_button:
            # Check if button is enabled
            is_disabled = await search_button.get_attribute('disabled')
            if not is_disabled:
                await search_button.click()
                print("✅ Clicked search button")
            else:
                print("⚠️ Search button is disabled, trying Enter key")
                await search_input.press('Enter')
        else:
            await search_input.press('Enter')
            print("✅ Pressed Enter to search")
        
        # Wait for results to load
        await page.wait_for_timeout(5000)
        
        # Take screenshot for debugging
        await page.screenshot(path=f"bmw_search_{zip_code}.png")
        print(f"📸 Screenshot saved: bmw_search_{zip_code}.png")
        
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
    
    all_dealers = []
    seen_dealers = set()
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Show browser for debugging
            slow_mo=1000     # Slow down for better reliability
        )
        
        page = await browser.new_page()
        
        # Set viewport
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            for zip_code in ZIP_CODES_TO_SEARCH:
                dealers = await search_dealers_for_zip(page, zip_code)
                
                # Add unique dealers
                for dealer in dealers:
                    key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
                    if key not in seen_dealers:
                        seen_dealers.add(key)
                        all_dealers.append(dealer)
                
                # Wait between searches
                await page.wait_for_timeout(2000)
            
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
    with open("data/bmw_playwright.json", "w") as f:
        json.dump(bmw_data, f, indent=2)
    
    print(f"\n🎉 Extraction complete!")
    print(f"📊 Total unique dealers found: {len(all_dealers)}")
    print(f"🔍 ZIP codes searched: {len(ZIP_CODES_TO_SEARCH)}")
    print(f"💾 Data saved to: data/bmw_playwright.json")
    
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
