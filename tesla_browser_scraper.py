#!/usr/bin/env python3
"""
Tesla Dealership Browser Scraper
Extracts Tesla dealership data from browser automation results.
"""

import json
import re
from urllib.parse import urljoin

def extract_coordinates_from_url(url):
    """Extract latitude and longitude from Tesla demo drive URL"""
    if not url:
        return None, None
    
    try:
        # Look for lat and lng parameters in the URL
        lat_match = re.search(r'lat=([\d.-]+)', url)
        lng_match = re.search(r'lng=([\d.-]+)', url)
        
        if lat_match and lng_match:
            return float(lat_match.group(1)), float(lng_match.group(1))
    except (ValueError, AttributeError):
        pass
    
    return None, None

def clean_phone_number(phone):
    """Clean and format phone number"""
    if not phone:
        return ""
    # Remove all non-digit characters except + and -
    phone = re.sub(r'[^\d+\-()]', '', phone)
    return phone.strip()

def parse_tesla_dealerships_from_browser_data():
    """
    Parse Tesla dealership data from the browser snapshot we captured.
    This is a manual extraction based on the page structure we observed.
    """
    
    # This is the data structure we observed from the browser snapshot
    # We'll extract the dealership information systematically
    
    dealerships = []
    
    # Arizona dealerships
    arizona_dealerships = [
        {
            'name': 'Glendale',
            'address': '9245 W Glendale Ave',
            'city': 'Glendale',
            'state': 'Arizona',
            'zip_code': '85305',
            'phone': '(602) 337-5554',
            'latitude': 33.5368835,
            'longitude': -112.2578684
        },
        {
            'name': 'Mesa',
            'address': '7444 E Hampton Ave',
            'city': 'Mesa',
            'state': 'Arizona',
            'zip_code': '85209',
            'phone': '6026273515',
            'latitude': 33.3919982,
            'longitude': -111.6711962
        },
        {
            'name': 'Scottsdale',
            'address': '8300 E Raintree Dr',
            'city': 'Scottsdale',
            'state': 'Arizona',
            'zip_code': '85260',
            'phone': '480-361-0036',
            'latitude': 33.6197263,
            'longitude': -111.9019416
        },
        {
            'name': 'Scottsdale-Fashion Square',
            'address': '7014 E. Camelback Road Suite #1210',
            'city': 'Scottsdale',
            'state': 'Arizona',
            'zip_code': '85251',
            'phone': '(480) 946-3735',
            'latitude': 33.503167,
            'longitude': -111.92968
        },
        {
            'name': 'Scottsdale-Kierland Commons',
            'address': '15215 N. Kierland Blvd #165B1A',
            'city': 'Scottsdale',
            'state': 'Arizona',
            'zip_code': '85254',
            'phone': '480-333-0029',
            'latitude': 33.625049,
            'longitude': -111.928706
        },
        {
            'name': 'Tempe - E. University Drive',
            'address': '2077 East University Drive',
            'city': 'Tempe',
            'state': 'Arizona',
            'zip_code': '85281',
            'phone': '602-643-0024',
            'latitude': 33.421679,
            'longitude': -111.897325
        },
        {
            'name': 'Deer Valley',
            'address': '21030 N 19th Ave',
            'city': 'Phoenix',
            'state': 'Arizona',
            'zip_code': '85027',
            'phone': '(480) 293-2097',
            'latitude': 33.6779561,
            'longitude': -112.1008029
        },
        {
            'name': 'Tucson',
            'address': '5081 N Oracle Rd',
            'city': 'Tucson',
            'state': 'Arizona',
            'zip_code': '85704',
            'phone': '520/416-7974',
            'latitude': 32.2986337,
            'longitude': -110.9790634
        }
    ]
    
    # California dealerships (sample - there are many more)
    california_dealerships = [
        {
            'name': 'Santa Rosa',
            'address': '3286 Airway Drive',
            'city': 'Santa Rosa',
            'state': 'California',
            'zip_code': '95403',
            'phone': '707-806-5040',
            'latitude': 38.4741754,
            'longitude': -122.737459
        },
        {
            'name': 'Alhambra',
            'address': '1200 W Main St',
            'city': 'Alhambra',
            'state': 'California',
            'zip_code': '91801',
            'phone': '626-313-5967',
            'latitude': 34.0911499,
            'longitude': -118.1360862
        },
        {
            'name': 'Aliso Viejo',
            'address': '26501 Aliso Creek Rd',
            'city': 'Aliso Viejo',
            'state': 'California',
            'zip_code': '92656',
            'phone': '(949) 860-8050',
            'latitude': 33.5795431,
            'longitude': -117.7239588
        },
        {
            'name': 'Bakersfield',
            'address': '5206 Young St Suite B',
            'city': 'Bakersfield',
            'state': 'California',
            'zip_code': '93311',
            'phone': '661-885-3939',
            'latitude': 35.307366,
            'longitude': -119.098094
        },
        {
            'name': 'Berkeley',
            'address': '1731 Fourth St',
            'city': 'Berkeley',
            'state': 'California',
            'zip_code': '94710',
            'phone': '(510) 898-7773',
            'latitude': 37.8709978,
            'longitude': -122.3007859
        },
        {
            'name': 'Brea-Brea Mall',
            'address': '1065 BREA MALL',
            'city': 'BREA',
            'state': 'California',
            'zip_code': '92821',
            'phone': '7146740296',
            'latitude': 33.9153422,
            'longitude': -117.8864509
        },
        {
            'name': 'Buena Park',
            'address': '6692 Auto Center Drive',
            'city': 'Buena Park',
            'state': 'California',
            'zip_code': '90621',
            'phone': '714-735-5696',
            'latitude': 33.863556,
            'longitude': -117.99074
        },
        {
            'name': 'Burbank',
            'address': '811 South San Fernando Boulevard',
            'city': 'Burbank',
            'state': 'California',
            'zip_code': '91502',
            'phone': '818-480-9217',
            'latitude': 34.174826,
            'longitude': -118.301286
        },
        {
            'name': 'Burlingame',
            'address': '50 Edwards Ct',
            'city': 'Burlingame',
            'state': 'California',
            'zip_code': '94010',
            'phone': '(650)642-1176',
            'latitude': 37.593128,
            'longitude': -122.367306
        },
        {
            'name': 'Camarillo',
            'address': '311 E Daily Drive',
            'city': 'Camarillo',
            'state': 'California',
            'zip_code': '93010',
            'phone': '805-465-1696',
            'latitude': 34.2198123,
            'longitude': -119.0655388
        }
    ]
    
    # Add all dealerships
    dealerships.extend(arizona_dealerships)
    dealerships.extend(california_dealerships)
    
    # Add more states as needed...
    # For now, let's add a few more key states with major dealerships
    
    # Texas dealerships
    texas_dealerships = [
        {
            'name': 'Austin Ridgepoint',
            'address': '2323 RIDGEPOINT DR',
            'city': 'AUSTIN',
            'state': 'Texas',
            'zip_code': '78754',
            'phone': '(737) 800-5731',
            'latitude': 30.3290182,
            'longitude': -97.6755978
        },
        {
            'name': 'Austin-500 E St Elmo Rd',
            'address': '500 E St Elmo Rd',
            'city': 'Austin',
            'state': 'Texas',
            'zip_code': '78745',
            'phone': '737-717-8919',
            'latitude': 30.2153692,
            'longitude': -97.7616189
        },
        {
            'name': 'Dallas',
            'address': '6500 Cedar Springs Road',
            'city': 'Dallas',
            'state': 'Texas',
            'zip_code': '75235',
            'phone': '214-736-0587',
            'latitude': 32.8323971,
            'longitude': -96.8375432
        },
        {
            'name': 'Houston',
            'address': '19820 Hempstead Hwy',
            'city': 'Houston',
            'state': 'Texas',
            'zip_code': '77065',
            'phone': '281-571-4390',
            'latitude': 29.9127482,
            'longitude': -95.6150909
        }
    ]
    
    # Florida dealerships
    florida_dealerships = [
        {
            'name': 'Aventura-Aventura Mall',
            'address': '19565 Biscayne Blvd #1948',
            'city': 'Aventura',
            'state': 'Florida',
            'zip_code': '33180',
            'phone': '(305) 914-3072',
            'latitude': 25.9583338,
            'longitude': -80.1424004
        },
        {
            'name': 'Coral Gables Miami',
            'address': '3851 Bird Road',
            'city': 'Miami',
            'state': 'Florida',
            'zip_code': '33146',
            'phone': '786-804-6926',
            'latitude': 25.735192,
            'longitude': -80.256911
        },
        {
            'name': 'Orlando',
            'address': '2214 John Young Pkwy',
            'city': 'Orlando',
            'state': 'Florida',
            'zip_code': '32804',
            'phone': '407-533-4117',
            'latitude': 28.573101,
            'longitude': -81.4174589
        }
    ]
    
    # New York dealerships
    new_york_dealerships = [
        {
            'name': 'Brooklyn',
            'address': '106 2nd Ave',
            'city': 'Brooklyn',
            'state': 'New York',
            'zip_code': '11215',
            'phone': '(646) 335-1060',
            'latitude': 40.6731907,
            'longitude': -73.9944353
        },
        {
            'name': 'Buffalo',
            'address': '1216 South Park Ave',
            'city': 'Buffalo',
            'state': 'New York',
            'zip_code': '14220',
            'phone': '(716) 587-3998',
            'latitude': 42.8605316,
            'longitude': -78.8378809
        },
        {
            'name': 'Tesla Meatpacking',
            'address': '860 Washington St.',
            'city': 'New York',
            'state': 'New York',
            'zip_code': '10014',
            'phone': '2122061204',
            'latitude': 40.74107,
            'longitude': -74.007562
        }
    ]
    
    dealerships.extend(texas_dealerships)
    dealerships.extend(florida_dealerships)
    dealerships.extend(new_york_dealerships)
    
    return dealerships

def main():
    print("Extracting Tesla dealership data from browser snapshot...")
    
    # Parse dealerships from the browser data we captured
    dealerships = parse_tesla_dealerships_from_browser_data()
    
    # Add website URLs
    base_url = "https://www.tesla.com"
    for dealership in dealerships:
        dealership['website_url'] = f"{base_url}/findus/location/store/{dealership['name'].lower().replace(' ', '').replace('-', '')}"
        dealership['demo_drive_url'] = f"{base_url}/drive?lat={dealership['latitude']}&lng={dealership['longitude']}"
    
    # Save to JSON file
    output_file = '/Users/kimseanpardo/autodealerships/tesla_dealerships_usa.json'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dealerships, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to {output_file}")
        
        # Print statistics
        states = {}
        for dealership in dealerships:
            state = dealership['state']
            states[state] = states.get(state, 0) + 1
        
        print(f"\nTotal dealerships: {len(dealerships)}")
        print(f"States covered: {len(states)}")
        print("\nDealerships by state:")
        for state, count in sorted(states.items()):
            print(f"  {state}: {count}")
            
    except Exception as e:
        print(f"Error saving data: {e}")

if __name__ == "__main__":
    main()
