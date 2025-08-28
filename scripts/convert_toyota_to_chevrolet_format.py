#!/usr/bin/env python3
"""
Convert Toyota dealer data to match Chevrolet JSON format
"""

import json
from pathlib import Path

def convert_toyota_to_chevrolet_format():
    """Convert Toyota dealer data to Chevrolet format"""
    
    # Read the current Toyota data
    with open('data/toyota_backup2.json', 'r') as f:
        toyota_data = json.load(f)
    
    # Extract dealers from the current format
    dealers = toyota_data['dealers']
    
    # Convert to Chevrolet format
    chevrolet_format_dealers = []
    
    for dealer in dealers:
        # Create Chevrolet format dealer object - ONLY the fields we need
        chevrolet_dealer = {
            "Dealer": dealer['name'],
            "Website": dealer.get('website', ''),
            "Phone": dealer.get('phone', ''),
            "Email": dealer.get('email', ''),
            "Street": dealer['address']['street'],
            "City": dealer['address']['city'],
            "State": dealer['address']['state'],
            "ZIP": dealer['address']['zip']
        }
        
        chevrolet_format_dealers.append(chevrolet_dealer)
    
    # Create the final structure matching Chevrolet format
    final_data = {
        "oem": "Toyota",
        "zip_code": "multiple",
        "total_dealers_found": len(chevrolet_format_dealers),
        "method": "api_dealer_discovery",
        "dealers": chevrolet_format_dealers
    }
    
    # Write to file
    with open('data/toyota.json', 'w') as f:
        json.dump(final_data, f, indent=2)
    
    print(f"Converted {len(chevrolet_format_dealers)} Toyota dealers to Chevrolet format")
    print("File saved as data/toyota.json")

if __name__ == "__main__":
    convert_toyota_to_chevrolet_format()
