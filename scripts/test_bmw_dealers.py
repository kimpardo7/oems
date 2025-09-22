#!/usr/bin/env python3
"""
Test BMW dealer extraction with just a few ZIP codes
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

# Test with just a few ZIP codes
TEST_ZIP_CODES = [
    "10001",  # NYC
    "90210",  # Beverly Hills
    "33101",  # Miami
]

async def extract_dealers_from_page(page):
    """Extract dealer information from the current BMW page"""
    dealers = []
    
    try:
        # Wait a bit for the page to load
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
                
                dealer = {
                    "Dealer": name.strip(),
                    "Website": "",
                    "Phone": "",
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

async def test_bmw_search():
    """Test BMW dealer search with a few ZIP codes"""
    print("🚗 Testing BMW dealer extraction...")
    
    all_dealers = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            for zip_code in TEST_ZIP_CODES:
                print(f"\n🔍 Testing ZIP code: {zip_code}")
                
                # Navigate to BMW dealer locator
                await page.goto("https://www.bmwusa.com/dealer-locator.html")
                print("✅ Navigated to BMW dealer locator")
                
                # Wait for page to load
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(5000)
                
                # Take a screenshot to see the initial page
                await page.screenshot(path=f"bmw_initial_{zip_code}.png")
                print(f"📸 Initial page screenshot saved: bmw_initial_{zip_code}.png")
                
                # Look for the location search input field
                search_input = await page.query_selector('#location-search')
                
                if not search_input:
                    print("❌ Could not find location search input field")
                    continue
                
                # Clear and fill the search input
                await search_input.click()
                await search_input.fill("")
                await search_input.type(zip_code, delay=100)
                print(f"✅ Entered ZIP code: {zip_code}")
                
                # Wait a moment for the input to be processed
                await page.wait_for_timeout(2000)
                
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
                await page.wait_for_timeout(8000)
                
                # Take screenshot for debugging
                await page.screenshot(path=f"bmw_test_{zip_code}.png")
                print(f"📸 Screenshot saved: bmw_test_{zip_code}.png")
                
                # Extract dealers from the page
                dealers = await extract_dealers_from_page(page)
                all_dealers.extend(dealers)
                
                print(f"✅ Found {len(dealers)} dealers for ZIP {zip_code}")
                
                # Wait between searches
                await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
        
        finally:
            await browser.close()
    
    # Save test results
    test_data = {
        "oem": "BMW",
        "test": True,
        "total_dealers_found": len(all_dealers),
        "zip_codes_tested": TEST_ZIP_CODES,
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    with open("bmw_test_results.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\n🎉 Test complete!")
    print(f"📊 Total dealers found: {len(all_dealers)}")
    print(f"💾 Test results saved to: bmw_test_results.json")
    
    # Print sample results
    if all_dealers:
        print(f"\n📋 Sample Results:")
        for i, dealer in enumerate(all_dealers[:3], 1):
            print(f"\nDealer {i}:")
            for key, value in dealer.items():
                print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_bmw_search())
