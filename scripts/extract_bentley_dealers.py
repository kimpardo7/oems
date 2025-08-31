#!/usr/bin/env python3
"""
Script to extract Bentley dealer information from HTML and convert to JSON format.
"""

import re
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def extract_dealer_info(html_content: str) -> List[Dict[str, Any]]:
    """
    Extract dealer information from Bentley HTML content.
    
    Args:
        html_content: Raw HTML content from bentily.txt
        
    Returns:
        List of dealer dictionaries
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    dealers = []
    
    # Find all button elements that contain dealer headers
    dealer_buttons = soup.find_all('button', class_='dl-e-accordion__header-wrapper')
    
    for button in dealer_buttons:
        dealer_info = {}
        
        # Extract dealer name
        name_element = button.find('div', class_='dl-m-dealer-locator__dealer-accordion__header-name')
        if name_element:
            dealer_info['Dealer'] = name_element.get_text(strip=True)
        
        # Find the corresponding content section for this dealer
        # The content follows the button in the same accordion
        content_section = button.find_next_sibling('div', class_='dl-e-accordion__content')
        if content_section:
            # Extract address information
            address_container = content_section.find('div', class_='dl-m-dealer-locator__dealer-details__address')
            if address_container:
                address_parts = []
                address_elements = address_container.find_all('p', class_='bm-desc--large')
                for elem in address_elements:
                    text = elem.get_text(strip=True)
                    if text:
                        address_parts.append(text)
                
                # Parse address parts
                if len(address_parts) >= 3:
                    dealer_info['Street'] = address_parts[0] if address_parts[0] else ''
                    dealer_info['City'] = address_parts[1] if len(address_parts) > 1 and address_parts[1] else ''
                    dealer_info['State'] = ''  # Bentley doesn't show state separately
                    dealer_info['ZIP'] = address_parts[2] if len(address_parts) > 2 else ''
            
            # Extract phone number
            phone_link = content_section.find('a', href=re.compile(r'^tel:'))
            if phone_link:
                phone_text = phone_link.get_text(strip=True)
                dealer_info['Phone'] = phone_text
            
            # Extract website (look for dealer website, not map links)
            website_links = content_section.find_all('a', href=re.compile(r'//.*\.com'))
            for link in website_links:
                href = link.get('href', '')
                # Skip map links and look for actual dealer websites
                if not 'google.com' in href and not 'maps.apple.com' in href and not 'bentleymotors.com' in href:
                    if href.startswith('//'):
                        href = 'https:' + href
                    dealer_info['Website'] = href
                    break
            
            # Extract coordinates from map links
            google_map_link = content_section.find('a', href=re.compile(r'google\.com/maps'))
            if google_map_link:
                href = google_map_link.get('href', '')
                coords_match = re.search(r'query=([^&]+)', href)
                if coords_match:
                    coords = coords_match.group(1).split(',')
                    if len(coords) == 2:
                        try:
                            dealer_info['coordinates'] = {
                                'latitude': float(coords[0]),
                                'longitude': float(coords[1])
                            }
                        except ValueError:
                            pass
            
            # Extract opening hours
            hours_container = content_section.find('div', class_='dl-m-dealer-locator__dealer-details__opening-hours-container')
            if hours_container:
                hours_table = hours_container.find('table')
                if hours_table:
                    hours = {}
                    rows = hours_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            day = cells[0].get_text(strip=True)
                            time = cells[1].get_text(strip=True)
                            if day and time:
                                hours[day] = time
                    dealer_info['opening_hours'] = hours
            
            # Extract departments/services for this specific dealer
            departments = []
            dept_elements = button.find_all('span', class_='dl-m-dealer-locator__dealer-accordion__header-department')
            for dept in dept_elements:
                dept_text = dept.get_text(strip=True)
                if dept_text:
                    departments.append(dept_text)
            dealer_info['departments'] = departments
        
        # Only add dealer if we have at least a name
        if dealer_info.get('Dealer'):
            dealers.append(dealer_info)
    
    return dealers

def main():
    """Main function to process the HTML file and create JSON output."""
    
    # Read the HTML file
    with open('bentley.txt', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract dealer information
    dealers = extract_dealer_info(html_content)
    
    # Create the final JSON structure matching Toyota format
    bentley_data = {
        "oem": "Bentley",
        "zip_code": "multiple",
        "total_dealers_found": len(dealers),
        "method": "bentley_html_extraction",
        "dealers": dealers
    }
    
    # Write to JSON file
    with open('data/bentley.json', 'w', encoding='utf-8') as f:
        json.dump(bentley_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully extracted {len(dealers)} Bentley dealers to data/bentley.json")
    
    # Print summary
    print("\nDealer Summary:")
    for dealer in dealers:
        print(f"- {dealer['Dealer']} ({dealer.get('City', 'Unknown city')})")

if __name__ == "__main__":
    main()
