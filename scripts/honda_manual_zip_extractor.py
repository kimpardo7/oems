#!/usr/bin/env python3
"""
Manual Honda dealer extraction with ZIP code input
Opens Honda dealer locator and allows manual ZIP code entry
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict, Set

# ZIP codes to search - covering major US cities
ZIP_CODES_TO_SEARCH = [
    # Major Cities - Start with a few to test
    "10001", "10002", "10003",  # NYC
    "90210", "90211", "90212",  # Beverly Hills
    "33101", "33102", "33103",  # Miami
    "60601", "60602", "60603",  # Chicago
    "75201", "75202", "75203",  # Dallas
    "77001", "77002", "77003",  # Houston
    "85001", "85002", "85003",  # Phoenix
    "98101", "98102", "98103",  # Seattle
    "30301", "30302", "30303",  # Atlanta
    "19102", "19103", "19104",  # Philadelphia
]

async def wait_for_user_input(message):
    """Wait for user to press Enter"""
    print(f"\n{message}")
    input("Press Enter to continue...")

async def extract_dealers_from_page(page):
    """Extract dealer information from the current page"""
    dealers = []
    
    try:
        # Wait a moment for page to load
        await page.wait_for_timeout(2000)
        
        # Take screenshot to see what's on the page
        await page.screenshot(path="current_page.png")
        print("📸 Screenshot saved as current_page.png")
        
        # Try multiple selectors for dealer information
        selectors_to_try = [
            '[data-testid="dealer-card"]',
            '.dealer-card',
            '.dealership-card',
            '[class*="dealer"]',
            '[class*="dealership"]',
            '.result-item',
            '.location-item'
        ]
        
        dealer_elements = []
        for selector in selectors_to_try:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    dealer_elements = elements
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    break
            except:
                continue
        
        if not dealer_elements:
            print("❌ No dealer elements found with any selector")
            # Let's look at the page content
            page_content = await page.content()
            print("📄 Page content preview:")
            print(page_content[:1000])
            return []
        
        for i, element in enumerate(dealer_elements):
            try:
                # Get all text content from the element
                text_content = await element.text_content()
                print(f"\n🔍 Dealer {i+1} content:")
                print(text_content)
                
                # Try to extract structured data
                dealer = {
                    "Dealer": "Unknown",
                    "Website": "",
                    "Phone": "",
                    "Email": "",
                    "Street": "",
                    "City": "",
                    "State": "",
                    "ZIP": ""
                }
                
                # Look for links (websites)
                links = await element.query_selector_all('a[href]')
                for link in links:
                    href = await link.get_attribute('href')
                    if href and 'http' in href:
                        dealer["Website"] = href
                        break
                
                # Try to parse the text content
                lines = text_content.split('\n') if text_content else []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Look for phone numbers
                    if any(char.isdigit() for char in line) and ('-' in line or '(' in line):
                        dealer["Phone"] = line
                    
                    # Look for dealer names (usually first line or contains "Honda")
                    if "Honda" in line and len(line) < 100:
                        dealer["Dealer"] = line
                    
                    # Look for addresses
                    if any(word in line.lower() for word in ['street', 'avenue', 'road', 'blvd', 'drive', 'lane']):
                        dealer["Street"] = line
                
                dealers.append(dealer)
                print(f"✅ Extracted dealer: {dealer['Dealer']}")
                
            except Exception as e:
                print(f"❌ Error extracting dealer {i+1}: {e}")
                continue
        
    except Exception as e:
        print(f"❌ Error extracting dealers: {e}")
    
    return dealers

async def search_dealers_for_zip(page, zip_code):
    """Search for dealers using a specific ZIP code"""
    print(f"\n🔍 Searching for dealers in ZIP code: {zip_code}")
    
    try:
        # Navigate to Honda dealer locator
        await page.goto("https://automobiles.honda.com/tools/dealership-locator")
        print("✅ Navigated to Honda dealer locator")
        
        # Wait for page to load
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)
        
        # Take initial screenshot
        await page.screenshot(path=f"honda_initial_{zip_code}.png")
        print(f"📸 Initial page screenshot saved")
        
        # Wait for user to see the page
        await wait_for_user_input(f"Page loaded for ZIP {zip_code}. Look for the search input field.")
        
        # Try to find the search input with multiple approaches
        search_input = None
        
        # Method 1: Look for input with ZIP in placeholder
        try:
            search_input = await page.query_selector('input[placeholder*="ZIP"], input[placeholder*="zip"]')
            if search_input:
                print("✅ Found search input by placeholder")
        except:
            pass
        
        # Method 2: Look for any text input
        if not search_input:
            try:
                inputs = await page.query_selector_all('input[type="text"]')
                if inputs:
                    search_input = inputs[0]
                    print("✅ Found first text input")
            except:
                pass
        
        # Method 3: Look for any input
        if not search_input:
            try:
                inputs = await page.query_selector_all('input')
                if inputs:
                    search_input = inputs[0]
                    print("✅ Found first input")
            except:
                pass
        
        if not search_input:
            print("❌ Could not find search input field")
            await wait_for_user_input("Please manually enter the ZIP code in the browser and press Enter when done.")
            return []
        
        # Try to interact with the input field
        try:
            # Click on the input field
            await search_input.click()
            print("✅ Clicked on search input")
            
            # Clear the field
            await search_input.fill("")
            print("✅ Cleared search input")
            
            # Type the ZIP code
            await search_input.type(zip_code)
            print(f"✅ Typed ZIP code: {zip_code}")
            
            # Press Enter to search
            await search_input.press('Enter')
            print("✅ Pressed Enter to search")
            
        except Exception as e:
            print(f"❌ Error interacting with input: {e}")
            await wait_for_user_input(f"Please manually enter {zip_code} in the search field and press Enter when done.")
        
        # Wait for results to load
        await page.wait_for_timeout(5000)
        
        # Take screenshot after search
        await page.screenshot(path=f"honda_after_search_{zip_code}.png")
        print(f"📸 After search screenshot saved")
        
        # Wait for user to see results
        await wait_for_user_input("Search completed. Check the results on the page.")
        
        # Extract dealers from the page
        dealers = await extract_dealers_from_page(page)
        
        print(f"✅ Found {len(dealers)} dealers for ZIP {zip_code}")
        return dealers
        
    except Exception as e:
        print(f"❌ Error searching ZIP {zip_code}: {e}")
        return []

async def main():
    """Main function to extract Honda dealers"""
    print("🚗 Starting Honda dealer extraction with manual ZIP input...")
    
    all_dealers = []
    seen_dealers = set()
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Show browser
            slow_mo=500      # Slow down for better reliability
        )
        
        page = await browser.new_page()
        
        # Set viewport
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            for zip_code in ZIP_CODES_TO_SEARCH:
                dealers = await search_dealers_for_zip(page, zip_code)
                
                # Add unique dealers
                for dealer in dealers:
                    key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
                    if key not in seen_dealers:
                        seen_dealers.add(key)
                        all_dealers.append(dealer)
                
                # Ask user if they want to continue
                if zip_code != ZIP_CODES_TO_SEARCH[-1]:
                    continue_search = input(f"\nContinue to next ZIP code ({ZIP_CODES_TO_SEARCH[ZIP_CODES_TO_SEARCH.index(zip_code)+1]})? (y/n): ")
                    if continue_search.lower() != 'y':
                        break
            
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
        
        finally:
            await browser.close()
    
    # Create JSON output
    honda_data = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "manual_playwright_extraction",
        "zip_codes_searched": len(ZIP_CODES_TO_SEARCH),
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    # Save to file
    with open("data/honda_manual_playwright.json", "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"\n🎉 Extraction complete!")
    print(f"📊 Total unique dealers found: {len(all_dealers)}")
    print(f"🔍 ZIP codes searched: {len(ZIP_CODES_TO_SEARCH)}")
    print(f"💾 Data saved to: data/honda_manual_playwright.json")

if __name__ == "__main__":
    asyncio.run(main())

