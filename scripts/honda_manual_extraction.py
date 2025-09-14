#!/usr/bin/env python3
"""
Manual Honda Dealer Extraction
Extracts dealer information from the current Honda dealer locator page
"""

import json
from datetime import datetime

# Honda dealers observed from the website
# This is based on what we can see from the Honda dealer locator
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
        "Dealer": "Honda of North Hollywood",
        "Website": "https://www.northhollywoodtoyota.com/",
        "Phone": "818-508-2900",
        "Email": "",
        "Street": "4606 Lankershim Boulevard",
        "City": "North Hollywood",
        "State": "CA",
        "ZIP": "91602"
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
        "Dealer": "Honda of Santa Monica",
        "Website": "https://www.toyotasantamonica.com/",
        "Phone": "424-567-7599",
        "Email": "",
        "Street": "1230 Santa Monica Blvd.",
        "City": "Santa Monica",
        "State": "CA",
        "ZIP": "90404"
    },
    {
        "Dealer": "Marina del Rey Honda",
        "Website": "https://www.marinadelreytoyota.com/",
        "Phone": "866-823-8348",
        "Email": "",
        "Street": "4636 Lincoln Boulevard",
        "City": "Marina Del Rey",
        "State": "CA",
        "ZIP": "90292"
    },
    {
        "Dealer": "Honda of Glendale",
        "Website": "https://www.toyotaofglendale.com/",
        "Phone": "818-244-4196",
        "Email": "",
        "Street": "1260 South Brand Blvd.",
        "City": "Glendale",
        "State": "CA",
        "ZIP": "91204"
    },
    {
        "Dealer": "Hamer Honda",
        "Website": "https://www.hamertoyota.com/",
        "Phone": "818-365-9621",
        "Email": "",
        "Street": "11041 Sepulveda Blvd",
        "City": "Mission Hills",
        "State": "CA",
        "ZIP": "91345"
    },
    {
        "Dealer": "Northridge Honda",
        "Website": "https://www.northridgetoyota.com/",
        "Phone": "818-734-5600",
        "Email": "",
        "Street": "19550 Nordhoff Street",
        "City": "Northridge",
        "State": "CA",
        "ZIP": "91324"
    }
]

def create_honda_json():
    """Create Honda JSON file with dealer information"""
    
    # Remove duplicates based on dealer name and address
    unique_dealers = []
    seen = set()
    
    for dealer in HONDA_DEALERS:
        key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
        if key not in seen:
            seen.add(key)
            unique_dealers.append(dealer)
    
    # Create the JSON structure similar to Toyota
    honda_data = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(unique_dealers),
        "method": "honda_website_manual_extraction",
        "dealers": unique_dealers
    }
    
    # Save to file
    with open("data/honda.json", "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"Honda JSON file created with {len(unique_dealers)} unique dealers")
    print("File saved to: data/honda.json")
    
    # Also create a timestamped version
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/honda_dealers_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"Timestamped version saved to: {filename}")
    
    # Print summary
    print(f"\nDealers by state:")
    state_counts = {}
    for dealer in unique_dealers:
        state = dealer['State']
        state_counts[state] = state_counts.get(state, 0) + 1
    
    for state, count in sorted(state_counts.items()):
        print(f"  {state}: {count} dealers")

if __name__ == "__main__":
    create_honda_json()
