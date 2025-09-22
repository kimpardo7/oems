#!/usr/bin/env python3
"""
BMW Quick Test - Test with just a few ZIP codes
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

# Test with just a few ZIP codes
QUICK_TEST_ZIPS = [
    "10001",  # NYC
    "90210",  # Beverly Hills
    "33101",  # Miami
    "60601",  # Chicago
    "75201",  # Dallas
]

async def extract_dealers_from_page(page):
    """Extract dealer information from the current BMW page"""
    dealers = []
    
    try:
        await page.wait_for_timeout(3000)
        dealer_list = await page.query_selector('.filterable-list-view__dealer-list')
        
        if not dealer_list:
            return dealers
        
        dealer_items = await page.query_selector_all('.filterable-list-view__dealer')
        
        for item in dealer_items:
            try:
                name_elem = await item.query_selector('.filterable-list-view__dealer-name')
                name = await name_elem.text_content() if name_elem else "Unknown"
                
                location_elem = await item.query_selector('.filterable-list-view__dealer-location')
                location_text = await location_elem.text_content() if location_elem else ""
                
                lines = location_text.split('\n') if location_text else []
                
                street = ""
                city = ""
                state = ""
                zip_code = ""
                
                if len(lines) >= 2:
                    first_line = lines[0].strip()
                    if '•' in first_line:
                        street = first_line.split('•')[1].strip()
                    else:
                        street = first_line
                    
                    second_line = lines[1].strip()
                    parts = second_line.split(',')
                    if len(parts) >= 2:
                        city = parts[0].strip()
                        state_zip = parts[1].strip().split()
                        if len(state_zip) >= 2:
                            state = state_zip[0]
                            zip_code = state_zip[1]
                
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
                print(f"  ✅ {name} - {city}, {state}")
                
            except Exception as e:
                print(f"  ❌ Error extracting dealer: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error extracting dealers: {e}")
    
    return dealers

async def quick_bmw_test():
    """Quick test with a few ZIP codes"""
    print("🚗 BMW Quick Test - Testing with 5 ZIP codes...")
    
    all_dealers = []
    seen_dealers = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            for i, zip_code in enumerate(QUICK_TEST_ZIPS, 1):
                print(f"\n🔍 Testing ZIP {zip_code} ({i}/{len(QUICK_TEST_ZIPS)})")
                
                await page.goto("https://www.bmwusa.com/dealer-locator.html", wait_until='domcontentloaded')
                await page.wait_for_timeout(5000)
                
                search_input = await page.query_selector('#location-search')
                if not search_input:
                    print("❌ No search input found")
                    continue
                
                await search_input.click()
                await search_input.fill("")
                await page.wait_for_timeout(500)
                
                for char in zip_code:
                    await search_input.type(char, delay=100)
                    await page.wait_for_timeout(200)
                
                await page.wait_for_timeout(2000)
                
                search_button = await page.query_selector('button[name="location-search-submit"]')
                if search_button:
                    is_disabled = await search_button.get_attribute('disabled')
                    if not is_disabled:
                        await search_button.click()
                    else:
                        await search_input.press('Enter')
                else:
                    await search_input.press('Enter')
                
                await page.wait_for_timeout(8000)
                
                dealers = await extract_dealers_from_page(page)
                
                new_dealers = 0
                for dealer in dealers:
                    key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
                    if key not in seen_dealers:
                        seen_dealers.add(key)
                        all_dealers.append(dealer)
                        new_dealers += 1
                
                print(f"📊 Found {len(dealers)} dealers, {new_dealers} new unique")
                await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()
    
    # Save results
    test_data = {
        "oem": "BMW",
        "test": True,
        "total_dealers_found": len(all_dealers),
        "zip_codes_tested": QUICK_TEST_ZIPS,
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    with open("bmw_quick_test_results.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\n🎉 Quick test complete!")
    print(f"📊 Total unique dealers found: {len(all_dealers)}")
    print(f"💾 Results saved to: bmw_quick_test_results.json")
    
    # Show sample results
    if all_dealers:
        print(f"\n📋 Sample Results (First 5):")
        for i, dealer in enumerate(all_dealers[:5], 1):
            print(f"\n{i}. {dealer['Dealer']}")
            print(f"   Address: {dealer['Street']}, {dealer['City']}, {dealer['State']} {dealer['ZIP']}")
            print(f"   M Performance Center: {dealer['M_Performance_Center']}")

if __name__ == "__main__":
    asyncio.run(quick_bmw_test())
