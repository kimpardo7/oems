#!/usr/bin/env python3
"""
Hyundai Clean Parser
Improved parser that extracts and cleans Hyundai dealer information from HTML.
"""

import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

def clean_dealer_name(name: str) -> str:
    """Clean dealer name by removing ratings, phone numbers, and other clutter."""
    # Remove rating patterns like "4.4(820)"
    name = re.sub(r'\d+\.\d+\(\d+\)', '', name)
    
    # Remove "Hyundai dealer" text
    name = re.sub(r'Hyundai dealer', '', name)
    
    # Remove special characters and extra spaces
    name = re.sub(r'[·\ue934]', '', name)
    name = re.sub(r'\s+', ' ', name)
    
    # Remove phone numbers
    name = re.sub(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', name)
    
    # Remove hours information
    name = re.sub(r'(Closed|Opens|Closes soon).*?(AM|PM)', '', name)
    
    # Remove address patterns
    name = re.sub(r'\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Way|Ln|Lane)', '', name)
    
    return name.strip()

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    match = re.search(phone_pattern, text)
    return match.group() if match else None

def extract_address(text: str) -> Optional[str]:
    """Extract address from text."""
    address_pattern = r'\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Way|Ln|Lane)'
    match = re.search(address_pattern, text)
    return match.group().strip() if match else None

def extract_rating(text: str) -> Optional[float]:
    """Extract rating from text."""
    rating_pattern = r'(\d+\.\d+)\(\d+\)'
    match = re.search(rating_pattern, text)
    return float(match.group(1)) if match else None

def extract_hours(text: str) -> Optional[str]:
    """Extract hours information from text."""
    hours_pattern = r'(Closed|Opens|Closes soon).*?(AM|PM)'
    match = re.search(hours_pattern, text)
    return match.group().strip() if match else None

def parse_hyundai_html_clean(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse Hyundai dealer HTML content and extract clean dealer information.
    
    Args:
        file_path: Path to the HTML file
        
    Returns:
        List of dictionaries containing clean dealer information
    """
    dealers = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for business name elements
        business_elements = soup.find_all(['div', 'span', 'a'], class_=re.compile(r'(fontHeadlineSmall|fontBodyMedium|fontBodySmall|fontDisplaySmall)'))
        
        seen_names = set()
        
        for element in business_elements:
            text = element.get_text(strip=True)
            if text and len(text) > 10:  # Filter out very short text
                # Check if this looks like a business name
                if any(keyword in text.lower() for keyword in ['hyundai', 'dealer', 'dealership', 'auto', 'motors']):
                    # Clean the name
                    clean_name = clean_dealer_name(text)
                    
                    # Skip if we've seen this name before or if it's too short
                    if clean_name in seen_names or len(clean_name) < 5:
                        continue
                    
                    seen_names.add(clean_name)
                    
                    # Extract additional information
                    phone = extract_phone(text)
                    address = extract_address(text)
                    rating = extract_rating(text)
                    hours = extract_hours(text)
                    
                    dealer = {
                        'name': clean_name,
                        'phone': phone,
                        'address': address,
                        'rating': rating,
                        'hours': hours,
                        'raw_text': text
                    }
                    
                    dealers.append(dealer)
        
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return []
    
    return dealers

def main():
    """Main function to parse Hyundai HTML and create clean JSON output."""
    input_file = '/Users/kimseanpardo/autodealerships/hyundai.txt'
    output_file = '/Users/kimseanpardo/autodealerships/hyundai_clean.json'
    
    print("Parsing Hyundai HTML content with clean extraction...")
    dealers = parse_hyundai_html_clean(input_file)
    
    print(f"Found {len(dealers)} clean dealer entries")
    
    # Create final JSON structure
    hyundai_data = {
        "brand": "Hyundai",
        "search_date": "2024-01-01",
        "total_dealers": len(dealers),
        "dealers": dealers
    }
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hyundai_data, f, indent=2, ensure_ascii=False)
    
    print(f"Clean Hyundai dealer data saved to {output_file}")
    
    # Print sample of results
    if dealers:
        print("\nSample dealer entries:")
        for i, dealer in enumerate(dealers[:5]):
            print(f"{i+1}. {dealer['name']}")
            if dealer.get('phone'):
                print(f"   Phone: {dealer['phone']}")
            if dealer.get('address'):
                print(f"   Address: {dealer['address']}")
            if dealer.get('rating'):
                print(f"   Rating: {dealer['rating']}")
            print()

if __name__ == "__main__":
    main()
