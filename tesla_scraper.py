#!/usr/bin/env python3
"""
Tesla Dealership Scraper
Scrapes all Tesla stores and galleries in the USA from the official Tesla website.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin

class TeslaDealershipScraper:
    def __init__(self):
        self.base_url = "https://www.tesla.com"
        self.stores_url = "https://www.tesla.com/findus/list/stores/United+States"
        self.dealerships = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def clean_phone_number(self, phone):
        """Clean and format phone number"""
        if not phone:
            return ""
        # Remove all non-digit characters except + and -
        phone = re.sub(r'[^\d+\-()]', '', phone)
        return phone.strip()

    def extract_coordinates_from_url(self, url):
        """Extract latitude and longitude from Tesla demo drive URL"""
        if not url:
            return None, None
        
        try:
            # Look for lat and lng parameters in the URL
            lat_match = re.search(r'lat=([\d.-]+)', url)
            lng_match = re.search(r'lng=([\d.-]+)', url)
            
            if lat_match and lng_match:
                return float(lat_match.group(1)), float(lng_match.group(1))
        except (ValueError, AttributeError):
            pass
        
        return None, None

    def scrape_dealerships(self):
        """Scrape all Tesla dealerships from the USA stores page"""
        print("Starting Tesla dealership scraping...")
        
        try:
            response = self.session.get(self.stores_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all state sections
            state_sections = soup.find_all('div', class_=lambda x: x and 'heading' in str(x))
            
            current_state = None
            dealership_count = 0
            
            # Process the page structure
            for element in soup.find_all(['h4', 'div']):
                if element.name == 'h4' and element.get_text().strip():
                    # This is a state heading
                    current_state = element.get_text().strip()
                    print(f"Processing state: {current_state}")
                
                elif element.name == 'div' and current_state:
                    # Look for dealership information in divs
                    dealership_info = self.extract_dealership_from_div(element, current_state)
                    if dealership_info:
                        self.dealerships.append(dealership_info)
                        dealership_count += 1
                        print(f"  Found dealership: {dealership_info['name']}")
            
            print(f"Scraping completed. Found {dealership_count} dealerships.")
            
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return False
        except Exception as e:
            print(f"Error during scraping: {e}")
            return False
        
        return True

    def extract_dealership_from_div(self, div, state):
        """Extract dealership information from a div element"""
        try:
            # Look for dealership name link
            name_link = div.find('a', href=lambda x: x and '/findus/location/store/' in x)
            if not name_link:
                return None
            
            name = name_link.get_text().strip()
            if not name or len(name) < 3:
                return None
            
            # Extract address information
            address_lines = []
            phone = ""
            demo_drive_url = ""
            
            # Look for address elements
            for child in div.find_all(['div', 'span']):
                text = child.get_text().strip()
                if text and not any(keyword in text.lower() for keyword in ['phone', 'schedule', 'demo', 'drive']):
                    # This might be an address line
                    if len(text) > 5 and not text.isdigit():
                        address_lines.append(text)
            
            # Look for phone number
            phone_link = div.find('a', href=lambda x: x and x.startswith('tel:'))
            if phone_link:
                phone = self.clean_phone_number(phone_link.get_text().strip())
            
            # Look for demo drive URL
            demo_link = div.find('a', href=lambda x: x and '/drive?' in x)
            if demo_link:
                demo_drive_url = demo_link.get('href')
            
            # Extract coordinates from demo drive URL
            lat, lng = self.extract_coordinates_from_url(demo_drive_url)
            
            # Clean up address
            address = ' '.join(address_lines).strip()
            
            # Extract city and zip from address
            city = ""
            zip_code = ""
            if address:
                # Try to extract city and zip
                parts = address.split(',')
                if len(parts) >= 2:
                    city = parts[-2].strip()
                    zip_part = parts[-1].strip()
                    # Extract zip code
                    zip_match = re.search(r'(\d{5}(?:-\d{4})?)', zip_part)
                    if zip_match:
                        zip_code = zip_match.group(1)
            
            dealership = {
                'name': name,
                'address': address,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'phone': phone,
                'latitude': lat,
                'longitude': lng,
                'demo_drive_url': demo_drive_url,
                'website_url': urljoin(self.base_url, name_link.get('href', ''))
            }
            
            return dealership
            
        except Exception as e:
            print(f"Error extracting dealership info: {e}")
            return None

    def save_to_json(self, filename):
        """Save dealerships data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.dealerships, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

    def get_statistics(self):
        """Get statistics about scraped data"""
        if not self.dealerships:
            return {}
        
        states = {}
        total_dealerships = len(self.dealerships)
        
        for dealership in self.dealerships:
            state = dealership.get('state', 'Unknown')
            states[state] = states.get(state, 0) + 1
        
        return {
            'total_dealerships': total_dealerships,
            'states_count': len(states),
            'dealerships_by_state': states
        }

def main():
    scraper = TeslaDealershipScraper()
    
    # Scrape dealerships
    if scraper.scrape_dealerships():
        # Save to JSON
        output_file = '/Users/kimseanpardo/autodealerships/tesla_dealerships_usa.json'
        if scraper.save_to_json(output_file):
            # Print statistics
            stats = scraper.get_statistics()
            print("\n" + "="*50)
            print("SCRAPING STATISTICS")
            print("="*50)
            print(f"Total dealerships found: {stats['total_dealerships']}")
            print(f"States covered: {stats['states_count']}")
            print("\nDealerships by state:")
            for state, count in sorted(stats['dealerships_by_state'].items()):
                print(f"  {state}: {count}")
        else:
            print("Failed to save data to JSON file")
    else:
        print("Failed to scrape dealership data")

if __name__ == "__main__":
    main()
