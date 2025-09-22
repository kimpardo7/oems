#!/usr/bin/env python3
"""
Lexus Dealer Scraper
Scrapes all Lexus dealers from all 50 US states
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# List of all 50 US states
STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
]

def extract_dealer_data(page):
    """Extract dealer data from the current page"""
    dealers = []
    
    # Wait for dealer results to load
    page.wait_for_selector('[data-testid="DealerCard"]', timeout=10000)
    
    # Get all dealer cards
    dealer_cards = page.query_selector_all('[data-testid="DealerCard"]')
    
    for card in dealer_cards:
        try:
            dealer = {}
            
            # Dealer name
            name_elem = card.query_selector('[data-testid="Typography"]')
            if name_elem:
                dealer['name'] = name_elem.inner_text().strip()
            
            # Address
            address_elem = card.query_selector('.sc-bETbji')
            if address_elem:
                address_lines = address_elem.query_selector_all('div')
                if len(address_lines) >= 2:
                    dealer['address'] = address_lines[0].inner_text().strip()
                    dealer['city_state_zip'] = address_lines[1].inner_text().strip()
            
            # Phone number
            phone_elem = card.query_selector('a[href^="tel:"]')
            if phone_elem:
                dealer['phone'] = phone_elem.inner_text().strip()
            
            # Hours
            hours_list = card.query_selector('ul.sc-bsOfxk')
            if hours_list:
                hours = []
                hour_items = hours_list.query_selector_all('li')
                for item in hour_items:
                    day_elem = item.query_selector('div:first-child')
                    time_elem = item.query_selector('div:last-child')
                    if day_elem and time_elem:
                        hours.append(f"{day_elem.inner_text().strip()} {time_elem.inner_text().strip()}")
                dealer['hours'] = hours
            
            # Badges
            badges = []
            
            # Elite Dealer badge
            elite_elem = card.query_selector('[data-testid="Typography"]:has-text("Elite Dealer")')
            if elite_elem:
                badges.append("Elite Dealer")
            
            # Monogram badge
            monogram_elem = card.query_selector('[data-testid="MonogramDealerBadge"]')
            if monogram_elem:
                badges.append("Monogram")
            
            # Collision Center badge
            collision_elem = card.query_selector('[data-testid="CollisionCenterBadge"]')
            if collision_elem:
                badges.append("Certified Collision Center")
            
            dealer['badges'] = badges
            
            # Links
            links = {}
            
            # Dealer details link
            details_elem = card.query_selector('a[href*="/dealers/"]')
            if details_elem:
                links['dealer_details'] = details_elem.get_attribute('href')
            
            # Dealer website
            website_elem = card.query_selector('a[href*="lexus"]:not([href*="/dealers/"])')
            if website_elem:
                links['website'] = website_elem.get_attribute('href')
            
            # Service link
            service_elem = card.query_selector('a:has-text("SCHEDULE SERVICE")')
            if service_elem:
                links['service'] = service_elem.get_attribute('href')
            
            # Contact link
            contact_elem = card.query_selector('a:has-text("CONTACT DEALER")')
            if contact_elem:
                links['contact'] = contact_elem.get_attribute('href')
            
            dealer['links'] = links
            
            dealers.append(dealer)
            
        except Exception as e:
            print(f"Error extracting dealer data: {e}")
            continue
    
    return dealers

def scrape_lexus_dealers():
    """Main function to scrape all Lexus dealers"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to Lexus dealer page
            print("Navigating to Lexus dealer page...")
            page.goto("https://www.lexus.com/dealers")
            
            # Wait for page to load
            page.wait_for_load_state("networkidle")
            
            # Click on STATE tab
            print("Clicking on STATE tab...")
            page.click('[role="tab"]:has-text("STATE")')
            
            # Wait for state dropdown to be available
            page.wait_for_selector('[role="combobox"][aria-label="STATE"]')
            
            all_dealers = {}
            total_dealers = 0
            
            for i, state in enumerate(STATES, 1):
                print(f"Processing {state} ({i}/50)...")
                
                try:
                    # Click on state dropdown
                    page.click('[role="combobox"][aria-label="STATE"]')
                    
                    # Wait for dropdown options
                    page.wait_for_selector('[role="option"]')
                    
                    # Click on the state option
                    page.click(f'[role="option"]:has-text("{state}")')
                    
                    # Wait for results to load
                    page.wait_for_selector('[data-testid="DealerCard"]', timeout=15000)
                    
                    # Extract dealer data
                    dealers = extract_dealer_data(page)
                    
                    if dealers:
                        all_dealers[state] = dealers
                        total_dealers += len(dealers)
                        print(f"  Found {len(dealers)} dealers in {state}")
                    else:
                        print(f"  No dealers found in {state}")
                        all_dealers[state] = []
                    
                    # Small delay between states
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  Error processing {state}: {e}")
                    all_dealers[state] = []
                    continue
            
            # Create final data structure
            result = {
                "brand": "Lexus",
                "scraped_date": datetime.now().isoformat(),
                "total_dealers": total_dealers,
                "states": all_dealers
            }
            
            # Save to JSON file
            output_file = "/Users/kimseanpardo/autodealerships/Lexus.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\nScraping completed!")
            print(f"Total dealers found: {total_dealers}")
            print(f"Data saved to: {output_file}")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_lexus_dealers()
