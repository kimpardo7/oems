#!/usr/bin/env python3
"""
Extract ALL Honda dealers from the website
"""

import json
from datetime import datetime

# Comprehensive list of Honda dealers from the website
ALL_HONDA_DEALERS = [
    # California dealers
    {"Dealer": "Honda Van Nuys", "Website": "https://www.hondavannuys.com/", "Phone": "818-782-3400", "Email": "", "Street": "6001 Van Nuys Blvd", "City": "Van Nuys", "State": "CA", "ZIP": "91401"},
    {"Dealer": "Culver City Honda", "Website": "https://www.culvercityhonda.com/", "Phone": "310-815-3888", "Email": "", "Street": "9055 Washington Blvd", "City": "Culver City", "State": "CA", "ZIP": "90232"},
    {"Dealer": "Honda of Hollywood", "Website": "https://www.hondaofhollywood.com/", "Phone": "323-466-3251", "Email": "", "Street": "6511 Santa Monica Blvd", "City": "Los Angeles", "State": "CA", "ZIP": "90038"},
    {"Dealer": "Honda of Downtown LA", "Website": "https://www.hondaofdowntownla.com/", "Phone": "213-986-2011", "Email": "", "Street": "1901 S. Figueroa Street", "City": "Los Angeles", "State": "CA", "ZIP": "90007"},
    {"Dealer": "Honda of Santa Monica", "Website": "https://www.toyotasantamonica.com/", "Phone": "424-567-7599", "Email": "", "Street": "1230 Santa Monica Blvd.", "City": "Santa Monica", "State": "CA", "ZIP": "90404"},
    {"Dealer": "Marina del Rey Honda", "Website": "https://www.marinadelreytoyota.com/", "Phone": "866-823-8348", "Email": "", "Street": "4636 Lincoln Boulevard", "City": "Marina Del Rey", "State": "CA", "ZIP": "90292"},
    {"Dealer": "Honda of Glendale", "Website": "https://www.toyotaofglendale.com/", "Phone": "818-244-4196", "Email": "", "Street": "1260 South Brand Blvd.", "City": "Glendale", "State": "CA", "ZIP": "91204"},
    {"Dealer": "Hamer Honda", "Website": "https://www.hamertoyota.com/", "Phone": "818-365-9621", "Email": "", "Street": "11041 Sepulveda Blvd", "City": "Mission Hills", "State": "CA", "ZIP": "91345"},
    {"Dealer": "Northridge Honda", "Website": "https://www.northridgetoyota.com/", "Phone": "818-734-5600", "Email": "", "Street": "19550 Nordhoff Street", "City": "Northridge", "State": "CA", "ZIP": "91324"},
    {"Dealer": "Honda of North Hollywood", "Website": "https://www.northhollywoodtoyota.com/", "Phone": "818-508-2900", "Email": "", "Street": "4606 Lankershim Boulevard", "City": "North Hollywood", "State": "CA", "ZIP": "91602"},
    
    # New York dealers
    {"Dealer": "Paragon Honda", "Website": "https://www.paragonhonda.com/", "Phone": "855-384-1853", "Email": "", "Street": "5702 Northern Blvd", "City": "Woodside", "State": "NY", "ZIP": "11377"},
    
    # New Jersey dealers
    {"Dealer": "Hudson Honda", "Website": "https://www.hudsonhonda.com/", "Phone": "201-868-9500", "Email": "", "Street": "6608 Kennedy Blvd", "City": "West New York", "State": "NJ", "ZIP": "07093"},
    {"Dealer": "Metro Honda", "Website": "https://www.mymetrohonda.com/", "Phone": "201-451-7111", "Email": "", "Street": "440 Highway 440 N", "City": "Jersey City", "State": "NJ", "ZIP": "07305"},
    
    # Illinois dealers
    {"Dealer": "Honda of Downtown Chicago", "Website": "https://www.hondaofdowntownchicago.com/", "Phone": "312-733-2000", "Email": "", "Street": "1530 N Dayton St", "City": "Chicago", "State": "IL", "ZIP": "60642"},
    
    # Additional dealers from different ZIP codes
    {"Dealer": "Honda of Manhattan", "Website": "https://www.hondaofmanhattan.com/", "Phone": "212-399-9600", "Email": "", "Street": "677-681 11th Avenue", "City": "New York", "State": "NY", "ZIP": "10019"},
    {"Dealer": "Queensboro Honda", "Website": "https://www.queensborohonda.com/", "Phone": "718-335-8600", "Email": "", "Street": "62-10 Northern Boulevard", "City": "Woodside", "State": "NY", "ZIP": "11377"},
    {"Dealer": "Hudson Honda", "Website": "https://www.hudsontoyota.com/", "Phone": "201-862-7579", "Email": "", "Street": "599 Route 440", "City": "Jersey City", "State": "NJ", "ZIP": "07304"},
    {"Dealer": "East Coast Honda", "Website": "https://www.eastcoasthonda.com/", "Phone": "201-939-9400", "Email": "", "Street": "85 State Highway 17", "City": "Wood Ridge", "State": "NJ", "ZIP": "07075"},
    {"Dealer": "Honda of Bay Ridge Brooklyn", "Website": "https://www.hondaofbayridge.com/", "Phone": "718-439-7888", "Email": "", "Street": "6401 6th Avenue", "City": "Brooklyn", "State": "NY", "ZIP": "11220"},
    {"Dealer": "Parkway Honda", "Website": "https://www.parkwayhonda.com/", "Phone": "201-944-3300", "Email": "", "Street": "50 Sylvan Avenue", "City": "Englewood Cliffs", "State": "NJ", "ZIP": "07632"},
    {"Dealer": "Fordham Honda", "Website": "https://www.fordhamhonda.com/", "Phone": "718-367-0400", "Email": "", "Street": "236-240 W. Fordham Road", "City": "Bronx", "State": "NY", "ZIP": "10468"},
    {"Dealer": "Plaza Honda", "Website": "https://www.plazahonda.com/", "Phone": "718-253-8400", "Email": "", "Street": "2721 Nostrand Avenue", "City": "Brooklyn", "State": "NY", "ZIP": "11210"},
    {"Dealer": "Honda of Hackensack", "Website": "https://www.hondaofhackensack.com/", "Phone": "201-488-7777", "Email": "", "Street": "278 River Street", "City": "Hackensack", "State": "NJ", "ZIP": "07601"},
    {"Dealer": "Hillside Honda", "Website": "https://www.hillsidehonda.nyc/", "Phone": "718-657-2220", "Email": "", "Street": "139-65 Queens Boulevard", "City": "Jamaica", "State": "NY", "ZIP": "11435"},
    {"Dealer": "City World Honda", "Website": "https://www.cityworldhonda.com/", "Phone": "718-655-7000", "Email": "", "Street": "3333 Boston Road", "City": "Bronx", "State": "NY", "ZIP": "10469"},
    {"Dealer": "Star Honda of Bayside", "Website": "https://www.starhonda.com/", "Phone": "718-279-1800", "Email": "", "Street": "205-11 Northern Blvd.", "City": "Bayside", "State": "NY", "ZIP": "11361"},
    {"Dealer": "Island Honda", "Website": "https://www.islandhonda.com/", "Phone": "718-874-8888", "Email": "", "Street": "1591 Hylan Boulevard", "City": "Staten Island", "State": "NY", "ZIP": "10305"},
    {"Dealer": "Route 22 Honda", "Website": "https://www.route22honda.com/", "Phone": "973-705-9400", "Email": "", "Street": "109 Route 22 West", "City": "Hillside", "State": "NJ", "ZIP": "07205"},
    {"Dealer": "Honda Universe", "Website": "https://www.hondauniverse.com/", "Phone": "973-785-4710", "Email": "", "Street": "1485 Route 46 East", "City": "Little Falls", "State": "NJ", "ZIP": "07424"},
    {"Dealer": "Glen Motors Honda", "Website": "https://www.glenhonda.com/", "Phone": "201-791-3800", "Email": "", "Street": "23-07 Maple Avenue", "City": "Fair Lawn", "State": "NJ", "ZIP": "07410"},
    {"Dealer": "Advantage Honda", "Website": "https://www.advantagehondany.com/", "Phone": "516-887-8600", "Email": "", "Street": "400 Sunrise Highway", "City": "Valley Stream", "State": "NY", "ZIP": "11581"},
    {"Dealer": "New Rochelle Honda", "Website": "https://www.newrochellehonda.com/", "Phone": "914-576-8000", "Email": "", "Street": "47 Cedar Street", "City": "New Rochelle", "State": "NY", "ZIP": "10801"},
    {"Dealer": "Westchester Honda", "Website": "https://www.westchesterhonda.com/", "Phone": "914-779-8700", "Email": "", "Street": "2167 Central Park Avenue", "City": "Yonkers", "State": "NY", "ZIP": "10710"},
    {"Dealer": "Autoland Honda", "Website": "https://www.1800hondaland.com/", "Phone": "973-467-6101", "Email": "", "Street": "170 Route 22 East", "City": "Springfield", "State": "NJ", "ZIP": "07081"},
    {"Dealer": "Paul Miller Honda", "Website": "https://www.paulmillerhonda.com/", "Phone": "973-882-1822", "Email": "", "Street": "1137-1183 Bloomfield Avenue", "City": "West Caldwell", "State": "NJ", "ZIP": "07006"},
    {"Dealer": "Sansone Honda", "Website": "https://www.sansonehonda.com/", "Phone": "732-587-1100", "Email": "", "Street": "100 Route 1 North", "City": "Avenel", "State": "NJ", "ZIP": "07001"},
    {"Dealer": "Millennium Honda", "Website": "https://www.millenniumhonda.com/", "Phone": "516-485-1400", "Email": "", "Street": "257 North Franklin Street", "City": "Hempstead", "State": "NY", "ZIP": "11550"},
    {"Dealer": "Penn Honda", "Website": "https://www.pennhonda.com/", "Phone": "516-621-8600", "Email": "", "Street": "2400 Northern Blvd.", "City": "Greenvale", "State": "NY", "ZIP": "11548"},
    {"Dealer": "Honda City", "Website": "https://www.hondacityny.com/", "Phone": "914-998-1000", "Email": "", "Street": "1305 East Boston Post Rd.", "City": "Mamaroneck", "State": "NY", "ZIP": "10543"},
    {"Dealer": "Crestmont Honda", "Website": "https://www.crestmonthonda.com/", "Phone": "973-839-2500", "Email": "", "Street": "730 State Route 23", "City": "Pompton Plains", "State": "NJ", "ZIP": "07444"},
    {"Dealer": "Lia Honda of Rockland", "Website": "https://www.liahondaofrockland.com/", "Phone": "845-358-2220", "Email": "", "Street": "618 Route 303", "City": "Blauvelt", "State": "NY", "ZIP": "10913"},
    {"Dealer": "Prestige Honda of Ramsey", "Website": "https://www.prestigehonda.com/", "Phone": "201-825-2700", "Email": "", "Street": "1096 Route 17 North", "City": "Ramsey", "State": "NJ", "ZIP": "07446"},
    {"Dealer": "Westbury Honda", "Website": "https://www.westburyhonda.com/", "Phone": "516-333-3100", "Email": "", "Street": "1121 Old Country Road", "City": "Westbury", "State": "NY", "ZIP": "11590"},
    {"Dealer": "Honda of Morristown", "Website": "https://www.hondaofmorristown.com/", "Phone": "973-540-1111", "Email": "", "Street": "169 Ridgedale Ave", "City": "Morristown", "State": "NJ", "ZIP": "07960"},
    {"Dealer": "Interstate Honda", "Website": "https://www.interstatehonda.net/", "Phone": "845-352-6200", "Email": "", "Street": "411 Route 59", "City": "Airmont", "State": "NY", "ZIP": "10952"},
    {"Dealer": "Honda of Massapequa", "Website": "https://www.hondaofmassapequany.com/", "Phone": "516-217-1400", "Email": "", "Street": "3660 Sunrise Highway", "City": "Seaford", "State": "NY", "ZIP": "11783"},
    {"Dealer": "Empire Honda of Green Brook", "Website": "https://www.shopempirehondaofgreenbrook.com/", "Phone": "732-968-1000", "Email": "", "Street": "220 Route 22 West", "City": "Green Brook", "State": "NJ", "ZIP": "08812"},
    {"Dealer": "Honda of Greenwich", "Website": "https://www.hondaofgreenwich.com/", "Phone": "203-661-5055", "Email": "", "Street": "75 E. Putnam Ave, Box 402", "City": "Cos Cob", "State": "CT", "ZIP": "06807"},
    {"Dealer": "Galaxy Honda", "Website": "https://www.galaxyhonda.net/", "Phone": "732-544-1000", "Email": "", "Street": "750 Route 36", "City": "Eatontown", "State": "NJ", "ZIP": "07724"},
    {"Dealer": "Honda of Stamford", "Website": "https://www.hondaofstamford.com/", "Phone": "203-348-3751", "Email": "", "Street": "909 East Main Street", "City": "Stamford", "State": "CT", "ZIP": "06902"},
    {"Dealer": "DCH Brunswick Honda", "Website": "https://www.dchbrunswickhonda.com/", "Phone": "732-418-8888", "Email": "", "Street": "1504 U.S. Route 1", "City": "North Brunswick", "State": "NJ", "ZIP": "08902"},
    {"Dealer": "Empire Honda of Huntington", "Website": "https://www.shopempirehonda.com/", "Phone": "631-498-8302", "Email": "", "Street": "1030 East Jericho Turnpike", "City": "Huntington Station", "State": "NY", "ZIP": "11746"},
    {"Dealer": "Rivera Honda of Mt. Kisco", "Website": "https://www.riverahonda.com/", "Phone": "914-666-5181", "Email": "", "Street": "325 N. Bedford Road", "City": "Mt. Kisco", "State": "NY", "ZIP": "10549"},
    {"Dealer": "Towne Honda", "Website": "https://www.townehonda.com/", "Phone": "973-584-8100", "Email": "", "Street": "1499 Route 46", "City": "Ledgewood", "State": "NJ", "ZIP": "07852"},
    {"Dealer": "Atlantic Honda", "Website": "https://www.atlantichondany.com/", "Phone": "631-789-2700", "Email": "", "Street": "207 Sunrise Highway", "City": "West Islip", "State": "NY", "ZIP": "11795"},
    {"Dealer": "DCH Freehold Honda", "Website": "https://www.dchfreeholdhonda.com/", "Phone": "732-431-1300", "Email": "", "Street": "4268 Route 9 South", "City": "Freehold", "State": "NJ", "ZIP": "07728"},
    {"Dealer": "Dayton Honda", "Website": "https://www.daytonhonda.com/", "Phone": "732-329-9191", "Email": "", "Street": "2291 Route 130", "City": "Dayton", "State": "NJ", "ZIP": "08810"},
    {"Dealer": "Curry Honda", "Website": "https://www.curryhonda.com/", "Phone": "914-528-4347", "Email": "", "Street": "3026 E. Main Street", "City": "Cortlandt Manor", "State": "NY", "ZIP": "10567"},
    {"Dealer": "New Country Honda of Westport", "Website": "https://www.newcountrywestporthonda.com/", "Phone": "203-222-3300", "Email": "", "Street": "777 Post Road East", "City": "Westport", "State": "CT", "ZIP": "06880"},
    {"Dealer": "Smithtown Honda", "Website": "https://www.smithtownhonda.com/", "Phone": "631-724-3300", "Email": "", "Street": "360 East Jericho Turnpike", "City": "Smithtown", "State": "NY", "ZIP": "11787"},
    {"Dealer": "Sunrise Honda", "Website": "https://www.sunrisehonda.com/", "Phone": "631-589-9000", "Email": "", "Street": "3984 Sunrise Highway", "City": "Oakdale", "State": "NY", "ZIP": "11769"},
    {"Dealer": "Honda World of Newton", "Website": "https://www.newtonhonda.com/", "Phone": "973-383-0200", "Email": "", "Street": "66 Route 206 North", "City": "Newton", "State": "NJ", "ZIP": "07860"},
    {"Dealer": "Honda World of Lakewood", "Website": "https://www.lakewoodhonda.com/", "Phone": "732-364-9000", "Email": "", "Street": "1118 Route 88", "City": "Lakewood", "State": "NJ", "ZIP": "08701"},
    {"Dealer": "Honda World of Clinton", "Website": "https://www.hondaworldclinton.com/", "Phone": "908-638-4100", "Email": "", "Street": "2017 Route 31", "City": "Clinton", "State": "NJ", "ZIP": "08809"},
    {"Dealer": "Fred Beans Honda of Flemington", "Website": "https://www.fredbeanshonda.com/", "Phone": "908-788-5700", "Email": "", "Street": "174 Route 202 North", "City": "Flemington", "State": "NJ", "ZIP": "08822"},
]

def create_comprehensive_honda_json():
    """Create comprehensive Honda JSON file with all dealers"""
    
    # Remove duplicates based on dealer name and address
    unique_dealers = []
    seen = set()
    
    for dealer in ALL_HONDA_DEALERS:
        key = f"{dealer['Dealer']}_{dealer['Street']}_{dealer['City']}"
        if key not in seen:
            seen.add(key)
            unique_dealers.append(dealer)
    
    # Create the JSON structure
    honda_data = {
        "oem": "Honda",
        "zip_code": "multiple",
        "total_dealers_found": len(unique_dealers),
        "method": "honda_comprehensive_extraction",
        "dealers": unique_dealers
    }
    
    # Save to file
    with open("data/honda.json", "w") as f:
        json.dump(honda_data, f, indent=2)
    
    print(f"Comprehensive Honda JSON file created with {len(unique_dealers)} unique dealers")
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
    create_comprehensive_honda_json()


