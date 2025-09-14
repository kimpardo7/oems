#!/usr/bin/env python3
"""
Extract Honda dealers using Playwright
Navigate to Honda dealer locator and extract dealers from multiple ZIP codes
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
]

async def extract_dealers_from_page(page):
    """Extract dealer information from the current page"""
    dealers = []
    
    try:
        # Wait for dealer results to load
        await page.wait_for_selector('[data-testid="dealer-card"]', timeout=10000)
        
        # Extract all dealer cards
        dealer_cards = await page.query_selector_all('[data-testid="dealer-card"]')
        
        print(f"Found {len(dealer_cards)} dealer cards on page")
        
        for card in dealer_cards:
            try:
                # Extract dealer name
                name_elem = await card.query_selector('[data-testid="dealer-name"]')
                name = await name_elem.text_content() if name_elem else "Unknown"
                
                # Extract website
                website_elem = await card.query_selector('a[href*="http"]')
                website = await website_elem.get_attribute('href') if website_elem else ""
                
                # Extract phone
                phone_elem = await card.query_selector('[data-testid="dealer-phone"]')
                phone = await phone_elem.text_content() if phone_elem else ""
                
                # Extract address
                address_elem = await card.query_selector('[data-testid="dealer-address"]')
                address_text = await address_elem.text_content() if address_elem else ""
                
                # Parse address components
                address_parts = address_text.split(',') if address_text else []
                street = address_parts[0].strip() if len(address_parts) > 0 else ""
                city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ""
                
                # Parse city, state, zip
                city_state_parts = city_state_zip.split() if city_state_zip else []
                if len(city_state_parts) >= 2:
                    state = city_state_parts[-1]
                    zip_code = city_state_parts[-2] if len(city_state_parts) >= 3 else ""
                    city = " ".join(city_state_parts[:-2]) if len(city_state_parts) > 2 else city_state_parts[0]
                else:
                    city = city_state_zip
                    state = ""
                    zip_code = ""
                
                dealer = {
                    "Dealer": name.strip(),
                    "Website": website.strip(),
                    "Phone": phone.strip(),
                    "Email": "",
                    "Street": street,
                    "City": city,
                    "State": state,
                    "ZIP": zip_code
                }
                
                dealers.append(dealer)
                print(f"  Extracted: {name}")
                
            except Exception as e:
                print(f"  Error extracting dealer card: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting dealers from page: {e}")
        # Try alternative selectors
        try:
            # Look for any dealer-like elements
            dealer_elements = await page.query_selector_all('.dealer, .dealership, [class*="dealer"], [class*="dealership"]')
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
    print(f"\n🔍 Searching for dealers in ZIP code: {zip_code}")
    
    try:
        # Navigate to Honda dealer locator
        await page.goto("https://automobiles.honda.com/tools/dealership-locator")
        print("✅ Navigated to Honda dealer locator")
        
        # Wait for page to load
        await page.wait_for_load_state('networkidle')
        
        # Look for search input field
        search_selectors = [
            'input[placeholder*="ZIP"]',
            'input[placeholder*="zip"]',
            'input[name*="zip"]',
            'input[id*="zip"]',
            'input[type="text"]',
            'input'
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                search_input = await page.query_selector(selector)
                if search_input:
                    print(f"✅ Found search input with selector: {selector}")
                    break
            except:
                continue
        
        if not search_input:
            print("❌ Could not find search input field")
            return []
        
        # Clear and fill the search input
        await search_input.click()
        await search_input.fill("")
        await search_input.type(zip_code)
        print(f"✅ Entered ZIP code: {zip_code}")
        
        # Look for search button or press Enter
        search_button = await page.query_selector('button[type="submit"], button:has-text("Search"), button:has-text("Find"), [data-testid="search-button"]')
        
        if search_button:
            await search_button.click()
            print("✅ Clicked search button")
        else:
            await search_input.press('Enter')
            print("✅ Pressed Enter to search")
        
        # Wait for results to load
        await page.wait_for_timeout(3000)
        
        # Take screenshot for debugging
        await page.screenshot(path=f"honda_search_{zip_code}.png")
        print(f"📸 Screenshot saved: honda_search_{zip_code}.png")
        
        # Extract dealers from the page
        dealers = await extract_dealers_from_page(page)
        
        print(f"✅ Found {len(dealers)} dealers for ZIP {zip_code}")
        return dealers
        
    except Exception as e:
        print(f"❌ Error searching ZIP {zip_code}: {e}")
        return []

async def main():
    """Main function to extract Honda dealers"""
    print("🚗 Starting Honda dealer extraction with Playwright...")
    
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
    honda_data = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "playwright_extraction",
        "zip_codes_searched": len(ZIP_CODES_TO_SEARCH),
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    # Save to file
    with open("data/honda_playwright.json", "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"\n🎉 Extraction complete!")
    print(f"📊 Total unique dealers found: {len(all_dealers)}")
    print(f"🔍 ZIP codes searched: {len(ZIP_CODES_TO_SEARCH)}")
    print(f"💾 Data saved to: data/honda_playwright.json")
    
    # Print summary by state
    state_counts = {}
    for dealer in all_dealers:
        state = dealer['State']
        state_counts[state] = state_counts.get(state, 0) + 1
    
    print(f"\n📈 Dealers by state:")
    for state, count in sorted(state_counts.items()):
        print(f"  {state}: {count} dealers")

if __name__ == "__main__":
    asyncio.run(main())

