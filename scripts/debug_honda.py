#!/usr/bin/env python3
"""
Debug Honda API call
"""

import asyncio
import aiohttp
import json

async def debug_honda_api():
    """Debug the Honda API call"""
    
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
    
    url = "https://automobiles.honda.com/platform/api/v2/dealer?productDivisionCode=A&excludeServiceCenters=true&zip=90210&maxResults=50"
    
    print(f"Testing URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                print(f"Response status: {response.status}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Response data: {json.dumps(data, indent=2)}")
                    
                    dealers = data.get('Dealers', [])
                    print(f"Found {len(dealers)} dealers")
                    
                    if dealers:
                        print(f"First dealer: {json.dumps(dealers[0], indent=2)}")
                else:
                    text = await response.text()
                    print(f"Error response: {text}")
                    
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_honda_api())
