import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Set

async def fetch_acura_dealers_with_playwright():
    """
    Use Playwright to fetch Acura dealerships by simulating real browser interactions
    """
    from playwright.async_api import async_playwright
    
    all_dealers = []
    dealer_keys = set()
    
    # Strategic ZIP codes covering major US regions
    strategic_zips = [
        "10001",  # New York, NY
        "90001",  # Los Angeles, CA
        "60601",  # Chicago, IL
        "77001",  # Houston, TX
        "33101",  # Miami, FL
        "30301",  # Atlanta, GA
        "80201",  # Denver, CO
        "98101",  # Seattle, WA
        "94101",  # San Francisco, CA
        "92101",  # San Diego, CA
        "85001",  # Phoenix, AZ
        "89101",  # Las Vegas, NV
        "48201",  # Detroit, MI
        "43201",  # Columbus, OH
        "28201",  # Charlotte, NC
        "37201",  # Nashville, TN
        "63101",  # St. Louis, MO
        "64101",  # Kansas City, MO
        "75201",  # Dallas, TX
        "33701",  # St. Petersburg, FL
    ]
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set to True for production
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        print(f"🚗 Fetching Acura dealerships using Playwright...")
        print(f"📋 Testing {len(strategic_zips)} strategic ZIP codes")
        
        for i, zip_code in enumerate(strategic_zips):
            print(f"\nProcessing ZIP {zip_code} ({i+1}/{len(strategic_zips)})...")
            
            try:
                # Navigate to Acura dealer locator
                await page.goto('https://www.acura.com/dealer-locator', wait_until='networkidle')
                
                # Wait for the page to load
                await page.wait_for_timeout(3000)
                
                # Take a screenshot to see what we're working with
                await page.screenshot(path=f"acura_page_{zip_code}.png")
                print(f"  📸 Screenshot saved as acura_page_{zip_code}.png")
                
                # Try multiple selectors for ZIP input field
                zip_input_selectors = [
                    'input[placeholder*="ZIP"]',
                    'input[placeholder*="zip"]',
                    'input[name*="zip"]',
                    'input[id*="zip"]',
                    'input[type="text"]',
                    'input[placeholder*="Enter"]',
                    'input[placeholder*="Location"]'
                ]
                
                zip_input = None
                for selector in zip_input_selectors:
                    try:
                        zip_input = page.locator(selector).first
                        if await zip_input.count() > 0:
                            print(f"  ✅ Found ZIP input with selector: {selector}")
                            break
                    except:
                        continue
                
                if zip_input and await zip_input.count() > 0:
                    # Clear the field and type the ZIP code
                    await zip_input.click()
                    await zip_input.fill('')  # Clear any existing text
                    await zip_input.type(zip_code, delay=100)  # Type with delay to simulate human
                    print(f"  ✅ Typed ZIP code: {zip_code}")
                    await page.wait_for_timeout(1000)
                    
                    # Try to find and click search button
                    search_button_selectors = [
                        'button[type="submit"]',
                        'button:has-text("Search")',
                        'button:has-text("Find")',
                        'button:has-text("Go")',
                        '[role="button"]:has-text("Search")',
                        'input[type="submit"]'
                    ]
                    
                    search_button = None
                    for selector in search_button_selectors:
                        try:
                            search_button = page.locator(selector).first
                            if await search_button.count() > 0:
                                print(f"  ✅ Found search button with selector: {selector}")
                                break
                        except:
                            continue
                    
                    if search_button and await search_button.count() > 0:
                        await search_button.click()
                        print(f"  ✅ Clicked search button")
                        await page.wait_for_timeout(5000)  # Wait for results to load
                        
                        # Take another screenshot after search
                        await page.screenshot(path=f"acura_results_{zip_code}.png")
                        print(f"  📸 Results screenshot saved as acura_results_{zip_code}.png")
                        
                        # Extract dealer information from the page
                        dealers = await extract_dealers_from_page(page)
                        
                        if dealers:
                            new_dealers = 0
                            for dealer in dealers:
                                dealer_key = f"{dealer['Dealer']}_{dealer['City']}_{dealer['State']}"
                                if dealer_key not in dealer_keys:
                                    dealer_keys.add(dealer_key)
                                    all_dealers.append(dealer)
                                    new_dealers += 1
                            
                            print(f"  ✅ Found {len(dealers)} dealers, {new_dealers} new unique")
                        else:
                            print(f"  ❌ No dealers found on page")
                    else:
                        print(f"  ❌ Search button not found")
                        # Try pressing Enter as alternative
                        await zip_input.press('Enter')
                        print(f"  ✅ Pressed Enter instead")
                        await page.wait_for_timeout(5000)
                else:
                    print(f"  ❌ ZIP input field not found")
                
                # Wait between requests to avoid rate limiting
                await page.wait_for_timeout(2000)
                
            except Exception as e:
                print(f"  ❌ Error processing {zip_code}: {e}")
                continue
        
        await browser.close()
    
    return all_dealers

async def extract_dealers_from_page(page):
    """
    Extract dealer information from the Acura dealer locator page
    """
    dealers = []
    
    try:
        # Look for dealer cards/containers with multiple selectors
        dealer_selectors = [
            '[class*="dealer"]',
            '[class*="card"]',
            '[data-testid*="dealer"]',
            'div:has-text("Acura")',
            'div:has-text("Dealer")',
            '[class*="result"]',
            '[class*="item"]'
        ]
        
        dealer_elements = []
        for selector in dealer_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                if count > 0:
                    dealer_elements = await elements.all()
                    print(f"    ✅ Found {count} dealer elements with selector: {selector}")
                    break
            except:
                continue
        
        if not dealer_elements:
            print(f"    ❌ No dealer elements found")
            return dealers
        
        for dealer_element in dealer_elements:
            try:
                dealer_info = {}
                
                # Extract dealer name
                name_selectors = ['h2', 'h3', '[class*="name"]', '[class*="title"]']
                for selector in name_selectors:
                    try:
                        name_element = dealer_element.locator(selector).first
                        if await name_element.count() > 0:
                            dealer_info['Dealer'] = await name_element.text_content()
                            break
                    except:
                        continue
                
                # Extract address
                address_selectors = ['[class*="address"]', '[class*="location"]', '[class*="street"]']
                for selector in address_selectors:
                    try:
                        address_element = dealer_element.locator(selector).first
                        if await address_element.count() > 0:
                            address_text = await address_element.text_content()
                            # Parse address into components
                            address_parts = address_text.split(',')
                            if len(address_parts) >= 3:
                                dealer_info['Street'] = address_parts[0].strip()
                                dealer_info['City'] = address_parts[1].strip()
                                state_zip = address_parts[2].strip().split()
                                if len(state_zip) >= 2:
                                    dealer_info['State'] = state_zip[0]
                                    dealer_info['ZIP'] = state_zip[1]
                            break
                    except:
                        continue
                
                # Extract phone
                phone_selectors = ['[class*="phone"]', 'a[href^="tel:"]', '[class*="contact"]']
                for selector in phone_selectors:
                    try:
                        phone_element = dealer_element.locator(selector).first
                        if await phone_element.count() > 0:
                            dealer_info['Phone'] = await phone_element.text_content()
                            break
                    except:
                        continue
                
                # Extract website
                try:
                    website_element = dealer_element.locator('a[href*="http"]').first
                    if await website_element.count() > 0:
                        dealer_info['Website'] = await website_element.get_attribute('href')
                except:
                    pass
                
                # Set default values for missing fields
                dealer_info.setdefault('Dealer', '')
                dealer_info.setdefault('Website', '')
                dealer_info.setdefault('Phone', '')
                dealer_info.setdefault('Email', '')  # Email not typically shown on dealer locator
                dealer_info.setdefault('Street', '')
                dealer_info.setdefault('City', '')
                dealer_info.setdefault('State', '')
                dealer_info.setdefault('ZIP', '')
                
                if dealer_info['Dealer']:  # Only add if we have at least a dealer name
                    dealers.append(dealer_info)
                    print(f"    ✅ Extracted dealer: {dealer_info['Dealer']}")
                    
            except Exception as e:
                print(f"    ⚠️ Error extracting dealer: {e}")
                continue
    
    except Exception as e:
        print(f"    ⚠️ Error extracting dealers from page: {e}")
    
    return dealers

def save_to_json(data: Dict, filename: str):
    """
    Save data to JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Data saved to {filename}")

async def main():
    print("🚗 Starting Acura dealership collection with Playwright...")
    
    # Fetch dealers using Playwright
    all_dealers = await fetch_acura_dealers_with_playwright()
    
    if all_dealers:
        # Create output data structure
        output_data = {
            'oem': 'Acura',
            'timestamp': datetime.now().isoformat(),
            'total_dealers_found': len(all_dealers),
            'method': 'playwright_browser_automation',
            'dealers': all_dealers
        }
        
        # Save to JSON file
        save_to_json(output_data, 'acura.json')
        
        print(f"\n📊 Final Summary:")
        print(f"Total unique dealers found: {len(all_dealers)}")
        print(f"Method: Playwright browser automation")
        
        # Print sample
        print(f"\n📋 Sample Data (First 5 Dealers):")
        print("=" * 50)
        for i, dealer in enumerate(all_dealers[:5], 1):
            print(f"\nDealer {i}:")
            for key, value in dealer.items():
                print(f"  {key}: {value}")
    else:
        print("❌ No dealers found")

if __name__ == "__main__":
    asyncio.run(main())
