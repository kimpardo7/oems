#!/usr/bin/env python3
"""
Test Honda API with a few ZIP codes
"""

import asyncio
import json
import aiohttp
from datetime import datetime

# Test with just a few ZIP codes
TEST_ZIP_CODES = ["90210", "10001", "60601"]

async def test_honda_api():
    """Test the Honda API with a few ZIP codes"""
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Referer': 'https://automobiles.honda.com/tools/dealership-locator',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        all_dealers = []
        
        for zipcode in TEST_ZIP_CODES:
            print(f"Testing ZIP: {zipcode}")
            
            url = f"https://automobiles.honda.com/platform/api/v2/dealer?productDivisionCode=A&excludeServiceCenters=true&zip={zipcode}&maxResults=50"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        dealers = data.get('Dealers', [])
                        print(f"  Found {len(dealers)} dealers for ZIP {zipcode}")
                        
                        for dealer in dealers:
                            dealer_info = {
                                'dealer_id': dealer.get('DealerNumber'),
                                'name': dealer.get('Name'),
                                'address': dealer.get('Address'),
                                'city': dealer.get('City'),
                                'state': dealer.get('State'),
                                'zip': dealer.get('ZipCode'),
                                'phone': dealer.get('Phone'),
                                'website': dealer.get('WebAddress'),
                                'latitude': dealer.get('Latitude'),
                                'longitude': dealer.get('Longitude'),
                                'distance_miles': dealer.get('DrivingDistanceMiles')
                            }
                            all_dealers.append(dealer_info)
                    else:
                        print(f"  Error: HTTP {response.status}")
                        
            except Exception as e:
                print(f"  Error fetching data for ZIP {zipcode}: {e}")
        
        print(f"\nTotal dealers found: {len(all_dealers)}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/honda_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'total_dealers': len(all_dealers),
                'dealers': all_dealers
            }, f, indent=2)
        
        print(f"Results saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(test_honda_api())
