#!/usr/bin/env python3
"""
Fully automated Honda dealer extraction with pagination handling
No manual input required - runs completely automatically
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
    """Extract dealer information from the current page with pagination handling"""
    dealers = []
    
    try:
        # Wait for page to load
        await page.wait_for_timeout(3000)
        
        # Handle pagination - click "View More Dealers" button multiple times
        max_pagination_clicks = 10  # Limit to prevent infinite loops
        pagination_clicks = 0
        
        while pagination_clicks < max_pagination_clicks:
            # Look for the "View More Dealers" button in the results container
            more_button = await page.query_selector('.dealers-result-more-button-container .dealers-result-more-button')
            
            if more_button:
                try:
                    # Check if button is visible and clickable
                    is_visible = await more_button.is_visible()
                    if is_visible:
                        await more_button.click()
                        print(f"✅ Clicked 'View More Dealers' button (click {pagination_clicks + 1})")
                        await page.wait_for_timeout(2000)  # Wait for new content to load
                        pagination_clicks += 1
                    else:
                        print("✅ 'View More Dealers' button not visible, all dealers loaded")
                        break
                except Exception as e:
                    print(f"❌ Error clicking 'View More Dealers' button: {e}")
                    break
            else:
                print("✅ No 'View More Dealers' button found, all dealers loaded")
                break
        
        # Take screenshot for debugging
        await page.screenshot(path="current_page.png")
        print("📸 Screenshot saved as current_page.png")
        
        # Extract dealers from the dealer-results-container
        dealer_elements = await page.query_selector_all('.dealer-results-container [data-is="dealer"]')
        
        if not dealer_elements:
            print("❌ No dealer elements found")
            return []
        
        print(f"✅ Found {len(dealer_elements)} dealer elements")
        
        for i, element in enumerate(dealer_elements):
            try:
                # Extract dealer name
                name_elem = await element.query_selector('.dealer-name-div a')
                dealer_name = await name_elem.text_content() if name_elem else "Unknown"
                
                # Extract website
                website_elem = await element.query_selector('.dealer-name-div a')
                website = await website_elem.get_attribute('href') if website_elem else ""
                
                # Extract phone number
                phone_elem = await element.query_selector('.phone-cta')
                phone = await phone_elem.text_content() if phone_elem else ""
                
                # Extract address
                address_elem = await element.query_selector('.ae-dealer-address .address-content')
                address_text = await address_elem.text_content() if address_elem else ""
                
                # Parse address components
                address_lines = address_text.split('\n') if address_text else []
                street = address_lines[0].strip() if len(address_lines) > 0 else ""
                city_state_zip = address_lines[1].strip() if len(address_lines) > 1 else ""
                
                # Parse city, state, zip
                city_state_parts = city_state_zip.split(',') if city_state_zip else []
                if len(city_state_parts) >= 2:
                    city = city_state_parts[0].strip()
                    state_zip = city_state_parts[1].strip().split()
                    if len(state_zip) >= 2:
                        state = state_zip[0]
                        zip_code = state_zip[1]
                    else:
                        state = ""
                        zip_code = ""
                else:
                    city = city_state_zip
                    state = ""
                    zip_code = ""
                
                dealer = {
                    "Dealer": dealer_name.strip(),
                    "Website": website.strip(),
                    "Phone": phone.strip(),
                    "Email": "",
                    "Street": street,
                    "City": city,
                    "State": state,
                    "ZIP": zip_code
                }
                
                # Only add if we found a dealer name
                if dealer["Dealer"] != "Unknown":
                    dealers.append(dealer)
                    print(f"✅ Extracted dealer: {dealer['Dealer']} - {dealer['City']}, {dealer['State']}")
                
            except Exception as e:
                print(f"❌ Error extracting dealer {i+1}: {e}")
                continue
        
    except Exception as e:
        print(f"❌ Error extracting dealers: {e}")
    
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
        await page.wait_for_timeout(3000)
        
        # Take initial screenshot
        await page.screenshot(path=f"honda_initial_{zip_code}.png")
        print(f"📸 Initial page screenshot saved")
        
        # Target the specific search input with ID 'placeLocation'
        search_input = await page.query_selector('#placeLocation')
        
        if not search_input:
            print("❌ Could not find search input field with ID 'placeLocation'")
            return []
        
        print("✅ Found search input field")
        
        # Try to interact with the input field
        try:
            # Click on the input field
            await search_input.click()
            print("✅ Clicked on search input")
            
            # Clear the field
            await search_input.fill("")
            print("✅ Cleared search input")
            
            # Type the ZIP code
            await search_input.type(zip_code)
            print(f"✅ Typed ZIP code: {zip_code}")
            
            # Find and click the submit button
            submit_button = await page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                print("✅ Clicked submit button")
            else:
                # Fallback to pressing Enter
                await search_input.press('Enter')
                print("✅ Pressed Enter to search")
            
        except Exception as e:
            print(f"❌ Error interacting with input: {e}")
            return []
        
        # Wait for results to load
        await page.wait_for_timeout(5000)
        
        # Take screenshot after search
        await page.screenshot(path=f"honda_after_search_{zip_code}.png")
        print(f"📸 After search screenshot saved")
        
        # Extract dealers from the page (with pagination handling)
        dealers = await extract_dealers_from_page(page)
        
        print(f"✅ Found {len(dealers)} dealers for ZIP {zip_code}")
        return dealers
        
    except Exception as e:
        print(f"❌ Error searching ZIP {zip_code}: {e}")
        return []

async def main():
    """Main function to extract Honda dealers"""
    print("🚗 Starting automated Honda dealer extraction with pagination...")
    
    all_dealers = []
    seen_dealers = set()
    
    async with async_playwright() as p:
        # Launch browser with working settings from simple test
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox']
        )
        
        print("✅ Browser launched")
        
        page = await browser.new_page()
        print("✅ New page created")
        
        # Set viewport
        await page.set_viewport_size({"width": 1280, "height": 720})
        print("✅ Viewport set")
        
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
        "method": "automated_playwright_extraction_with_pagination",
        "zip_codes_searched": len(ZIP_CODES_TO_SEARCH),
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    # Save to file
    with open("data/honda_auto_playwright.json", "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"\n🎉 Extraction complete!")
    print(f"📊 Total unique dealers found: {len(all_dealers)}")
    print(f"🔍 ZIP codes searched: {len(ZIP_CODES_TO_SEARCH)}")
    print(f"💾 Data saved to: data/honda_auto_playwright.json")
    
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
