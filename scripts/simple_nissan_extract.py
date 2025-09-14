#!/usr/bin/env python3
"""
Simple Nissan dealer extraction - just extract from current page
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def extract_nissan_dealers():
    """Extract Nissan dealers from the current page"""
    print("🚗 Starting simple Nissan dealer extraction...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        try:
            # Navigate to Nissan dealer locator
            await page.goto("https://www.nissanusa.com/dealer-locator.html", timeout=60000)
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # Find and enter ZIP code
            search_input = await page.query_selector('input.sc-b09ff0c6-2.goQJlr.pac-target-input')
            if search_input:
                await search_input.click()
                await search_input.fill("90210")
                print("✅ Entered ZIP code: 90210")
                
                # Click search button
                search_button = await page.query_selector('button.sc-b09ff0c6-3.erAepT')
                if search_button:
                    await search_button.click()
                    print("✅ Clicked search button")
                    
                    # Wait for results
                    await page.wait_for_timeout(5000)
                    
                    # Extract dealers
                    dealer_cards = await page.query_selector_all('div.sc-536f716-2.eGBXOP')
                    print(f"✅ Found {len(dealer_cards)} dealer cards")
                    
                    dealers = []
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
                            
                            # Parse address
                            address_parts = address_text.split(',') if address_text else []
                            street = address_parts[0].strip() if len(address_parts) > 0 else ""
                            city_state_zip = address_parts[1].strip() if len(address_parts) > 1 else ""
                            
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
                            print(f"  ❌ Error extracting dealer: {e}")
                            continue
                    
                    # Save to JSON
                    nissan_data = {
                        "oem": "Nissan",
                        "zip_code": "90210",
                        "total_dealers_found": len(dealers),
                        "method": "nissan_simple_extraction",
                        "extraction_date": datetime.now().isoformat(),
                        "dealers": dealers
                    }
                    
                    with open("data/nissan.json", "w") as f:
                        json.dump(nissan_data, f, indent=2)
                    
                    print(f"\n🎉 Extraction complete!")
                    print(f"📊 Total dealers found: {len(dealers)}")
                    print(f"💾 Data saved to: data/nissan.json")
                    
                    # Show sample data
                    if dealers:
                        print(f"\n📝 Sample dealer data:")
                        sample = dealers[0]
                        print(f"  Name: {sample['Dealer']}")
                        print(f"  Website: {sample['Website']}")
                        print(f"  Phone: {sample['Phone']}")
                        print(f"  Address: {sample['Street']}, {sample['City']}, {sample['State']} {sample['ZIP']}")
                
                else:
                    print("❌ Could not find search button")
            else:
                print("❌ Could not find search input")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(extract_nissan_dealers())
