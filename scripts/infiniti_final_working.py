#!/usr/bin/env python3
"""
Infiniti Final Working Dealer Locator
Optimized version that handles timeouts and extracts results properly
"""

import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class InfinitiFinalLocator:
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
            
            # Click on the "Retailer Locator" button to open the panel
            print("Clicking on Retailer Locator button...")
            retailer_locator_button = page.locator('button[data-panel="Retailer_Locator"]')
            
            if retailer_locator_button.is_visible():
                retailer_locator_button.click()
                time.sleep(3)
                print("Retailer Locator panel opened")
                
                # Find and fill the zip code input
                zip_input = page.locator('input[name="predict-input"]')
                if zip_input.is_visible():
                    print("Entering zip code...")
                    zip_input.clear()
                    zip_input.fill(str(zip_code))
                    time.sleep(2)
                    
                    # Click the search button
                    search_button = page.locator('button.predict-input_search-button')
                    if search_button.is_visible():
                        print("Clicking search button...")
                        search_button.click()
                        
                        # Wait for results with a more reasonable timeout
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=15000)
                            time.sleep(3)
                        except PlaywrightTimeoutError:
                            print("Results taking longer to load, continuing...")
                            time.sleep(5)
                        
                        # Take screenshot of results
                        page.screenshot(path=f"infiniti_final_zip_{zip_code}_results.png")
                        
                        # Extract dealer information
                        dealers = self.extract_dealers(page, zip_code)
                        
                        # Check for "See More" button
                        self.handle_see_more(page, zip_code)
                        
                        return dealers
                    else:
                        print("Search button not found")
                        return []
                else:
                    print("Zip input not found")
                    return []
            else:
                print("Retailer Locator button not found")
                return []
            
        except Exception as e:
            print(f"Error searching zip code {zip_code}: {e}")
            return []
    
    def extract_dealers(self, page, zip_code):
        """Extract dealer information from the current page"""
        dealers = []
        
        try:
            print("Extracting dealer information...")
            
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
                '.retailer-info',
                '.dealer-info',
                '.dealer-listing',
                '.retailer-listing',
                '.dealer-result',
                '.retailer-result'
            ]
            
            dealer_elements = None
            for selector in dealer_selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    if count > 0:
                        dealer_elements = elements
                        print(f"Found {count} dealers using selector: {selector}")
                        break
                except:
                    continue
            
            if not dealer_elements:
                # Try to find any div that contains "Infiniti" text
                print("Trying to find dealer elements by text content...")
                dealer_elements = page.locator('div').filter(has_text='Infiniti')
                count = dealer_elements.count()
                if count > 0:
                    print(f"Found {count} potential dealer elements by text content")
                else:
                    print("No dealer elements found")
                    return dealers
            
            # Extract information from each dealer element
            for i in range(dealer_elements.count()):
                try:
                    dealer_element = dealer_elements.nth(i)
                    
                    # Get the full text content to analyze
                    full_text = dealer_element.text_content() or ""
                    
                    # Skip if the element doesn't seem to contain dealer info
                    if not any(keyword in full_text.lower() for keyword in ['infiniti', 'dealer', 'retailer', 'address', 'phone']):
                        continue
                    
                    # Extract dealer information
                    dealer_info = {
                        'zip_searched': zip_code,
                        'name': self.extract_text_safely(dealer_element, [
                            'h1', 'h2', 'h3', 'h4', '.dealer-name', '.retailer-name', 
                            '.store-name', '.location-name', '[data-testid*="name"]',
                            '.retailer-info h3', '.dealer-info h3', '.dealer-title',
                            '.retailer-title', '.dealer-title', '.retailer-title'
                        ]),
                        'address': self.extract_text_safely(dealer_element, [
                            '.address', '.dealer-address', '.retailer-address',
                            '.store-address', '.location-address', '[data-testid*="address"]',
                            '.retailer-address', '.dealer-address', '.dealer-location',
                            '.retailer-location', '.dealer-address-line', '.retailer-address-line'
                        ]),
                        'phone': self.extract_text_safely(dealer_element, [
                            '.phone', '.dealer-phone', '.retailer-phone',
                            '.store-phone', '.location-phone', '[data-testid*="phone"]',
                            'a[href^="tel:"]', '.retailer-phone', '.dealer-phone',
                            '.dealer-contact', '.retailer-contact', '.phone-number'
                        ]),
                        'website': self.extract_href_safely(dealer_element, [
                            'a[href*="infiniti"]', 'a[href*="dealer"]', 
                            '.website-link', '[data-testid*="website"]',
                            'a[href*="retailer"]', '.dealer-website', '.retailer-website'
                        ]),
                        'distance': self.extract_text_safely(dealer_element, [
                            '.distance', '.dealer-distance', '.miles',
                            '[data-testid*="distance"]', '.dealer-miles', '.retailer-miles'
                        ]),
                        'full_text': full_text[:200] + "..." if len(full_text) > 200 else full_text
                    }
                    
                    # Only add if we have meaningful information
                    if dealer_info['name'] or dealer_info['address'] or 'infiniti' in full_text.lower():
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
            
            # Look for "See More" button
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
        "60601",  # Chicago, IL
        "33101",  # Miami, FL
        "75201"   # Dallas, TX
    ]
    
    locator = InfinitiFinalLocator()
    
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
    
    # Print some sample results
    if dealers:
        print("\nSample dealers found:")
        for i, dealer in enumerate(dealers[:3]):
            print(f"{i+1}. {dealer.get('name', 'Unknown')} - {dealer.get('address', 'No address')}")

if __name__ == "__main__":
    main()
