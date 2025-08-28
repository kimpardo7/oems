#!/usr/bin/env python3
"""
Convert Toyota dealer data to match Ferrari JSON format
"""

import json
from pathlib import Path

def convert_toyota_to_ferrari_format():
    """Convert Toyota dealer data to Ferrari format"""
    
    # Read the current Toyota data
    with open('data/toyota_backup2.json', 'r') as f:
        toyota_data = json.load(f)
    
    # Extract dealers from the current format
    dealers = toyota_data['dealers']
    
    # Convert to Ferrari format
    ferrari_format_dealers = []
    
    for dealer in dealers:
        # Create address string like Ferrari format
        address_parts = dealer['address']
        address_string = f"{address_parts['street']}, {address_parts['city']}, {address_parts['state']}, {address_parts['zip']}"
        
        # Convert distance from miles to km (if distance exists)
        distance_km = None
        if dealer.get('distance'):
            distance_km = dealer['distance'] * 1.60934  # Convert miles to km
        
        # Create Ferrari format dealer object (clean, simple structure)
        ferrari_dealer = {
            "id": dealer['dealer_code'],
            "name": dealer['name'],
            "distance_km": distance_km,
            "address": address_string,
            "country": "US",
            "services": ["Sale", "Service"]  # Default services for Toyota dealers
        }
        
        ferrari_format_dealers.append(ferrari_dealer)
    
    # Create the final structure
    final_data = {
        "toyota_dealers": ferrari_format_dealers
    }
    
    # Write to file
    with open('data/toyota.json', 'w') as f:
        json.dump(final_data, f, indent=4)
    
    print(f"Converted {len(ferrari_format_dealers)} Toyota dealers to Ferrari format")
    print("File saved as data/toyota.json")

if __name__ == "__main__":
    convert_toyota_to_ferrari_format()
