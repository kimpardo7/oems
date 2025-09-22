#!/usr/bin/env python3
"""
Infiniti Working Dealer Locator
Based on debug findings - clicks Retailer Locator button first, then searches by zip
"""

import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class InfinitiWorkingLocator:
    def __init__(self):
        self.base_url = "https://www.infinitiusa.com"
        self.dealers = []
        self.processed_zips = set()
        
    def search_by_zip(self, zip_code, page):
        """Search for dealers by zip code"""
        try:
            print(f"Searching for dealers near zip code: {zip_code}")
            
            # Navigate to the main Infiniti page
            page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)
            
            # Take screenshot of initial page
            page.screenshot(path=f"infiniti_working_zip_{zip_code}_initial.png")
            
            # Click on the "Retailer Locator" button to open the panel
            print("Clicking on Retailer Locator button...")
            retailer_locator_button = page.locator('button[data-panel="Retailer_Locator"]')
            
            if retailer_locator_button.is_visible():
                retailer_locator_button.click()
                time.sleep(3)
                print("Retailer Locator panel opened")
                
                # Take screenshot after opening panel
                page.screenshot(path=f"infiniti_working_zip_{zip_code}_panel_opened.png")
                
                # Now look for the zip code input field in the opened panel
                zip_input = None
                zip_selectors = [
                    'input[name="predict-input"]',
                    'input[placeholder*="Zip"]',
                    'input[placeholder*="zip"]',
                    'input[autocomplete="postal-code"]',
                    '.predict-input_field',
                    'input[type="text"]'
                ]
                
                for selector in zip_selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible():
                            print(f"Found zip input with selector: {selector}")
                            zip_input = element
                            break
                    except:
                        continue
                
                if not zip_input:
                    print("Zip input not found in panel, trying alternative approach...")
                    # Try to find any input field that might be for zip codes
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
                                
                                if any(keyword in placeholder.lower() for keyword in ['zip', 'postal', 'code']):
                                    zip_input = input_elem
                                    print(f"Using input {i} as zip input")
                                    break
                        except:
                            continue
                
                if zip_input:
                    print("Entering zip code...")
                    zip_input.clear()
                    zip_input.fill(str(zip_code))
                    time.sleep(2)
                    
                    # Take screenshot after entering zip code
                    page.screenshot(path=f"infiniti_working_zip_{zip_code}_after_typing.png")
                    
                    # Click the search button
                    search_button = None
                    search_selectors = [
                        'button.predict-input_search-button',
                        'button[type="button"]',
                        'button[type="submit"]',
                        'input[type="submit"]',
                        'button:has-text("Search")',
                        '.predict-input_search-button',
                        'button[aria-label*="Enter your Zip Code"]'
                    ]
                    
                    for selector in search_selectors:
                        try:
                            element = page.locator(selector).first
                            if element.is_visible():
                                print(f"Found search button with selector: {selector}")
                                search_button = element
                                break
                        except:
                            continue
                    
                    if search_button:
                        print("Clicking search button...")
                        search_button.click()
                        time.sleep(5)
                    else:
                        print("Search button not found, trying Enter key...")
                        zip_input.press("Enter")
                        time.sleep(5)
                    
                    # Wait for results to load
                    page.wait_for_load_state("networkidle", timeout=30000)
                    time.sleep(2)
                    
                    # Take screenshot after search
                    page.screenshot(path=f"infiniti_working_zip_{zip_code}_after_search.png")
                    
                    # Extract dealer information
                    dealers = self.extract_dealers(page, zip_code)
                    
                    # Check for "See More" button and handle pagination
                    self.handle_see_more(page, zip_code)
                    
                    return dealers
                else:
                    print("Could not find zip code input field in the panel")
                    return []
            else:
                print("Retailer Locator button not found or not visible")
                return []
            
        except PlaywrightTimeoutError:
            print(f"Timeout while searching zip code {zip_code}")
            return []
        except Exception as e:
            print(f"Error searching zip code {zip_code}: {e}")
            return []
    
    def extract_dealers(self, page, zip_code):
        """Extract dealer information from the current page"""
        dealers = []
        
        try:
            # Look for dealer cards/containers
            dealer_selectors = [
                '.dealer-card',
                '.retailer-card', 
                '.dealer-item',
                '.retailer-item',
                '.location-card',
                '.store-card',
                '[data-testid*="dealer"]',
                '[data-testid*="retailer"]',
                '.retailer-info',
                '.dealer-info',
                '.dealer-listing',
                '.retailer-listing'
            ]
            
            dealer_elements = None
            for selector in dealer_selectors:
                elements = page.locator(selector)
                if elements.count() > 0:
                    dealer_elements = elements
                    print(f"Found {elements.count()} dealers using selector: {selector}")
                    break
            
            if not dealer_elements:
                # Try to find any elements that might contain dealer info
                dealer_elements = page.locator('div').filter(has_text='Infiniti')
                if dealer_elements.count() > 0:
                    print(f"Found {dealer_elements.count()} potential dealer elements")
                else:
                    print("No dealer elements found")
                    return dealers
            
            # Extract information from each dealer element
            for i in range(dealer_elements.count()):
                try:
                    dealer_element = dealer_elements.nth(i)
                    
                    # Extract dealer information
                    dealer_info = {
                        'zip_searched': zip_code,
                        'name': self.extract_text_safely(dealer_element, [
                            'h1', 'h2', 'h3', 'h4', '.dealer-name', '.retailer-name', 
                            '.store-name', '.location-name', '[data-testid*="name"]',
                            '.retailer-info h3', '.dealer-info h3', '.dealer-title',
                            '.retailer-title'
                        ]),
                        'address': self.extract_text_safely(dealer_element, [
                            '.address', '.dealer-address', '.retailer-address',
                            '.store-address', '.location-address', '[data-testid*="address"]',
                            '.retailer-address', '.dealer-address', '.dealer-location',
                            '.retailer-location'
                        ]),
                        'phone': self.extract_text_safely(dealer_element, [
                            '.phone', '.dealer-phone', '.retailer-phone',
                            '.store-phone', '.location-phone', '[data-testid*="phone"]',
                            'a[href^="tel:"]', '.retailer-phone', '.dealer-phone',
                            '.dealer-contact', '.retailer-contact'
                        ]),
                        'website': self.extract_href_safely(dealer_element, [
                            'a[href*="infiniti"]', 'a[href*="dealer"]', 
                            '.website-link', '[data-testid*="website"]',
                            'a[href*="retailer"]', '.dealer-website', '.retailer-website'
                        ]),
                        'distance': self.extract_text_safely(dealer_element, [
                            '.distance', '.dealer-distance', '.miles',
                            '[data-testid*="distance"]', '.dealer-miles', '.retailer-miles'
                        ])
                    }
                    
                    # Only add if we have at least a name or address
                    if dealer_info['name'] or dealer_info['address']:
                        dealers.append(dealer_info)
                        print(f"Extracted dealer: {dealer_info['name'] or 'Unknown'}")
                    
                except Exception as e:
                    print(f"Error extracting dealer {i}: {e}")
                    continue
            
            print(f"Extracted {len(dealers)} dealers for zip code {zip_code}")
            return dealers
            
        except Exception as e:
            print(f"Error extracting dealers: {e}")
            return dealers
    
    def extract_text_safely(self, element, selectors):
        """Safely extract text from element using multiple selectors"""
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
    
    def extract_href_safely(self, element, selectors):
        """Safely extract href from element using multiple selectors"""
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
    
    def handle_see_more(self, page, zip_code):
        """Handle 'See More' button to load additional dealers"""
        try:
            print("Checking for 'See More' button...")
            # Look for "See More" button at the bottom
            see_more_selectors = [
                'button:has-text("See More")',
                'a:has-text("See More")',
                '.see-more',
                '.load-more',
                '[data-testid*="see-more"]',
                '[data-testid*="load-more"]',
                'button:has-text("Load More")',
                'a:has-text("Load More")',
                'button:has-text("Show More")',
                'a:has-text("Show More")'
            ]
            
            for selector in see_more_selectors:
                try:
                    see_more_button = page.locator(selector)
                    if see_more_button.is_visible():
                        print(f"Found 'See More' button with selector: {selector}, clicking...")
                        see_more_button.click()
                        time.sleep(3)
                        
                        # Take screenshot after clicking See More
                        page.screenshot(path=f"infiniti_working_zip_{zip_code}_after_see_more.png")
                        
                        # Extract additional dealers
                        additional_dealers = self.extract_dealers(page, zip_code)
                        self.dealers.extend(additional_dealers)
                        print(f"Added {len(additional_dealers)} additional dealers")
                        break
                except:
                    continue
            else:
                print("No 'See More' button found")
                    
        except Exception as e:
            print(f"Error handling 'See More': {e}")
    
    def search_multiple_zips(self, zip_codes):
        """Search for dealers using multiple zip codes"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.set_default_timeout(60000)
            
            try:
                for zip_code in zip_codes:
                    if zip_code in self.processed_zips:
                        print(f"Zip code {zip_code} already processed, skipping...")
                        continue
                    
                    dealers = self.search_by_zip(zip_code, page)
                    self.dealers.extend(dealers)
                    self.processed_zips.add(zip_code)
                    
                    # Random delay between searches
                    time.sleep(random.uniform(2, 4))
                    
            finally:
                browser.close()
        
        return self.dealers
    
    def save_to_json(self, filename="Infiniti.json"):
        """Save dealers to JSON file"""
        data = {
            "brand": "Infiniti",
            "dealers": self.dealers,
            "last_updated": datetime.now().isoformat(),
            "total_dealers": len(self.dealers),
            "search_method": "zip_code_locator",
            "source_url": self.base_url
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(self.dealers)} dealers to {filename}")

def main():
    """Main function to run the Infiniti dealer locator"""
    # Sample zip codes for testing
    test_zips = [
        "90210",  # Beverly Hills, CA
        "10001",  # New York, NY
    ]
    
    locator = InfinitiWorkingLocator()
    
    print("Starting Infiniti dealer search...")
    dealers = locator.search_multiple_zips(test_zips)
    
    print(f"\nFound {len(dealers)} total dealers")
    locator.save_to_json()
    
    # Print summary
    unique_dealers = {}
    for dealer in dealers:
        key = f"{dealer.get('name', '')}-{dealer.get('address', '')}"
        if key not in unique_dealers:
            unique_dealers[key] = dealer
    
    print(f"Unique dealers found: {len(unique_dealers)}")

if __name__ == "__main__":
    main()
