#!/usr/bin/env python3
"""
Test Playwright installation and basic functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    """Test basic Playwright functionality"""
    print("Testing Playwright installation...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to a simple page
        await page.goto("https://www.google.com")
        print("✅ Successfully navigated to Google")
        
        # Take a screenshot
        await page.screenshot(path="test_screenshot.png")
        print("✅ Screenshot saved as test_screenshot.png")
        
        # Get page title
        title = await page.title()
        print(f"✅ Page title: {title}")
        
        # Close browser
        await browser.close()
        print("✅ Browser closed successfully")
        
        print("\n🎉 Playwright is working correctly!")

if __name__ == "__main__":
    asyncio.run(test_playwright())

