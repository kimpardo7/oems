#!/usr/bin/env python3
"""
Working BMW dealer test - handles button state properly
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def bmw_working_test():
    """Working test that handles BMW page properly"""
    print("🚗 Starting working BMW test...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            print("1. Navigating to BMW dealer locator...")
            await page.goto("https://www.bmwusa.com/dealer-locator.html", wait_until='domcontentloaded')
            print("✅ Page loaded")
            
            # Wait for page to fully load
            await page.wait_for_timeout(5000)
            
            print("2. Taking initial screenshot...")
            await page.screenshot(path="bmw_working_initial.png")
            print("✅ Screenshot saved: bmw_working_initial.png")
            
            print("3. Looking for search input...")
            search_input = await page.query_selector('#location-search')
            
            if not search_input:
                print("❌ No search input found")
                return
            
            print("✅ Found search input")
            
            print("4. Entering ZIP code with proper typing...")
            await search_input.click()
            await search_input.fill("")  # Clear first
            await page.wait_for_timeout(500)
            
            # Type character by character to trigger validation
            zip_code = "10001"
            for char in zip_code:
                await search_input.type(char, delay=100)
                await page.wait_for_timeout(200)
            
            print(f"✅ ZIP code {zip_code} entered")
            
            # Wait for validation to complete
            await page.wait_for_timeout(2000)
            
            print("5. Taking screenshot after typing...")
            await page.screenshot(path="bmw_working_after_typing.png")
            print("✅ Screenshot saved: bmw_working_after_typing.png")
            
            print("6. Checking search button state...")
            search_button = await page.query_selector('button[name="location-search-submit"]')
            
            if search_button:
                is_disabled = await search_button.get_attribute('disabled')
                print(f"Search button disabled: {is_disabled}")
                
                if not is_disabled:
                    print("7. Clicking search button...")
                    await search_button.click()
                    print("✅ Search button clicked")
                else:
                    print("7. Button still disabled, trying Enter key...")
                    await search_input.press('Enter')
                    print("✅ Enter key pressed")
            else:
                print("7. No search button found, trying Enter key...")
                await search_input.press('Enter')
                print("✅ Enter key pressed")
            
            print("8. Waiting for results...")
            await page.wait_for_timeout(8000)
            
            print("9. Taking results screenshot...")
            await page.screenshot(path="bmw_working_results.png")
            print("✅ Results screenshot saved: bmw_working_results.png")
            
            print("10. Looking for dealer results...")
            # Check for dealer results with multiple selectors
            dealer_results = []
            
            # Try the main dealer list
            dealer_list = await page.query_selector('.filterable-list-view__dealer-list')
            if dealer_list:
                dealers = await page.query_selector_all('.filterable-list-view__dealer')
                print(f"✅ Found {len(dealers)} dealers in main list")
                
                for i, dealer in enumerate(dealers):
                    try:
                        name_elem = await dealer.query_selector('.filterable-list-view__dealer-name')
                        name = await name_elem.text_content() if name_elem else f"Dealer {i+1}"
                        
                        location_elem = await dealer.query_selector('.filterable-list-view__dealer-location')
                        location = await location_elem.text_content() if location_elem else ""
                        
                        dealer_info = {
                            "name": name.strip(),
                            "location": location.strip()
                        }
                        dealer_results.append(dealer_info)
                        print(f"  Dealer {i+1}: {name}")
                        
                    except Exception as e:
                        print(f"  Error extracting dealer {i+1}: {e}")
            
            # Try alternative selectors if no results found
            if not dealer_results:
                print("No dealers found with main selector, trying alternatives...")
                alt_selectors = [
                    '[class*="dealer"]',
                    '[class*="result"]',
                    '[class*="item"]'
                ]
                
                for selector in alt_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"Found {len(elements)} elements with selector: {selector}")
                            for i, elem in enumerate(elements[:5]):  # Show first 5
                                text = await elem.text_content()
                                if text and len(text.strip()) > 10:
                                    print(f"  Element {i+1}: {text[:100]}...")
                    except:
                        continue
            
            print(f"11. Test completed! Found {len(dealer_results)} dealers")
            
            # Save results
            if dealer_results:
                results_data = {
                    "test_date": datetime.now().isoformat(),
                    "zip_code": "10001",
                    "dealers_found": len(dealer_results),
                    "dealers": dealer_results
                }
                
                with open("bmw_working_results.json", "w") as f:
                    json.dump(results_data, f, indent=2)
                print("✅ Results saved to bmw_working_results.json")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="bmw_working_error.png")
            print("✅ Error screenshot saved: bmw_working_error.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(bmw_working_test())
