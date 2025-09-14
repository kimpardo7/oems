#!/usr/bin/env python3
"""
Working Nissan dealer locator test - with better error handling and waiting
"""

import asyncio
from playwright.async_api import async_playwright

async def test_nissan_working():
    """Test Nissan website with better error handling"""
    print("🔍 Testing Nissan dealer locator with improved approach...")
    
    async with async_playwright() as p:
        # Launch browser in visible mode
        browser = await p.chromium.launch(
            headless=False,  # Show browser
            slow_mo=1000     # Slow down to see what's happening
        )
        
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        # Set user agent to avoid detection
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        try:
            print("📍 Navigating to Nissan dealer locator...")
            
            # Navigate with longer timeout
            await page.goto("https://www.nissanusa.com/dealer-locator.html", timeout=60000)
            print("✅ Page navigation completed")
            
            # Wait for page to be fully loaded
            await page.wait_for_load_state('domcontentloaded')
            print("✅ DOM content loaded")
            
            # Wait a bit more for dynamic content
            await page.wait_for_timeout(5000)
            print("✅ Waited for dynamic content")
            
            # Take initial screenshot
            await page.screenshot(path="nissan_loaded.png")
            print("📸 Screenshot saved: nissan_loaded.png")
            
            # Try to find the search input with multiple approaches
            print("🔍 Looking for search input field...")
            
            # Wait for the input to be visible
            try:
                await page.wait_for_selector('input', timeout=10000)
                print("✅ Found input element")
            except:
                print("⚠️  No input element found, trying alternative approach")
            
            # Try different selectors for the input
            input_selectors = [
                'input.sc-b09ff0c6-2.goQJlr.pac-target-input',
                'input[placeholder*="Location"]',
                'input[placeholder*="Enter"]',
                'input[type="text"]',
                'input'
            ]
            
            search_input = None
            for selector in input_selectors:
                try:
                    search_input = await page.query_selector(selector)
                    if search_input:
                        is_visible = await search_input.is_visible()
                        if is_visible:
                            print(f"✅ Found visible input with selector: {selector}")
                            break
                        else:
                            print(f"⚠️  Found input but not visible: {selector}")
                            search_input = None
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
                    continue
            
            if search_input:
                print("✅ Input field found and visible")
                
                # Click and clear the input
                await search_input.click()
                await search_input.fill("")
                print("✅ Clicked and cleared input field")
                
                # Type the ZIP code slowly
                await search_input.type("90210", delay=100)
                print("✅ Entered ZIP code: 90210")
                
                # Wait a moment
                await page.wait_for_timeout(2000)
                
                # Take screenshot after entering ZIP
                await page.screenshot(path="nissan_with_zip.png")
                print("📸 Screenshot with ZIP saved: nissan_with_zip.png")
                
                # Look for search button
                print("🔍 Looking for search button...")
                
                button_selectors = [
                    'button.sc-b09ff0c6-3.erAepT',
                    'button[aria-label="Search"]',
                    'button:has-text("Search")',
                    'button[type="submit"]',
                    'button'
                ]
                
                search_button = None
                for selector in button_selectors:
                    try:
                        search_button = await page.query_selector(selector)
                        if search_button:
                            is_visible = await search_button.is_visible()
                            if is_visible:
                                print(f"✅ Found visible button with selector: {selector}")
                                break
                            else:
                                print(f"⚠️  Found button but not visible: {selector}")
                                search_button = None
                    except Exception as e:
                        print(f"❌ Error with button selector {selector}: {e}")
                        continue
                
                if search_button:
                    print("✅ Search button found and visible")
                    await search_button.click()
                    print("✅ Clicked search button")
                    
                    # Wait for results
                    await page.wait_for_timeout(5000)
                    
                    # Take screenshot after search
                    await page.screenshot(path="nissan_search_results.png")
                    print("📸 Search results screenshot saved: nissan_search_results.png")
                    
                    # Look for any results on the page
                    print("🔍 Looking for search results...")
                    
                    # Get page content to see what's there
                    content = await page.content()
                    if 'dealer' in content.lower() or 'nissan' in content.lower():
                        print("✅ Page contains dealer-related content")
                    else:
                        print("⚠️  Page doesn't seem to contain dealer content")
                    
                    # Wait to see the results
                    await page.wait_for_timeout(10000)
                    
                else:
                    print("❌ Could not find search button")
                    # Try pressing Enter instead
                    await search_input.press('Enter')
                    print("✅ Pressed Enter instead of clicking button")
                    
                    # Wait for results
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path="nissan_enter_results.png")
                    print("📸 Enter results screenshot saved: nissan_enter_results.png")
                    
            else:
                print("❌ Could not find any input field")
                # Take screenshot to see what's on the page
                await page.screenshot(path="nissan_no_input.png")
                print("📸 Screenshot saved: nissan_no_input.png")
            
        except Exception as e:
            print(f"❌ Error during navigation or interaction: {e}")
            # Take error screenshot
            try:
                await page.screenshot(path="nissan_error.png")
                print("📸 Error screenshot saved: nissan_error.png")
            except:
                pass
        
        finally:
            await browser.close()
    
    print("✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_nissan_working())
