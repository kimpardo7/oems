#!/usr/bin/env python3
"""
Convert Toyota API data to simple format matching Jeep structure.
This script transforms the rich Toyota API response into a simple format
with just the essential dealer information.
"""

import json
import os

def convert_toyota_to_simple_format():
    """Convert Toyota API data to simple format."""
    
    # Check if test file exists
    test_file = 'data/toyota_test.json'
    if not os.path.exists(test_file):
        print(f"Error: {test_file} not found! Please run test_toyota_api.py first.")
        return
    
    print(f"Reading from {test_file}...")
    
    # Read the Toyota test data
    with open(test_file, 'r') as f:
        toyota_data = json.load(f)
    
    print(f"Loaded {len(toyota_data)} dealers from test file")
    
    # Create the simple format structure
    simple_data = {
        "oem": "Toyota",
        "zip_code": "multiple",
        "total_dealers_found": len(toyota_data),
        "method": "toyota_api_test",
        "dealers": []
    }
    
    # Convert each dealer to simple format
    for dealer in toyota_data:
        simple_dealer = {
            "Dealer": dealer.get("name", ""),
            "Website": dealer.get("url", ""),  # Toyota API provides website URLs in 'url' field
            "Phone": dealer.get("general", {}).get("phone", ""),
            "Email": dealer.get("email", ""),
            "Street": dealer.get("address1", ""),
            "City": dealer.get("city", ""),
            "State": dealer.get("state", ""),
            "ZIP": dealer.get("zip", "")
        }
        simple_data["dealers"].append(simple_dealer)
    
    # Save the simple format data
    output_file = 'data/toyota.json'
    print(f"Saving to {output_file}...")
    
    with open(output_file, 'w') as f:
        json.dump(simple_data, f, indent=2)
    
    print(f"✅ Successfully converted Toyota data to simple format!")
    print(f"📊 Total dealers converted: {len(toyota_data)}")
    print(f"📝 Format matches Jeep structure: Dealer, Website, Phone, Email, Street, City, State, ZIP")
    
    # Show sample of converted data
    if simple_data["dealers"]:
        print(f"\n📋 Sample converted dealer:")
        sample = simple_data["dealers"][0]
        for key, value in sample.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    convert_toyota_to_simple_format()
