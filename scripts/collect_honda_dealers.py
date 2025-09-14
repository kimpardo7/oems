#!/usr/bin/env python3
"""
Honda Dealer Collection Script
Uses the Honda API to collect all Honda dealerships across the US
"""

import asyncio
import json
import time
import aiohttp
from datetime import datetime
from typing import List, Dict, Set
import aiofiles

# ZIP codes covering major US regions
ZIP_CODES = [
    # Northeast
    "10001", "02101", "19102", "20001", "21201", "02108", "10002", "19103", "20002", "21202",
    "02109", "10003", "19104", "20003", "21203", "02110", "10004", "19105", "20004", "21204",
    "02111", "10005", "19106", "20005", "21205", "02112", "10006", "19107", "20006", "21206",
    
    # Southeast
    "33101", "32801", "28201", "37201", "38101", "33102", "32802", "28202", "37202", "38102",
    "33103", "32803", "28203", "37203", "38103", "33104", "32804", "28204", "37204", "38104",
    "33105", "32805", "28205", "37205", "38105", "33106", "32806", "28206", "37206", "38106",
    
    # Midwest
    "60601", "53201", "46201", "44101", "48201", "60602", "53202", "46202", "44102", "48202",
    "60603", "53203", "46203", "44103", "48203", "60604", "53204", "46204", "44104", "48204",
    "60605", "53205", "46205", "44105", "48205", "60606", "53206", "46206", "44106", "48206",
    
    # Southwest
    "75201", "77001", "73101", "85001", "89101", "75202", "77002", "73102", "85002", "89102",
    "75203", "77003", "73103", "85003", "89103", "75204", "77004", "73104", "85004", "89104",
    "75205", "77005", "73105", "85005", "89105", "75206", "77006", "73106", "85006", "89106",
    
    # West Coast
    "90210", "94101", "98101", "97201", "95801", "90211", "94102", "98102", "97202", "95802",
    "90212", "94103", "98103", "97203", "95803", "90213", "94104", "98104", "97204", "95804",
    "90214", "94105", "98105", "97205", "95805", "90215", "94106", "98106", "97206", "95806"
]

async def fetch_dealers_for_zip(session: aiohttp.ClientSession, zipcode: str) -> List[Dict]:
    """Fetch dealers for a specific ZIP code"""
    
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
    
    url = f"https://automobiles.honda.com/platform/api/v2/dealer?productDivisionCode=A&excludeServiceCenters=true&zip={zipcode}&maxResults=5000"
    
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                dealers = data.get('Dealers', [])
                print(f"  Found {len(dealers)} dealers for ZIP {zipcode}")
            return dealers
            else:
                print(f"  Error: HTTP {response.status} for ZIP {zipcode}")
                return []
        except Exception as e:
        print(f"  Error fetching data for ZIP {zipcode}: {e}")
            return []
    
async def collect_all_honda_dealers():
    """Collect all Honda dealers across the US"""
    
    print("Starting Honda dealer collection...")
    print(f"Testing {len(ZIP_CODES)} ZIP codes...")
    
    # Track unique dealers by dealer number
    unique_dealers = {}
    total_requests = 0
    
    async with aiohttp.ClientSession() as session:
        for i, zipcode in enumerate(ZIP_CODES, 1):
            print(f"Progress: {i}/{len(ZIP_CODES)} - ZIP: {zipcode}")
            
            dealers = await fetch_dealers_for_zip(session, zipcode)
            total_requests += 1
            
            for dealer in dealers:
                dealer_number = dealer.get('DealerNumber')
                if dealer_number and dealer_number not in unique_dealers:
                    unique_dealers[dealer_number] = {
                        'dealer_id': dealer.get('DealerNumber'),
                        'name': dealer.get('Name'),
                        'address': dealer.get('Address'),
                        'city': dealer.get('City'),
                        'state': dealer.get('State'),
                        'zip': dealer.get('ZipCode'),
                        'phone': dealer.get('Phone'),
                        'parts_phone': dealer.get('PartsPhone'),
                        'service_phone': dealer.get('ServicePhone'),
                        'website': dealer.get('WebAddress'),
                        'latitude': dealer.get('Latitude'),
                        'longitude': dealer.get('Longitude'),
                        'sales_hours': dealer.get('SalesHours', []),
                        'parts_hours': dealer.get('PartsHours', []),
                        'service_hours': dealer.get('ServiceHours', []),
                        'attributes': dealer.get('Attributes', []),
                        'is_service_center': dealer.get('IsServiceCenter', False),
                        'preferred': dealer.get('Preferred', False)
                    }
            
            # Add delay between requests
            if i < len(ZIP_CODES):
                await asyncio.sleep(0.5)
        
        print(f"\nCollection complete!")
    print(f"Total ZIP codes tested: {total_requests}")
    print(f"Unique dealers found: {len(unique_dealers)}")
    
    # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/honda_dealers_{timestamp}.json"
        
    result_data = {
        'collection_date': datetime.now().isoformat(),
        'total_zip_codes_tested': total_requests,
        'unique_dealers_found': len(unique_dealers),
        'dealers': list(unique_dealers.values())
    }
    
        async with aiofiles.open(filename, 'w') as f:
        await f.write(json.dumps(result_data, indent=2))
        
        print(f"Results saved to: {filename}")
    
    # Also save a simple format for consistency
    simple_filename = f"data/honda.json"
    simple_data = {
        'brand': 'Honda',
        'collection_date': datetime.now().isoformat(),
        'total_dealers': len(unique_dealers),
        'dealers': list(unique_dealers.values())
    }
    
    async with aiofiles.open(simple_filename, 'w') as f:
        await f.write(json.dumps(simple_data, indent=2))
    
    print(f"Simple format saved to: {simple_filename}")

if __name__ == "__main__":
    asyncio.run(collect_all_honda_dealers())
