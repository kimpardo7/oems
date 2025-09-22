#!/usr/bin/env python3
"""
Infiniti Simple Test - One zip code at a time
Focus on getting actual dealer data without getting stuck
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

def test_single_zip(zip_code):
    """Test with a single zip code and save results immediately"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(30000)
        
        try:
            print(f"Testing zip code: {zip_code}")
            
            # Navigate to Infiniti
            page.goto("https://www.infinitiusa.com", wait_until="domcontentloaded")
            time.sleep(3)
            
            # Click Retailer Locator
            page.locator('button[data-panel="Retailer_Locator"]').click()
            time.sleep(3)
            
            # Enter zip code
            zip_input = page.locator('input[name="predict-input"]')
            zip_input.clear()
            zip_input.fill(zip_code)
            time.sleep(2)
            
            # Click search
            page.locator('button.predict-input_search-button').click()
            time.sleep(5)
            
            # Take screenshot
            page.screenshot(path=f"infiniti_simple_{zip_code}.png")
            
            # Get all text content to see what we're working with
            page_content = page.content()
            
            # Save the page content for analysis
            with open(f"infiniti_simple_{zip_code}_content.html", "w", encoding="utf-8") as f:
                f.write(page_content)
            
            # Look for any text that might be dealer names
            dealer_names = []
            dealer_addresses = []
            
            # Try to find dealer information in the page
            all_text = page.text_content()
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and len(line) > 5:
                    # Look for lines that might be dealer names
                    if any(keyword in line.lower() for keyword in ['infiniti', 'dealer', 'retailer']) and len(line) < 100:
                        dealer_names.append(line)
                    # Look for lines that might be addresses
                    elif any(keyword in line.lower() for keyword in ['street', 'avenue', 'road', 'drive', 'boulevard']) and len(line) < 200:
                        dealer_addresses.append(line)
            
            # Create simple dealer data
            dealers = []
            for i, name in enumerate(dealer_names[:10]):  # Limit to 10
                address = dealer_addresses[i] if i < len(dealer_addresses) else ""
                dealers.append({
                    'zip_searched': zip_code,
                    'name': name,
                    'address': address,
                    'phone': '',
                    'website': ''
                })
            
            # Save results immediately
            results = {
                "brand": "Infiniti",
                "dealers": dealers,
                "last_updated": datetime.now().isoformat(),
                "total_dealers": len(dealers),
                "search_method": "zip_code_locator",
                "source_url": "https://www.infinitiusa.com",
                "zip_code_tested": zip_code
            }
            
            filename = f"Infiniti_{zip_code}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Found {len(dealers)} dealers for zip {zip_code}")
            print(f"Saved to {filename}")
            
            # Print the dealer names found
            for i, dealer in enumerate(dealers):
                print(f"{i+1}. {dealer['name']}")
            
            return dealers
            
        except Exception as e:
            print(f"Error with zip {zip_code}: {e}")
            return []
        
        finally:
            browser.close()

def main():
    """Test with different zip codes one at a time"""
    zip_codes = ["90210", "10001", "60601", "33101", "75201"]
    
    all_dealers = []
    
    for zip_code in zip_codes:
        print(f"\n{'='*50}")
        dealers = test_single_zip(zip_code)
        all_dealers.extend(dealers)
        
        # Small delay between tests
        time.sleep(2)
    
    # Save combined results
    combined_results = {
        "brand": "Infiniti",
        "dealers": all_dealers,
        "last_updated": datetime.now().isoformat(),
        "total_dealers": len(all_dealers),
        "search_method": "zip_code_locator",
        "source_url": "https://www.infinitiusa.com"
    }
    
    with open("Infiniti.json", 'w') as f:
        json.dump(combined_results, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"TOTAL: Found {len(all_dealers)} dealers across all zip codes")
    print("Saved to Infiniti.json")

if __name__ == "__main__":
    main()