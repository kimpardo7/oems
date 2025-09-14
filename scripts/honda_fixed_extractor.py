#!/usr/bin/env python3
"""
Fixed Honda Dealer Extractor using Playwright
Uses correct selectors based on actual page structure
"""

import asyncio
import json
from playwright.async_api import async_playwright
import time

async def extract_honda_dealers(zip_code):
    """Extract Honda dealers for a given ZIP code using correct selectors"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print(f"Navigating to Honda dealer finder for ZIP: {zip_code}")
            
            # Navigate to Honda dealer finder
            await page.goto("https://automobiles.honda.com/dealer-locator")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            print(f"Page loaded: {page.url}")
            
            # Check if we're on the correct page
            page_title = await page.title()
            print(f"Page title: {page_title}")
            
            # Look for the ZIP code input field using the correct selector
            zip_input = await page.wait_for_selector('input[placeholder="ZIP Code"]', timeout=10000)
            if zip_input:
                print("✓ Found ZIP code input field")
                
                # Clear and enter ZIP code
                await zip_input.clear()
                await zip_input.fill(zip_code)
                print(f"✓ Entered ZIP code: {zip_code}")
                
                # Find and click the search button
                search_button = await page.query_selector('button[type="submit"]')
                if search_button:
                    print("✓ Found search button")
                    await search_button.click()
                    print("✓ Clicked search button")
                    
                    # Wait for results to load
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(3)
                    
                    # Extract dealer information
                    dealers = await extract_dealer_info(page)
                    return dealers
                else:
                    print("✗ Search button not found")
                    return []
            else:
                print("✗ ZIP code input field not found")
                return []
                
        except Exception as e:
            print(f"Error during extraction: {e}")
            return []
        finally:
            await browser.close()

async def extract_dealer_info(page):
    """Extract dealer information from the results page"""
    dealers = []
    
    try:
        print("Extracting dealer information...")
        
        # Wait for dealer cards to load
        await page.wait_for_selector('[data-testid="dealer-card"]', timeout=15000)
        
        # Find all dealer cards
        dealer_cards = await page.query_selector_all('[data-testid="dealer-card"]')
        print(f"Found {len(dealer_cards)} dealer cards")
        
        for card in dealer_cards:
            try:
                # Extract dealer name
                name_element = await card.query_selector('[data-testid="dealer-name"]')
                name = await name_element.inner_text() if name_element else "Unknown"
                
                # Extract address
                address_element = await card.query_selector('[data-testid="dealer-address"]')
                address_text = await address_element.inner_text() if address_element else ""
                
                # Extract phone
                phone_element = await card.query_selector('[data-testid="dealer-phone"]')
                phone = await phone_element.inner_text() if phone_element else ""
                
                # Extract website
                website_element = await card.query_selector('[data-testid="dealer-website"] a')
                website = await website_element.get_attribute('href') if website_element else ""
                
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
                print(f"  Extracted: {name}")
                
            except Exception as e:
                print(f"  Error extracting dealer card: {e}")
                continue
                
    except Exception as e:
        print(f"Error extracting dealers from page: {e}")
        # Try alternative selectors if the main ones fail
        try:
            print("Trying alternative selectors...")
            
            # Look for any dealer-like elements
            dealer_elements = await page.query_selector_all('.dealer, .dealership, [class*="dealer"], [class*="dealership"]')
            print(f"Found {len(dealer_elements)} dealer elements with alternative selectors")
            
            for element in dealer_elements:
                try:
                    # Try to extract basic info
                    text_content = await element.inner_text()
                    if text_content and len(text_content.strip()) > 10:
                        dealer = {
                            "Dealer": "Unknown",
                            "Website": "",
                            "Phone": "",
                            "Email": "",
                            "Street": "",
                            "City": "",
                            "State": "",
                            "ZIP": "",
                            "Raw_Content": text_content.strip()
                        }
                        dealers.append(dealer)
                        print(f"  Extracted raw content: {text_content[:50]}...")
                except Exception as e:
                    print(f"  Error extracting alternative element: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error with alternative extraction: {e}")
    
    return dealers

async def test_extraction():
    """Test the extraction with a sample ZIP code"""
    zip_code = "90210"  # Beverly Hills
    print(f"Testing Honda dealer extraction for ZIP: {zip_code}")
    
    dealers = await extract_honda_dealers(zip_code)
    
    print(f"\nExtraction Results:")
    print(f"Found {len(dealers)} dealers")
    
    for i, dealer in enumerate(dealers, 1):
        print(f"\n{i}. {dealer['Dealer']}")
        print(f"   Address: {dealer['Street']}, {dealer['City']}, {dealer['State']} {dealer['ZIP']}")
        print(f"   Phone: {dealer['Phone']}")
        print(f"   Website: {dealer['Website']}")
        if 'Raw_Content' in dealer:
            print(f"   Raw Content: {dealer['Raw_Content'][:100]}...")
    
    # Save results
    output_file = f"honda_test_results_{zip_code}.json"
    with open(output_file, 'w') as f:
        json.dump(dealers, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(test_extraction())
