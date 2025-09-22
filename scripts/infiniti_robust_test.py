#!/usr/bin/env python3
"""
Robust Infiniti Dealer Locator Test
Handles timeouts and uses direct retailer locator URL
"""

import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def test_infiniti_retailer_locator():
    """Test the Infiniti retailer locator directly"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Set longer timeout
        page.set_default_timeout(60000)
        
        try:
            print("Navigating directly to Infiniti retailer locator...")
            
            # Try the direct retailer locator URL
            page.goto("https://www.infiniti.com/retailer-locator.html", 
                     wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            
            print("Taking screenshot of retailer locator page...")
            page.screenshot(path="infiniti_retailer_locator.png")
            
            # Look for the zip code input field
            print("Looking for zip code input field...")
            
            # Try multiple selectors for the zip input
            zip_input_selectors = [
                'input[name="predict-input"]',
                'input[placeholder*="Zip"]',
                'input[placeholder*="zip"]',
                'input[autocomplete="postal-code"]',
                'input[type="text"]',
                '.predict-input_field'
            ]
            
            zip_input = None
            for selector in zip_input_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        print(f"Found zip input with selector: {selector}")
                        zip_input = element
                        break
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            if not zip_input:
                print("Zip input not found, trying to find any input field...")
                all_inputs = page.locator('input')
                input_count = all_inputs.count()
                print(f"Found {input_count} input fields on the page")
                
                for i in range(input_count):
                    try:
                        input_elem = all_inputs.nth(i)
                        if input_elem.is_visible():
                            placeholder = input_elem.get_attribute('placeholder') or ''
                            input_type = input_elem.get_attribute('type') or ''
                            name = input_elem.get_attribute('name') or ''
                            print(f"Input {i}: placeholder='{placeholder}', type='{input_type}', name='{name}'")
                            
                            if 'zip' in placeholder.lower() or 'postal' in placeholder.lower():
                                zip_input = input_elem
                                print(f"Using input {i} as zip input")
                                break
                    except:
                        continue
            
            if zip_input:
                print("Testing zip code input with 90210...")
                zip_input.clear()
                zip_input.fill("90210")
                time.sleep(2)
                
                # Look for search button
                print("Looking for search button...")
                search_button_selectors = [
                    'button.predict-input_search-button',
                    'button[type="button"]',
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Search")',
                    '.predict-input_search-button'
                ]
                
                search_button = None
                for selector in search_button_selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible():
                            print(f"Found search button with selector: {selector}")
                            search_button = element
                            break
                    except Exception as e:
                        print(f"Search button selector {selector} failed: {e}")
                        continue
                
                if search_button:
                    print("Clicking search button...")
                    search_button.click()
                    time.sleep(5)
                else:
                    print("Search button not found, trying Enter key...")
                    zip_input.press("Enter")
                    time.sleep(5)
                
                print("Taking screenshot after search...")
                page.screenshot(path="infiniti_after_search.png")
                
                # Look for results
                print("Looking for dealer results...")
                dealers = extract_dealers_from_page(page)
                print(f"Found {len(dealers)} dealers")
                
                # Check for "See More" button
                print("Checking for 'See More' button...")
                see_more_found = check_see_more_button(page)
                
                # Save results
                save_test_results(dealers, see_more_found)
                
            else:
                print("Could not find zip code input field")
                page.screenshot(path="infiniti_no_zip_input.png")
            
        except PlaywrightTimeoutError as e:
            print(f"Timeout error: {e}")
            page.screenshot(path="infiniti_timeout_error.png")
        except Exception as e:
            print(f"Error during test: {e}")
            page.screenshot(path="infiniti_general_error.png")
        
        finally:
            browser.close()

def extract_dealers_from_page(page):
    """Extract dealer information from the current page"""
    dealers = []
    
    # Try multiple selectors for dealer elements
    dealer_selectors = [
        '.dealer-card',
        '.retailer-card',
        '.dealer-item',
        '.retailer-item',
        '.location-card',
        '.store-card',
        '[data-testid*="dealer"]',
        '[data-testid*="retailer"]',
        'div:has-text("Infiniti")'
    ]
    
    for selector in dealer_selectors:
        try:
            elements = page.locator(selector)
            count = elements.count()
            if count > 0:
                print(f"Found {count} elements with selector: {selector}")
                
                for i in range(count):
                    try:
                        element = elements.nth(i)
                        if element.is_visible():
                            dealer_info = {
                                'name': extract_text_from_element(element, [
                                    'h1', 'h2', 'h3', '.dealer-name', '.retailer-name',
                                    '.store-name', '.location-name'
                                ]),
                                'address': extract_text_from_element(element, [
                                    '.address', '.dealer-address', '.retailer-address',
                                    '.store-address', '.location-address'
                                ]),
                                'phone': extract_text_from_element(element, [
                                    '.phone', '.dealer-phone', '.retailer-phone',
                                    '.store-phone', '.location-phone', 'a[href^="tel:"]'
                                ]),
                                'website': extract_href_from_element(element, [
                                    'a[href*="infiniti"]', 'a[href*="dealer"]',
                                    '.website-link'
                                ])
                            }
                            
                            if dealer_info['name'] or dealer_info['address']:
                                dealers.append(dealer_info)
                                print(f"Extracted dealer: {dealer_info['name'] or 'Unknown'}")
                    except Exception as e:
                        print(f"Error extracting dealer {i}: {e}")
                        continue
                
                if dealers:
                    break
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
            continue
    
    return dealers

def extract_text_from_element(element, selectors):
    """Extract text from element using multiple selectors"""
    for selector in selectors:
        try:
            sub_element = element.locator(selector).first
            if sub_element.is_visible():
                text = sub_element.text_content().strip()
                if text:
                    return text
        except:
            continue
    return ""

def extract_href_from_element(element, selectors):
    """Extract href from element using multiple selectors"""
    for selector in selectors:
        try:
            sub_element = element.locator(selector).first
            if sub_element.is_visible():
                href = sub_element.get_attribute('href')
                if href:
                    return href
        except:
            continue
    return ""

def check_see_more_button(page):
    """Check if 'See More' button exists"""
    see_more_selectors = [
        'button:has-text("See More")',
        'a:has-text("See More")',
        '.see-more',
        '.load-more',
        '[data-testid*="see-more"]',
        '[data-testid*="load-more"]'
    ]
    
    for selector in see_more_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible():
                print(f"Found 'See More' button with selector: {selector}")
                return True
        except:
            continue
    
    print("No 'See More' button found")
    return False

def save_test_results(dealers, see_more_found):
    """Save test results to JSON file"""
    results = {
        "test_date": datetime.now().isoformat(),
        "dealers_found": len(dealers),
        "dealers": dealers,
        "see_more_button_found": see_more_found,
        "test_status": "completed"
    }
    
    with open("infiniti_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Test results saved to infiniti_test_results.json")

if __name__ == "__main__":
    test_infiniti_retailer_locator()
