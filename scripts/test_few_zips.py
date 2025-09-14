#!/usr/bin/env python3
"""
Test Honda API with just a few ZIP codes
"""

import asyncio
import aiohttp
import json

async def test_few_zips():
    """Test with just a few ZIP codes"""
    
    test_zips = ["90210", "10001", "60601"]
    
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
    
    async with aiohttp.ClientSession() as session:
        for i, zipcode in enumerate(test_zips, 1):
            print(f"Test {i}: ZIP {zipcode}")
            
            url = f"https://automobiles.honda.com/platform/api/v2/dealer?productDivisionCode=A&excludeServiceCenters=true&zip={zipcode}&maxResults=50"
            
            try:
                async with session.get(url, headers=headers) as response:
                    print(f"  Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        dealers = data.get('Dealers', [])
                        print(f"  Found {len(dealers)} dealers")
                        
                        if dealers:
                            print(f"  First dealer: {dealers[0].get('Name')}")
                    else:
                        text = await response.text()
                        print(f"  Error: {text}")
                        
            except Exception as e:
                print(f"  Exception: {e}")
            
            # Add delay
            if i < len(test_zips):
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_few_zips())
