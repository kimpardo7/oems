#!/usr/bin/env python3
"""
Convert Toyota data format to match the standard format used by other mainstream brands.
This script transforms the complex Toyota JSON structure into the simpler format used by
Chevrolet, Chrysler, and Dodge.
"""

import json
import os

def convert_toyota_format():
    """Convert Toyota data to standard mainstream format."""
    
    # Read the current Toyota data
    with open('data/toyota.json', 'r') as f:
        toyota_data = json.load(f)
    
    # Create the new format structure
    converted_data = {
        "oem": "Toyota",
        "zip_code": "multiple",
        "total_dealers_found": len(toyota_data),
        "method": "converted_from_toyota_api_format",
        "dealers": []
    }
    
    # Convert each dealer
    for dealer in toyota_data:
        converted_dealer = {
            "Dealer": dealer.get("name", ""),
            "Website": dealer.get("website", ""),
            "Phone": dealer.get("phone", ""),
            "Email": dealer.get("email", ""),
            "Street": dealer.get("address", {}).get("street", ""),
            "City": dealer.get("address", {}).get("city", ""),
            "State": dealer.get("address", {}).get("state", ""),
            "ZIP": dealer.get("address", {}).get("zip", "")
        }
        converted_data["dealers"].append(converted_dealer)
    
    # Save the converted data
    with open('data/toyota.json', 'w') as f:
        json.dump(converted_data, f, indent=2)
    
    print(f"Successfully converted Toyota data format!")
    print(f"Total dealers converted: {len(toyota_data)}")
    print(f"New format matches Chevrolet/Chrysler/Dodge structure")

if __name__ == "__main__":
    convert_toyota_format()
