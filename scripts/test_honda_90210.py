#!/usr/bin/env python3
"""
Test Honda Dealer Locator with ZIP 90210
"""

import asyncio
from playwright.async_api import async_playwright

async def test_honda_90210():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser for debugging
        page = await browser.new_page()
        
        print("Navigating to Honda dealer locator...")
        await page.goto("https://automobiles.honda.com/tools/dealership-locator")
        await page.wait_for_load_state("networkidle")
        
        print("Page loaded, looking for search elements...")
        
        # Try to find any input elements
        inputs = await page.query_selector_all('input')
        print(f"Found {len(inputs)} input elements")
        
        for i, inp in enumerate(inputs):
            placeholder = await inp.get_attribute('placeholder')
            input_type = await inp.get_attribute('type')
            print(f"Input {i}: type={input_type}, placeholder={placeholder}")
        
        # Try to find the search box by different selectors
        selectors_to_try = [
            'input[placeholder*="search"]',
            'input[placeholder*="Search"]',
            'input[type="search"]',
            'input[placeholder*="zip"]',
            'input[placeholder*="ZIP"]',
            'input[placeholder*="location"]',
            'input[placeholder*="Location"]',
            'input[placeholder*="address"]',
            'input[placeholder*="Address"]',
            '.search-input',
            '#search-input',
            '[data-testid*="search"]',
            'input'
        ]
        
        search_box = None
        for selector in selectors_to_try:
            try:
                search_box = await page.wait_for_selector(selector, timeout=2000)
                if search_box:
                    print(f"Found search box with selector: {selector}")
                    break
            except:
                continue
        
        if search_box:
            print("Filling in ZIP code 90210...")
            await search_box.fill("90210")
            await search_box.press("Enter")
            await asyncio.sleep(5)
            
            print("Extracting dealer data...")
            # Look for dealer elements
            dealer_elements = await page.query_selector_all('h3')
            print(f"Found {len(dealer_elements)} h3 elements")
            
            for i, element in enumerate(dealer_elements):
                text = await element.text_content()
                print(f"H3 {i}: {text}")
        
        await asyncio.sleep(10)  # Keep browser open to see results
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_honda_90210())
