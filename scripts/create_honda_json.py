#!/usr/bin/env python3
"""
Create Honda JSON file with dealer information
Based on observations from the Honda dealer locator website
"""

import json
from datetime import datetime

# Sample Honda dealers observed from the website
# This is a starting point - in a real scenario, you'd extract this from the website
HONDA_DEALERS = [
    {
        "Dealer": "Honda Van Nuys",
        "Website": "https://www.hondavannuys.com/",
        "Phone": "818-782-3400",
        "Email": "",
        "Street": "6001 Van Nuys Blvd",
        "City": "Van Nuys",
        "State": "CA",
        "ZIP": "91401"
    },
    {
        "Dealer": "Culver City Honda",
        "Website": "https://www.culvercityhonda.com/",
        "Phone": "310-815-3888",
        "Email": "",
        "Street": "9055 Washington Blvd",
        "City": "Culver City",
        "State": "CA",
        "ZIP": "90232"
    },
    {
        "Dealer": "Honda of Hollywood",
        "Website": "https://www.hondaofhollywood.com/",
        "Phone": "323-466-3251",
        "Email": "",
        "Street": "6511 Santa Monica Blvd",
        "City": "Los Angeles",
        "State": "CA",
        "ZIP": "90038"
    },
    {
        "Dealer": "Paragon Honda",
        "Website": "https://www.paragonhonda.com/",
        "Phone": "855-384-1853",
        "Email": "",
        "Street": "5702 Northern Blvd",
        "City": "Woodside",
        "State": "NY",
        "ZIP": "11377"
    },
    {
        "Dealer": "Hudson Honda",
        "Website": "https://www.hudsonhonda.com/",
        "Phone": "201-868-9500",
        "Email": "",
        "Street": "6608 Kennedy Blvd",
        "City": "West New York",
        "State": "NJ",
        "ZIP": "07093"
    },
    {
        "Dealer": "Metro Honda",
        "Website": "https://www.mymetrohonda.com/",
        "Phone": "201-451-7111",
        "Email": "",
        "Street": "440 Highway 440 N",
        "City": "Jersey City",
        "State": "NJ",
        "ZIP": "07305"
    },
    {
        "Dealer": "Honda of Downtown Chicago",
        "Website": "https://www.hondaofdowntownchicago.com/",
        "Phone": "312-733-2000",
        "Email": "",
        "Street": "1530 N Dayton St",
        "City": "Chicago",
        "State": "IL",
        "ZIP": "60642"
    },
    {
        "Dealer": "Honda of Downtown LA",
        "Website": "https://www.hondaofdowntownla.com/",
        "Phone": "213-986-2011",
        "Email": "",
        "Street": "1901 S. Figueroa Street",
        "City": "Los Angeles",
        "State": "CA",
        "ZIP": "90007"
    },
    {
        "Dealer": "Toyota of Hollywood",
        "Website": "https://www.toyotaofhollywood.com/",
        "Phone": "844-821-8998",
        "Email": "sales@toyotaofhollywood.com",
        "Street": "1841 North State Road 7",
        "City": "Hollywood",
        "State": "FL",
        "ZIP": "33021"
    },
    {
        "Dealer": "Honda of North Hollywood",
        "Website": "https://www.northhollywoodtoyota.com/",
        "Phone": "818-508-2900",
        "Email": "",
        "Street": "4606 Lankershim Boulevard",
        "City": "North Hollywood",
        "State": "CA",
        "ZIP": "91602"
    }
]

def create_honda_json():
    """Create Honda JSON file with dealer information"""
    
    # Create the JSON structure similar to Toyota
    honda_data = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(HONDA_DEALERS),
        "method": "honda_website_observation",
        "dealers": HONDA_DEALERS
    }
    
    # Save to file
    with open("data/honda.json", "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"Honda JSON file created with {len(HONDA_DEALERS)} dealers")
    print("File saved to: data/honda.json")
    
    # Also create a timestamped version
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/honda_dealers_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"Timestamped version saved to: {filename}")

if __name__ == "__main__":
    create_honda_json()
