#!/usr/bin/env python3
"""
Test Nissan dealer locator with a single ZIP code to verify it works
"""

import asyncio
from playwright.async_api import async_playwright

async def test_nissan_single_zip():
    """Test Nissan website with a single ZIP code"""
    print("🔍 Testing Nissan dealer locator with ZIP 90210...")
    
    async with async_playwright() as p:
        # Launch browser in visible mode
        browser = await p.chromium.launch(
            headless=False,  # Show browser
            slow_mo=2000     # Slow down to see what's happening
        )
        
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            # Navigate to Nissan dealer locator
            print("📍 Navigating to Nissan dealer locator...")
            await page.goto("https://www.nissanusa.com/dealer-locator.html")
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            print("✅ Page loaded")
            
            # Take initial screenshot
            await page.screenshot(path="nissan_initial.png")
            print("📸 Initial screenshot saved: nissan_initial.png")
            
            # Wait a bit to see the page
            await page.wait_for_timeout(3000)
            
            # Find the search input field
            print("🔍 Looking for search input field...")
            search_input = await page.query_selector('input.sc-b09ff0c6-2.goQJlr.pac-target-input')
            
            if search_input:
                print("✅ Found search input field")
                
                # Click and enter ZIP code
                await search_input.click()
                await search_input.fill("")
                await search_input.type("90210")
                print("✅ Entered ZIP code: 90210")
                
                # Wait a moment
                await page.wait_for_timeout(2000)
                
                # Find and click search button
                print("🔍 Looking for search button...")
                search_button = await page.query_selector('button.sc-b09ff0c6-3.erAepT')
                
                if search_button:
                    print("✅ Found search button")
                    await search_button.click()
                    print("✅ Clicked search button")
                    
                    # Wait for results
                    await page.wait_for_timeout(5000)
                    
                    # Take screenshot after search
                    await page.screenshot(path="nissan_after_search.png")
                    print("📸 After search screenshot saved: nissan_after_search.png")
                    
                    # Look for dealer results
                    print("🔍 Looking for dealer results...")
                    
                    # Try to find any dealer-related elements
                    dealer_elements = await page.query_selector_all('div, article, section')
                    dealer_count = 0
                    
                    for elem in dealer_elements:
                        text = await elem.text_content()
                        if text and ('nissan' in text.lower() or 'dealer' in text.lower()) and len(text.strip()) > 20:
                            dealer_count += 1
                            print(f"  Found potential dealer content: {text[:100]}...")
                    
                    print(f"📊 Found {dealer_count} potential dealer elements")
                    
                else:
                    print("❌ Could not find search button")
            else:
                print("❌ Could not find search input field")
            
            # Wait to see the final result
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()
    
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_nissan_single_zip())
