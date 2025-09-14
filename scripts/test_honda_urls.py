#!/usr/bin/env python3
"""
Test different Honda dealer finder URLs
"""

import asyncio
from playwright.async_api import async_playwright

async def test_honda_urls():
    """Test different Honda dealer finder URLs"""
    
    urls_to_test = [
        "https://automobiles.honda.com/find-a-dealer",
        "https://www.honda.com/find-a-dealer",
        "https://owners.honda.com/service-maintenance/find-a-dealer",
        "https://automobiles.honda.com/dealer-locator",
        "https://www.honda.com/dealer-locator"
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        for url in urls_to_test:
            try:
                print(f"\nTesting URL: {url}")
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                page_title = await page.title()
                current_url = page.url
                
                print(f"  Title: {page_title}")
                print(f"  Final URL: {current_url}")
                
                # Check for common elements
                zip_input = await page.query_selector('input[placeholder*="zip"], input[placeholder*="ZIP"], input[type="text"]')
                if zip_input:
                    print("  ✓ Found ZIP input field")
                else:
                    print("  ✗ No ZIP input field found")
                
                # Check for search button
                search_btn = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Search")')
                if search_btn:
                    print("  ✓ Found search button")
                else:
                    print("  ✗ No search button found")
                
                # Check for dealer finder text
                page_content = await page.content()
                if "dealer" in page_content.lower():
                    print("  ✓ Page contains dealer-related content")
                else:
                    print("  ✗ No dealer-related content found")
                    
            except Exception as e:
                print(f"  Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_honda_urls())
