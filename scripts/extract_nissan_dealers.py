#!/usr/bin/env python3
"""
Extract Nissan dealers using Playwright
Navigate to Nissan dealer locator and extract dealers from multiple ZIP codes
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict, Set

# ZIP codes to search - start with a few to test
ZIP_CODES_TO_SEARCH = [
    "90210",  # Beverly Hills - test ZIP
    "10001",  # NYC
    "33101",  # Miami
    "60601",  # Chicago
    "75201",  # Dallas
    "77001",  # Houston
    "85001",  # Phoenix
    "98101",  # Seattle
    "30301",  # Atlanta
    "19102",  # Philadelphia
]

async def extract_dealers_from_page(page):
    """Extract dealer information from the current page"""
    dealers = []
    
    try:
        # Wait for dealer results to load - use the correct Nissan selector
        await page.wait_for_selector('div.sc-536f716-2.eGBXOP', timeout=10000)
        
        # Extract all dealer cards using the correct Nissan selector
        dealer_cards = await page.query_selector_all('div.sc-536f716-2.eGBXOP')
        
        print(f"✅ Found {len(dealer_cards)} dealer cards")
        
        for card in dealer_cards:
            try:
                # Extract dealer name using Nissan specific selector
                name_elem = await card.query_selector('h3.sc-536f716-8.NZipW')
                name = await name_elem.text_content() if name_elem else "Unknown"
                
                # Extract website from dealer website button
                website = ""
                website_elem = await card.query_selector('a[data-track-button="dealer-website"]')
                if website_elem:
                    website = await website_elem.get_attribute('href')
                
                # Extract phone number
                phone = ""
                phone_elem = await card.query_selector('a[href^="tel:"]')
                if phone_elem:
                    phone_text = await phone_elem.text_content()
                    if phone_text:
                        phone = phone_text.strip()
                
                # Extract address
                address_elem = await card.query_selector('p.sc-536f716-11.sc-536f716-12.hIwtZp')
                address_text = await address_elem.text_content() if address_elem else ""
                
                # Parse address components
                address_parts = address_text.split(',') if address_text else []
                street = address_parts[0].strip() if len(address_parts) > 0 else ""
                city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ""
                
                # Parse city, state, zip
                city_state_parts = city_state_zip.split() if city_state_zip else []
                if len(city_state_parts) >= 2:
                    state = city_state_parts[-1]
                    zip_code = city_state_parts[-2] if len(city_state_parts) >= 3 else ""
                    city = " ".join(city_state_parts[:-2]) if len(city_state_parts) > 2 else city_state_parts[0]
                else:
                    city = city_state_zip
                    state = ""
                    zip_code = ""
                
                dealer = {
                    "Dealer": name.strip(),
                    "Website": website.strip(),
                    "Phone": phone.strip(),
                    "Email": "",
                    "Street": street,
                    "City": city,
                    "State": state,
                    "ZIP": zip_code
                }
                
                dealers.append(dealer)
                print(f"  ✅ Extracted: {name}")
                
            except Exception as e:
                print(f"  ❌ Error extracting dealer card: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error extracting dealers from page: {e}")
        # Try to get page content for debugging
        try:
            content = await page.content()
            print(f"📄 Page content length: {len(content)} characters")
            if 'nissan' in content.lower():
                print("✅ Page contains 'nissan' - likely correct page")
            else:
                print("⚠️  Page doesn't contain 'nissan' - might be wrong page")
        except:
            pass
    
    return dealers

async def search_dealers_for_zip(page, zip_code):
    """Search for dealers using a specific ZIP code"""
    print(f"\n🔍 Searching for Nissan dealers in ZIP code: {zip_code}")
    
    try:
        # Navigate to Nissan dealer locator
        await page.goto("https://www.nissanusa.com/dealer-locator.html", timeout=60000)
        print("✅ Navigated to Nissan dealer locator")
        
        # Wait for page to load
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(5000)  # Wait for dynamic content
        
        # Look for search input field - use the correct Nissan selector
        search_selectors = [
            'input.sc-b09ff0c6-2.goQJlr.pac-target-input',  # Nissan specific selector
            'input[placeholder*="Location"]',
            'input[placeholder*="ZIP"]',
            'input[placeholder*="zip"]',
            'input[placeholder*="ZIP"]',
            'input[name*="zip"]',
            'input[id*="zip"]',
            'input[type="text"]',
            'input[data-testid*="zip"]',
            'input[class*="zip"]',
            'input'
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                search_input = await page.query_selector(selector)
                if search_input:
                    # Check if it's visible and interactable
                    is_visible = await search_input.is_visible()
                    if is_visible:
                        print(f"✅ Found search input with selector: {selector}")
                        break
                    else:
                        print(f"⚠️  Found input but not visible: {selector}")
                        search_input = None
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
                continue
        
        if not search_input:
            print("❌ Could not find search input field")
            return []
        
        # Clear and fill the search input
        await search_input.click()
        await search_input.fill("")
        await search_input.type(zip_code, delay=100)
        print(f"✅ Entered ZIP code: {zip_code}")
        
        # Wait a moment for the input to be processed
        await page.wait_for_timeout(2000)
        
        # Look for search button or press Enter - use the correct Nissan selector
        search_button_selectors = [
            'button.sc-b09ff0c6-3.erAepT',  # Nissan specific selector
            'button[aria-label="Search"]',
            'button[type="submit"]',
            'button:has-text("Search")',
            'button:has-text("Find")',
            'button:has-text("Locate")',
            '[data-testid="search-button"]',
            '.search-button',
            '.submit-button',
            'button'
        ]
        
        search_button = None
        for selector in search_button_selectors:
            try:
                search_button = await page.query_selector(selector)
                if search_button:
                    is_visible = await search_button.is_visible()
                    if is_visible:
                        print(f"✅ Found search button with selector: {selector}")
                        break
                    else:
                        print(f"⚠️  Found button but not visible: {selector}")
                        search_button = None
            except Exception as e:
                print(f"❌ Error with button selector {selector}: {e}")
                continue
        
        if search_button:
            await search_button.click()
            print("✅ Clicked search button")
        else:
            await search_input.press('Enter')
            print("✅ Pressed Enter to search")
        
        # Wait for results to load
        await page.wait_for_timeout(5000)
        
        # Extract dealers from the page
        dealers = await extract_dealers_from_page(page)
        
        print(f"✅ Found {len(dealers)} dealers for ZIP {zip_code}")
        return dealers
        
    except Exception as e:
        print(f"❌ Error searching ZIP {zip_code}: {e}")
        return []

async def main():
    """Main function to extract Nissan dealers"""
    print("🚗 Starting Nissan dealer extraction with Playwright...")
    
    all_dealers = []
    seen_dealers = set()
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,  # Show browser for debugging
            slow_mo=1000     # Slow down for better reliability
        )
        
        page = await browser.new_page()
        
        # Set viewport
        await page.set_viewport_size({"width": 1280, "height": 720})
        
        # Set user agent to avoid detection
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        try:
            for i, zip_code in enumerate(ZIP_CODES_TO_SEARCH, 1):
                print(f"\n📍 Progress: {i}/{len(ZIP_CODES_TO_SEARCH)}")
                dealers = await search_dealers_for_zip(page, zip_code)
                
                # Add unique dealers
                for dealer in dealers:
                    key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
                    if key not in seen_dealers:
                        seen_dealers.add(key)
                        all_dealers.append(dealer)
                
                print(f"📊 Total unique dealers so far: {len(all_dealers)}")
                
                # Wait between searches
                await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
        
        finally:
            await browser.close()
    
    # Create JSON output
    nissan_data = {
        "oem": "Nissan",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "nissan_playwright_extraction",
        "zip_codes_searched": len(ZIP_CODES_TO_SEARCH),
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    # Save to file
    with open("data/nissan.json", "w") as f:
        json.dump(nissan_data, f, indent=2)
    
    print(f"\n🎉 Extraction complete!")
    print(f"📊 Total unique dealers found: {len(all_dealers)}")
    print(f"🔍 ZIP codes searched: {len(ZIP_CODES_TO_SEARCH)}")
    print(f"💾 Data saved to: data/nissan.json")
    
    # Print summary by state
    state_counts = {}
    for dealer in all_dealers:
        state = dealer['State']
        if state:
            state_counts[state] = state_counts.get(state, 0) + 1
    
    if state_counts:
        print(f"\n📈 Dealers by state:")
        for state, count in sorted(state_counts.items()):
            print(f"  {state}: {count} dealers")
    else:
        print(f"\n⚠️  No state data found in dealer records")

if __name__ == "__main__":
    asyncio.run(main())
