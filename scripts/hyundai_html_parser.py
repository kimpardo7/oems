#!/usr/bin/env python3
"""
Hyundai HTML Parser
Parses HTML content from Google Maps search results for Hyundai dealers
and extracts structured dealer information into JSON format.
"""

import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def parse_hyundai_html(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse Hyundai dealer HTML content and extract dealer information.
    
    Args:
        file_path: Path to the HTML file
        
    Returns:
        List of dictionaries containing dealer information
    """
    dealers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for common Google Maps result patterns
        # Search for elements that might contain dealer information
        
        # Method 1: Look for elements with specific classes that typically contain business info
        business_elements = soup.find_all(['div', 'span', 'a'], class_=re.compile(r'(fontHeadlineSmall|fontBodyMedium|fontBodySmall|fontDisplaySmall)'))
        
        for element in business_elements:
            text = element.get_text(strip=True)
            if text and len(text) > 3:  # Filter out very short text
                # Check if this looks like a business name or address
                if any(keyword in text.lower() for keyword in ['hyundai', 'dealer', 'dealership', 'auto', 'motors']):
                    dealers.append({
                        'name': text,
                        'type': 'business_name',
                        'raw_text': text
                    })
        
        # Method 2: Look for phone numbers
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_matches = re.findall(phone_pattern, html_content)
        for phone in phone_matches:
            dealers.append({
                'phone': phone,
                'type': 'phone_number'
            })
        
        # Method 3: Look for addresses (street addresses)
        address_pattern = r'\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Way|Ln|Lane)'
        address_matches = re.findall(address_pattern, html_content)
        for address in address_matches:
            dealers.append({
                'address': address,
                'type': 'street_address'
            })
        
        # Method 4: Look for city, state, zip patterns
        city_state_zip_pattern = r'([A-Za-z\s]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)'
        city_state_zip_matches = re.findall(city_state_zip_pattern, html_content)
        for city, state, zip_code in city_state_zip_matches:
            dealers.append({
                'city': city.strip(),
                'state': state,
                'zip_code': zip_code,
                'type': 'location'
            })
        
        # Method 5: Look for specific Google Maps result containers
        result_containers = soup.find_all('div', {'role': 'article'})
        for container in result_containers:
            dealer_info = {}
            
            # Extract business name
            name_elem = container.find(['h3', 'h4', 'div'], class_=re.compile(r'fontHeadlineSmall'))
            if name_elem:
                dealer_info['name'] = name_elem.get_text(strip=True)
            
            # Extract address
            address_elem = container.find(['div', 'span'], class_=re.compile(r'fontBodyMedium'))
            if address_elem:
                address_text = address_elem.get_text(strip=True)
                if any(keyword in address_text.lower() for keyword in ['st', 'street', 'ave', 'avenue', 'rd', 'road']):
                    dealer_info['address'] = address_text
            
            # Extract phone
            phone_elem = container.find(text=re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'))
            if phone_elem:
                phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', phone_elem)
                if phone_match:
                    dealer_info['phone'] = phone_match.group()
            
            if dealer_info:
                dealer_info['type'] = 'complete_dealer'
                dealers.append(dealer_info)
        
        # Method 6: Look for aria-label attributes that might contain business names
        aria_labels = soup.find_all(attrs={'aria-label': True})
        for elem in aria_labels:
            label = elem.get('aria-label', '')
            if 'hyundai' in label.lower() and len(label) > 10:
                dealers.append({
                    'name': label,
                    'type': 'aria_label',
                    'raw_text': label
                })
        
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return []
    
    return dealers

def clean_and_deduplicate_dealers(dealers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean and deduplicate dealer information.
    
    Args:
        dealers: Raw list of dealer information
        
    Returns:
        Cleaned and deduplicated list
    """
    cleaned_dealers = []
    seen_names = set()
    
    for dealer in dealers:
        if dealer.get('type') == 'complete_dealer' and 'name' in dealer:
            name = dealer['name'].strip()
            if name not in seen_names and len(name) > 3:
                seen_names.add(name)
                cleaned_dealers.append(dealer)
    
    return cleaned_dealers

def main():
    """Main function to parse Hyundai HTML and create JSON output."""
    input_file = '/Users/kimseanpardo/autodealerships/hyundai.txt'
    output_file = '/Users/kimseanpardo/autodealerships/hyundai.json'
    raw_output_file = '/Users/kimseanpardo/autodealerships/hyundai_raw.json'
    
    print("Parsing Hyundai HTML content...")
    dealers = parse_hyundai_html(input_file)
    
    print(f"Found {len(dealers)} raw dealer entries")
    
    # Save raw data for debugging
    with open(raw_output_file, 'w', encoding='utf-8') as f:
        json.dump(dealers, f, indent=2, ensure_ascii=False)
    print(f"Raw data saved to {raw_output_file}")
    
    # Clean and deduplicate
    cleaned_dealers = clean_and_deduplicate_dealers(dealers)
    
    print(f"After cleaning: {len(cleaned_dealers)} unique dealers")
    
    # If no complete dealers found, include all raw data
    if not cleaned_dealers:
        print("No complete dealers found, including all raw data...")
        cleaned_dealers = dealers
    
    # Create final JSON structure
    hyundai_data = {
        "brand": "Hyundai",
        "search_date": "2024-01-01",  # Update with actual date
        "total_dealers": len(cleaned_dealers),
        "dealers": cleaned_dealers
    }
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hyundai_data, f, indent=2, ensure_ascii=False)
    
    print(f"Hyundai dealer data saved to {output_file}")
    
    # Print sample of results
    if cleaned_dealers:
        print("\nSample dealer entries:")
        for i, dealer in enumerate(cleaned_dealers[:5]):
            print(f"{i+1}. {dealer}")

if __name__ == "__main__":
    main()
