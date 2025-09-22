#!/usr/bin/env python3
"""
Infiniti Improved Dealer Extraction
Focuses on proper extraction of dealer information and testing multiple zip codes
"""

import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class InfinitiImprovedExtractor:
    def __init__(self):
        self.base_url = "https://www.infinitiusa.com"
        self.dealers = []
        self.processed_zips = set()
        
    def search_single_zip(self, zip_code, page):
        """Search for dealers by a single zip code"""
        try:
            print(f"\n=== Searching for dealers near zip code: {zip_code} ===")
            
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
                        
                        # Wait for results
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=15000)
                            time.sleep(3)
                        except PlaywrightTimeoutError:
                            print("Results taking longer to load, continuing...")
                            time.sleep(5)
                        
                        # Take screenshot of results
                        page.screenshot(path=f"infiniti_improved_zip_{zip_code}_results.png")
                        
                        # Extract dealer information with better logic
                        dealers = self.extract_dealers_improved(page, zip_code)
                        
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
    
    def extract_dealers_improved(self, page, zip_code):
        """Improved dealer extraction with better filtering"""
        dealers = []
        
        try:
            print("Extracting dealer information with improved logic...")
            
            # First, try to find specific dealer result containers
            dealer_selectors = [
                '.dealer-result',
                '.retailer-result',
                '.dealer-card',
                '.retailer-card',
                '.dealer-item',
                '.retailer-item',
                '.location-card',
                '.store-card',
                '[data-testid*="dealer"]',
                '[data-testid*="retailer"]'
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
                # If no specific dealer containers found, look for any div with dealer-like content
                print("No specific dealer containers found, looking for dealer-like content...")
                
                # Get all divs and filter for those that might contain dealer info
                all_divs = page.locator('div')
                div_count = all_divs.count()
                print(f"Checking {div_count} div elements for dealer content...")
                
                potential_dealers = []
                for i in range(min(div_count, 100)):  # Limit to first 100 divs for performance
                    try:
                        div = all_divs.nth(i)
                        if div.is_visible():
                            text = div.text_content() or ""
                            
                            # Check if this div contains dealer-like information
                            if self.is_dealer_content(text):
                                potential_dealers.append(div)
                                if len(potential_dealers) >= 10:  # Limit to 10 potential dealers
                                    break
                    except:
                        continue
                
                if potential_dealers:
                    print(f"Found {len(potential_dealers)} potential dealer divs")
                    dealer_elements = potential_dealers
                else:
                    print("No dealer content found")
                    return dealers
            
            # Extract information from each dealer element
            for i in range(len(dealer_elements)):
                try:
                    dealer_element = dealer_elements[i]
                    full_text = dealer_element.text_content() or ""
                    
                    # Skip if text is too short or doesn't contain relevant info
                    if len(full_text.strip()) < 20:
                        continue
                    
                    # Extract dealer information
                    dealer_info = self.extract_dealer_info(dealer_element, zip_code, full_text)
                    
                    # Only add if we have meaningful information
                    if dealer_info and (dealer_info.get('name') or dealer_info.get('address')):
                        dealers.append(dealer_info)
                        print(f"Extracted dealer: {dealer_info.get('name', 'Unknown')} - {dealer_info.get('address', 'No address')}")
                    
                except Exception as e:
                    print(f"Error extracting dealer {i}: {e}")
                    continue
            
            print(f"Successfully extracted {len(dealers)} dealers for zip code {zip_code}")
            return dealers
            
        except Exception as e:
            print(f"Error extracting dealers: {e}")
            return dealers
    
    def is_dealer_content(self, text):
        """Check if text content looks like dealer information"""
        if not text or len(text.strip()) < 20:
            return False
        
        text_lower = text.lower()
        
        # Look for dealer-related keywords
        dealer_keywords = ['infiniti', 'dealer', 'retailer', 'automotive', 'cars', 'vehicles']
        address_keywords = ['street', 'avenue', 'road', 'drive', 'boulevard', 'way', 'lane']
        contact_keywords = ['phone', 'tel', 'call', 'contact']
        
        # Check if text contains dealer-related content
        has_dealer_keyword = any(keyword in text_lower for keyword in dealer_keywords)
        has_address_keyword = any(keyword in text_lower for keyword in address_keywords)
        has_contact_keyword = any(keyword in text_lower for keyword in contact_keywords)
        
        # Must have at least one dealer keyword and either address or contact info
        return has_dealer_keyword and (has_address_keyword or has_contact_keyword)
    
    def extract_dealer_info(self, element, zip_code, full_text):
        """Extract dealer information from an element"""
        try:
            # Try to extract name from headings
            name = ""
            name_selectors = ['h1', 'h2', 'h3', 'h4', '.dealer-name', '.retailer-name', '.store-name']
            for selector in name_selectors:
                try:
                    name_elem = element.locator(selector).first
                    if name_elem.is_visible():
                        name = name_elem.text_content().strip()
                        if name and len(name) > 3:
                            break
                except:
                    continue
            
            # If no name found in headings, try to extract from full text
            if not name:
                lines = full_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and any(keyword in line.lower() for keyword in ['infiniti', 'dealer', 'retailer']):
                        name = line
                        break
            
            # Extract address
            address = ""
            address_selectors = ['.address', '.dealer-address', '.retailer-address', '.location-address']
            for selector in address_selectors:
                try:
                    addr_elem = element.locator(selector).first
                    if addr_elem.is_visible():
                        address = addr_elem.text_content().strip()
                        if address:
                            break
                except:
                    continue
            
            # If no address found in specific selectors, try to extract from full text
            if not address:
                lines = full_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and any(keyword in line.lower() for keyword in ['street', 'avenue', 'road', 'drive', 'boulevard']):
                        address = line
                        break
            
            # Extract phone
            phone = ""
            phone_selectors = ['.phone', '.dealer-phone', '.retailer-phone', 'a[href^="tel:"]']
            for selector in phone_selectors:
                try:
                    phone_elem = element.locator(selector).first
                    if phone_elem.is_visible():
                        phone = phone_elem.text_content().strip()
                        if phone:
                            break
                except:
                    continue
            
            # Extract website
            website = ""
            try:
                website_elem = element.locator('a[href*="infiniti"], a[href*="dealer"]').first
                if website_elem.is_visible():
                    website = website_elem.get_attribute('href')
            except:
                pass
            
            return {
                'zip_searched': zip_code,
                'name': name,
                'address': address,
                'phone': phone,
                'website': website,
                'full_text_preview': full_text[:100] + "..." if len(full_text) > 100 else full_text
            }
            
        except Exception as e:
            print(f"Error extracting dealer info: {e}")
            return None
    
    def handle_see_more(self, page, zip_code):
        """Handle 'See More' button to load additional dealers"""
        try:
            print("Checking for 'See More' button...")
            
            see_more_selectors = [
                'button:has-text("See More")',
                'a:has-text("See More")',
                '.see-more',
                '.load-more',
                'button:has-text("Load More")',
                'a:has-text("Load More")'
            ]
            
            for selector in see_more_selectors:
                try:
                    see_more_button = page.locator(selector)
                    if see_more_button.is_visible():
                        print(f"Found 'See More' button, clicking...")
                        see_more_button.click()
                        time.sleep(3)
                        
                        # Extract additional dealers
                        additional_dealers = self.extract_dealers_improved(page, zip_code)
                        self.dealers.extend(additional_dealers)
                        print(f"Added {len(additional_dealers)} additional dealers")
                        break
                except:
                    continue
            else:
                print("No 'See More' button found")
                    
        except Exception as e:
            print(f"Error handling 'See More': {e}")
    
    def test_multiple_zips(self, zip_codes):
        """Test with multiple zip codes to ensure variety"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.set_default_timeout(60000)
            
            try:
                for zip_code in zip_codes:
                    if zip_code in self.processed_zips:
                        print(f"Zip code {zip_code} already processed, skipping...")
                        continue
                    
                    dealers = self.search_single_zip(zip_code, page)
                    self.dealers.extend(dealers)
                    self.processed_zips.add(zip_code)
                    
                    print(f"Total dealers found so far: {len(self.dealers)}")
                    
                    # Random delay between searches
                    time.sleep(random.uniform(3, 5))
                    
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
    """Main function to test with different zip codes"""
    # Test with different zip codes from different regions
    test_zips = [
        "90210",  # Beverly Hills, CA
        "10001",  # New York, NY
        "60601",  # Chicago, IL
        "33101",  # Miami, FL
        "75201",  # Dallas, TX
        "98101",  # Seattle, WA
        "30301",  # Atlanta, GA
        "80201"   # Denver, CO
    ]
    
    extractor = InfinitiImprovedExtractor()
    
    print("Starting Infiniti dealer search with improved extraction...")
    dealers = extractor.test_multiple_zips(test_zips)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Found {len(dealers)} total dealers")
    extractor.save_to_json()
    
    # Print summary by zip code
    zip_summary = {}
    for dealer in dealers:
        zip_code = dealer.get('zip_searched', 'Unknown')
        if zip_code not in zip_summary:
            zip_summary[zip_code] = 0
        zip_summary[zip_code] += 1
    
    print(f"\nDealers found by zip code:")
    for zip_code, count in zip_summary.items():
        print(f"  {zip_code}: {count} dealers")
    
    # Print some sample results
    if dealers:
        print(f"\nSample dealers found:")
        for i, dealer in enumerate(dealers[:5]):
            print(f"{i+1}. {dealer.get('name', 'Unknown')} - {dealer.get('address', 'No address')}")

if __name__ == "__main__":
    main()
