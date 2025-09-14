#!/usr/bin/env python3
"""
Simple Honda dealer extraction
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def main():
    """Simple Honda dealer extraction"""
    print("🚗 Starting simple Honda dealer extraction...")
    
    async with async_playwright() as p:
        # Try different browser launch methods
        try:
            # Method 1: Launch with minimal settings
            browser = await p.chromium.launch(
                headless=False,
                args=['--no-sandbox']
            )
            print("✅ Browser launched with minimal settings")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            try:
                # Method 2: Launch with different executable path
                browser = await p.chromium.launch(
                    headless=False,
                    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                )
                print("✅ Browser launched with Chrome executable")
            except Exception as e2:
                print(f"❌ Method 2 failed: {e2}")
                return
        
        page = await browser.new_page()
        print("✅ New page created")
        
        try:
            # Navigate to Honda dealer locator
            print("🌐 Navigating to Honda dealer locator...")
            await page.goto("https://automobiles.honda.com/tools/dealership-locator")
            print("✅ Navigated to Honda dealer locator")
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            print("✅ Page loaded")
            
            # Take screenshot
            await page.screenshot(path="honda_simple_test.png")
            print("📸 Screenshot saved as honda_simple_test.png")
            
            # Wait a bit
            await page.wait_for_timeout(5000)
            print("⏰ Waited 5 seconds")
            
            # Try to find and interact with search input
            search_input = await page.query_selector('#placeLocation')
            if search_input:
                print("✅ Found search input field")
                
                await search_input.click()
                print("✅ Clicked on search input")
                
                await search_input.fill("10001")
                print("✅ Typed ZIP code: 10001")
                
                # Find submit button
                submit_button = await page.query_selector('button[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    print("✅ Clicked submit button")
                else:
                    await search_input.press('Enter')
                    print("✅ Pressed Enter")
                
                # Wait for results
                await page.wait_for_timeout(5000)
                print("⏰ Waited for results")
                
                # Take another screenshot
                await page.screenshot(path="honda_with_results.png")
                print("📸 Results screenshot saved")
                
            else:
                print("❌ Could not find search input")
            
        except Exception as e:
            print(f"❌ Error during navigation: {e}")
        
        finally:
            await browser.close()
            print("✅ Browser closed")

if __name__ == "__main__":
    asyncio.run(main())

