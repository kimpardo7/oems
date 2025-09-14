#!/usr/bin/env python3
"""
Simple Nissan dealer locator test - just navigate and take screenshots
to understand the page structure
"""

import asyncio
from playwright.async_api import async_playwright

async def test_nissan_website():
    """Test Nissan website to understand its structure"""
    print("🔍 Testing Nissan dealer locator website...")
    
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
            await page.screenshot(path="nissan_initial_page.png")
            print("📸 Screenshot saved: nissan_initial_page.png")
            
            # Wait a bit to see the page
            await page.wait_for_timeout(5000)
            
            # Try to find any input fields
            print("🔍 Looking for input fields...")
            inputs = await page.query_selector_all('input')
            print(f"Found {len(inputs)} input fields")
            
            for i, input_elem in enumerate(inputs):
                try:
                    input_type = await input_elem.get_attribute('type')
                    placeholder = await input_elem.get_attribute('placeholder')
                    name = await input_elem.get_attribute('name')
                    id_attr = await input_elem.get_attribute('id')
                    print(f"  Input {i}: type={input_type}, placeholder={placeholder}, name={name}, id={id_attr}")
                except:
                    print(f"  Input {i}: Could not get attributes")
            
            # Try to find any buttons
            print("🔍 Looking for buttons...")
            buttons = await page.query_selector_all('button')
            print(f"Found {len(buttons)} buttons")
            
            for i, button in enumerate(buttons):
                try:
                    button_text = await button.text_content()
                    button_type = await button.get_attribute('type')
                    print(f"  Button {i}: text='{button_text}', type={button_type}")
                except:
                    print(f"  Button {i}: Could not get attributes")
            
            # Wait to see the page
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()
    
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_nissan_website())
