#!/usr/bin/env python3
"""
Convert comprehensive Toyota data to simple format matching Jeep structure.
This script transforms the rich comprehensive Toyota API response into a simple format
with just the essential dealer information.
"""

import json
import os

def convert_comprehensive_to_simple():
    """Convert comprehensive Toyota data to simple format."""
    
    # Check if comprehensive file exists
    comprehensive_file = 'data/toyota_comprehensive.json'
    if not os.path.exists(comprehensive_file):
        print(f"Error: {comprehensive_file} not found! Please run collect_all_toyota_dealers.py first.")
        return
    
    print(f"Reading from {comprehensive_file}...")
    
    # Read the comprehensive Toyota data
    with open(comprehensive_file, 'r') as f:
        toyota_data = json.load(f)
    
    print(f"Loaded {len(toyota_data)} dealers from comprehensive file")
    
    # Create the simple format structure
    simple_data = {
        "oem": "Toyota",
        "zip_code": "multiple",
        "total_dealers_found": len(toyota_data),
        "method": "toyota_comprehensive_api",
        "dealers": []
    }
    
    # Convert each dealer to simple format
    for dealer in toyota_data:
        simple_dealer = {
            "Dealer": dealer.get("name", ""),
            "Website": dealer.get("url", ""),
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
    
    print(f"✅ Successfully converted comprehensive Toyota data to simple format!")
    print(f"📊 Total dealers converted: {len(toyota_data)}")
    print(f"📝 Format matches Jeep structure: Dealer, Website, Phone, Email, Street, City, State, ZIP")
    
    # Show sample of converted data
    if simple_data["dealers"]:
        print(f"\n📋 Sample converted dealer:")
        sample = simple_data["dealers"][0]
        for key, value in sample.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    convert_comprehensive_to_simple()

