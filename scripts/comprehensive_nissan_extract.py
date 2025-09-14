#!/usr/bin/env python3
"""
Comprehensive Nissan dealer extraction across multiple ZIP codes
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

# Comprehensive list of ZIP codes covering major US cities
ZIP_CODES_TO_SEARCH = [
    # West Coast
    "90210", "90211", "90212",  # Beverly Hills, CA
    "10001", "10002", "10003",  # New York, NY
    "33101", "33102", "33103",  # Miami, FL
    "60601", "60602", "60603",  # Chicago, IL
    "75201", "75202", "75203",  # Dallas, TX
    "77001", "77002", "77003",  # Houston, TX
    "85001", "85002", "85003",  # Phoenix, AZ
    "98101", "98102", "98103",  # Seattle, WA
    "30301", "30302", "30303",  # Atlanta, GA
    "19102", "19103", "19104",  # Philadelphia, PA
    "02101", "02102", "02103",  # Boston, MA
    "20001", "20002", "20003",  # Washington, DC
    "28201", "28202", "28203",  # Charlotte, NC
    "37201", "37202", "37203",  # Nashville, TN
    "48201", "48202", "48203",  # Detroit, MI
    "43201", "43202", "43203",  # Columbus, OH
    "46201", "46202", "46203",  # Indianapolis, IN
    "73101", "73102", "73103",  # Oklahoma City, OK
    "80201", "80202", "80203",  # Denver, CO
    "84101", "84102", "84103",  # Salt Lake City, UT
    "89101", "89102", "89103",  # Las Vegas, NV
    "95101", "95102", "95103",  # San Jose, CA
    "95801", "95802", "95803",  # Sacramento, CA
    "97201", "97202", "97203",  # Portland, OR
    "21201", "21202", "21203",  # Baltimore, MD
    "23201", "23202", "23203",  # Richmond, VA
    "27601", "27602", "27603",  # Raleigh, NC
    "29201", "29202", "29203",  # Columbia, SC
    "70101", "70102", "70103",  # New Orleans, LA
    "78401", "78402", "78403",  # Corpus Christi, TX
    "79901", "79902", "79903",  # El Paso, TX
    "87101", "87102", "87103",  # Albuquerque, NM
]

async def extract_dealers_from_page(page):
    """Extract dealer information from the current page"""
    dealers = []
    
    try:
        # Wait for dealer results to load
        await page.wait_for_selector('div.sc-536f716-2.eGBXOP', timeout=10000)
        
        # Extract all dealer cards
        dealer_cards = await page.query_selector_all('div.sc-536f716-2.eGBXOP')
        
        print(f"✅ Found {len(dealer_cards)} dealer cards")
        
        for card in dealer_cards:
            try:
                # Extract dealer name
                name_elem = await card.query_selector('h3.sc-536f716-8.NZipW')
                name = await name_elem.text_content() if name_elem else "Unknown"
                
                # Extract website
                website = ""
                website_elem = await card.query_selector('a[data-track-button="dealer-website"]')
                if website_elem:
                    website = await website_elem.get_attribute('href')
                
                # Extract phone
                phone = ""
                phone_elem = await card.query_selector('a[href^="tel:"]')
                if phone_elem:
                    phone_text = await phone_elem.text_content()
                    if phone_text:
                        phone = phone_text.strip()
                
                # Extract address
                address_elem = await card.query_selector('p.sc-536f716-11.sc-536f716-12.hIwtZp')
                address_text = await address_elem.text_content() if address_elem else ""
                
                # Parse address - improved parsing
                address_parts = address_text.split(',') if address_text else []
                street = address_parts[0].strip() if len(address_parts) > 0 else ""
                city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ""
                
                # Better address parsing
                city_state_parts = city_state_zip.split() if city_state_zip else []
                if len(city_state_parts) >= 2:
                    # Try to identify state (usually 2 letters at the end)
                    if len(city_state_parts[-1]) == 2 and city_state_parts[-1].isupper():
                        state = city_state_parts[-1]
                        # Check if second to last is ZIP code (5 digits)
                        if len(city_state_parts) >= 3 and city_state_parts[-2].isdigit() and len(city_state_parts[-2]) == 5:
                            zip_code = city_state_parts[-2]
                            city = " ".join(city_state_parts[:-2])
                        else:
                            zip_code = ""
                            city = " ".join(city_state_parts[:-1])
                    else:
                        # No clear state, try to parse differently
                        state = ""
                        zip_code = ""
                        city = city_state_zip
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
                print(f"  ❌ Error extracting dealer: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Error extracting dealers from page: {e}")
    
    return dealers

async def search_dealers_for_zip(page, zip_code):
    """Search for dealers using a specific ZIP code"""
    print(f"\n🔍 Searching for Nissan dealers in ZIP code: {zip_code}")
    
    try:
        # Navigate to Nissan dealer locator
        await page.goto("https://www.nissanusa.com/dealer-locator.html", timeout=60000)
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(3000)
        
        # Find and enter ZIP code
        search_input = await page.query_selector('input.sc-b09ff0c6-2.goQJlr.pac-target-input')
        if not search_input:
            print("❌ Could not find search input field")
            return []
        
        await search_input.click()
        await search_input.fill("")
        await search_input.type(zip_code, delay=100)
        print(f"✅ Entered ZIP code: {zip_code}")
        
        # Wait a moment for the input to be processed
        await page.wait_for_timeout(2000)
        
        # Click search button
        search_button = await page.query_selector('button.sc-b09ff0c6-3.erAepT')
        if not search_button:
            print("❌ Could not find search button")
            return []
        
        await search_button.click()
        print("✅ Clicked search button")
        
        # Wait for results
        await page.wait_for_timeout(5000)
        
        # Extract dealers from the page
        dealers = await extract_dealers_from_page(page)
        
        print(f"✅ Found {len(dealers)} dealers for ZIP {zip_code}")
        return dealers
        
    except Exception as e:
        print(f"❌ Error searching ZIP {zip_code}: {e}")
        return []

async def main():
    """Main function to extract Nissan dealers from multiple ZIP codes"""
    print("🚗 Starting comprehensive Nissan dealer extraction...")
    print(f"📍 Total ZIP codes to process: {len(ZIP_CODES_TO_SEARCH)}")
    
    all_dealers = []
    seen_dealers = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            for i, zip_code in enumerate(ZIP_CODES_TO_SEARCH, 1):
                print(f"\n📍 Progress: {i}/{len(ZIP_CODES_TO_SEARCH)}")
                
                dealers = await search_dealers_for_zip(page, zip_code)
                
                # Add unique dealers
                for dealer in dealers:
                    # Create a unique key for each dealer
                    dealer_key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
                    
                    if dealer_key not in seen_dealers:
                        seen_dealers.add(dealer_key)
                        all_dealers.append(dealer)
                
                print(f"📊 Total unique dealers so far: {len(all_dealers)}")
                
                # Wait between searches to be respectful
                await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
        
        finally:
            await browser.close()
    
    # Create comprehensive JSON output
    nissan_data = {
        "oem": "Nissan",
        "zip_code": "multiple",
        "total_dealers_found": len(all_dealers),
        "method": "nissan_comprehensive_extraction",
        "zip_codes_searched": len(ZIP_CODES_TO_SEARCH),
        "extraction_date": datetime.now().isoformat(),
        "dealers": all_dealers
    }
    
    # Save to file
    with open("data/nissan.json", "w") as f:
        json.dump(nissan_data, f, indent=2)
    
    print(f"\n🎉 COMPREHENSIVE EXTRACTION COMPLETE!")
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
        for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {state}: {count} dealers")
    
    # Show sample dealer data
    if all_dealers:
        print(f"\n📝 Sample dealer data:")
        sample = all_dealers[0]
        print(f"  Name: {sample['Dealer']}")
        print(f"  Website: {sample['Website']}")
        print(f"  Phone: {sample['Phone']}")
        print(f"  Address: {sample['Street']}, {sample['City']}, {sample['State']} {sample['ZIP']}")

if __name__ == "__main__":
    asyncio.run(main())
