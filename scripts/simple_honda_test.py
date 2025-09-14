#!/usr/bin/env python3
"""
Simple test to open Honda dealer locator
"""

import asyncio
from playwright.async_api import async_playwright

async def simple_test():
    """Simple test to open Honda dealer locator"""
    print("🚗 Opening Honda dealer locator...")
    
    async with async_playwright() as p:
        # Launch browser with more explicit settings
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        print("✅ Browser launched")
        
        page = await browser.new_page()
        print("✅ New page created")
        
        # Set viewport
        await page.set_viewport_size({"width": 1280, "height": 720})
        print("✅ Viewport set")
        
        try:
            # Navigate to Honda dealer locator
            print("🌐 Navigating to Honda dealer locator...")
            await page.goto("https://automobiles.honda.com/tools/dealership-locator")
            print("✅ Navigated to Honda dealer locator")
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            print("✅ Page loaded")
            
            # Take screenshot
            await page.screenshot(path="honda_test.png")
            print("📸 Screenshot saved as honda_test.png")
            
            # Wait a bit to see the page
            await page.wait_for_timeout(5000)
            print("⏰ Waited 5 seconds")
            
            # Try to find the search input
            search_input = await page.query_selector('#placeLocation')
            if search_input:
                print("✅ Found search input field")
                
                # Try to click on it
                await search_input.click()
                print("✅ Clicked on search input")
                
                # Type a test ZIP code
                await search_input.type("10001")
                print("✅ Typed ZIP code: 10001")
                
                # Wait a bit more
                await page.wait_for_timeout(3000)
                print("⏰ Waited 3 more seconds")
                
            else:
                print("❌ Could not find search input field")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            print("🔒 Closing browser...")
            await browser.close()
            print("✅ Browser closed")

if __name__ == "__main__":
    asyncio.run(simple_test())
