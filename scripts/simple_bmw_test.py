#!/usr/bin/env python3
"""
Simple BMW dealer test - step by step debugging
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def simple_bmw_test():
    """Simple test to debug BMW page interaction"""
    print("🚗 Starting simple BMW test...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            print("1. Navigating to BMW dealer locator...")
            await page.goto("https://www.bmwusa.com/dealer-locator.html", wait_until='domcontentloaded')
            print("✅ Page loaded")
            
            # Wait a bit for any dynamic content
            await page.wait_for_timeout(3000)
            
            print("2. Taking initial screenshot...")
            await page.screenshot(path="bmw_initial.png")
            print("✅ Screenshot saved: bmw_initial.png")
            
            print("3. Looking for search input...")
            # Try multiple selectors for the search input
            search_selectors = [
                '#location-search',
                'input[placeholder*="ZIP"]',
                'input[placeholder*="zip"]',
                'input[name="location-search"]',
                'input[type="text"]'
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"✅ Found search input with selector: {selector}")
                        search_input = element
                        break
                except:
                    continue
            
            if not search_input:
                print("❌ No search input found")
                # Print page content to debug
                content = await page.content()
                print("Page content preview:")
                print(content[:1000])
                return
            
            print("4. Entering ZIP code...")
            await search_input.click()
            await search_input.fill("10001")
            print("✅ ZIP code entered")
            
            await page.wait_for_timeout(1000)
            
            print("5. Looking for search button...")
            # Try multiple selectors for search button
            button_selectors = [
                'button[name="location-search-submit"]',
                'button:has-text("Search")',
                'button[type="button"]',
                'button'
            ]
            
            search_button = None
            for selector in button_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if "search" in text.lower() or selector == 'button[name="location-search-submit"]':
                            print(f"✅ Found search button with selector: {selector}")
                            search_button = element
                            break
                except:
                    continue
            
            if search_button:
                print("6. Clicking search button...")
                await search_button.click()
                print("✅ Search button clicked")
            else:
                print("6. No search button found, trying Enter key...")
                await search_input.press('Enter')
                print("✅ Enter key pressed")
            
            print("7. Waiting for results...")
            await page.wait_for_timeout(5000)
            
            print("8. Taking results screenshot...")
            await page.screenshot(path="bmw_after_search.png")
            print("✅ Results screenshot saved: bmw_after_search.png")
            
            print("9. Looking for dealer results...")
            # Check for dealer results
            dealer_selectors = [
                '.filterable-list-view__dealer-list',
                '.filterable-list-view__dealer',
                '[class*="dealer"]',
                '[class*="result"]'
            ]
            
            for selector in dealer_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        for i, elem in enumerate(elements[:3]):  # Show first 3
                            text = await elem.text_content()
                            print(f"  Element {i+1}: {text[:100]}...")
                except:
                    continue
            
            print("10. Test completed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="bmw_error.png")
            print("✅ Error screenshot saved: bmw_error.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_bmw_test())
