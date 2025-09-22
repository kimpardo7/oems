#!/usr/bin/env python3
"""
Infiniti Dealer Locator Script
Searches for Infiniti dealers by zip code using their retailer locator
"""

import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class InfinitiDealerLocator:
    def __init__(self):
        self.base_url = "https://www.infiniti.com/retailer-locator.html"
        self.dealers = []
        self.processed_zips = set()
        
    def search_by_zip(self, zip_code, page):
        """Search for dealers by zip code"""
        try:
            print(f"Searching for dealers near zip code: {zip_code}")
            
            # Navigate to the retailer locator page
            page.goto(self.base_url, wait_until="networkidle")
            time.sleep(2)
            
            # Find and click the Retailer Locator menu item
            try:
                retailer_locator_button = page.locator('button[data-panel="Retailer_Locator"]')
                if retailer_locator_button.is_visible():
                    retailer_locator_button.click()
                    time.sleep(2)
            except Exception as e:
                print(f"Could not find/click Retailer Locator button: {e}")
            
            # Find the zip code input field
            zip_input = page.locator('input[name="predict-input"]')
            if not zip_input.is_visible():
                print("Zip code input field not found")
                return []
            
            # Clear and enter zip code
            zip_input.clear()
            zip_input.fill(str(zip_code))
            time.sleep(1)
            
            # Click the search button
            search_button = page.locator('button.predict-input_search-button')
            if search_button.is_visible():
                search_button.click()
                time.sleep(3)
            else:
                # Try pressing Enter if button not found
                zip_input.press("Enter")
                time.sleep(3)
            
            # Wait for results to load
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Extract dealer information
            dealers = self.extract_dealers(page, zip_code)
            
            # Check for "See More" button and handle pagination
            self.handle_see_more(page, zip_code)
            
            return dealers
            
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
            # Common selectors for dealer listings
            dealer_selectors = [
                '.dealer-card',
                '.retailer-card', 
                '.dealer-item',
                '.retailer-item',
                '[data-testid*="dealer"]',
                '[data-testid*="retailer"]',
                '.location-card',
                '.store-card'
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
                            'h1', 'h2', 'h3', '.dealer-name', '.retailer-name', 
                            '.store-name', '.location-name', '[data-testid*="name"]'
                        ]),
                        'address': self.extract_text_safely(dealer_element, [
                            '.address', '.dealer-address', '.retailer-address',
                            '.store-address', '.location-address', '[data-testid*="address"]'
                        ]),
                        'phone': self.extract_text_safely(dealer_element, [
                            '.phone', '.dealer-phone', '.retailer-phone',
                            '.store-phone', '.location-phone', '[data-testid*="phone"]',
                            'a[href^="tel:"]'
                        ]),
                        'website': self.extract_href_safely(dealer_element, [
                            'a[href*="infiniti"]', 'a[href*="dealer"]', 
                            '.website-link', '[data-testid*="website"]'
                        ]),
                        'distance': self.extract_text_safely(dealer_element, [
                            '.distance', '.dealer-distance', '.miles',
                            '[data-testid*="distance"]'
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
            # Look for "See More" button at the bottom
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
                    see_more_button = page.locator(selector)
                    if see_more_button.is_visible():
                        print(f"Found 'See More' button, clicking...")
                        see_more_button.click()
                        time.sleep(3)
                        
                        # Extract additional dealers
                        additional_dealers = self.extract_dealers(page, zip_code)
                        self.dealers.extend(additional_dealers)
                        print(f"Added {len(additional_dealers)} additional dealers")
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"Error handling 'See More': {e}")
    
    def search_multiple_zips(self, zip_codes):
        """Search for dealers using multiple zip codes"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
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
    
    locator = InfinitiDealerLocator()
    
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
